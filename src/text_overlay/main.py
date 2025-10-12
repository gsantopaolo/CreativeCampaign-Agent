"""
Text Overlay Service

Subscribes to: brand.composed

Adds campaign message text to branded images using AI-powered placement.
"""

import os
import sys
import asyncio
import base64
import json
import logging
from datetime import datetime, timezone
from io import BytesIO
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import boto3
from botocore.client import Config
from openai import AsyncOpenAI
from PIL import Image, ImageDraw, ImageFont

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.lib_py.gen_types import brand_compose_pb2, text_overlay_pb2
from src.lib_py.middlewares.jetstream_publisher import JetStreamPublisher
from src.lib_py.middlewares.jetstream_event_subscriber import JetStreamEventSubscriber
from src.lib_py.middlewares.readiness_probe import ReadinessProbe

# ————— Logging Setup —————
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

NATS_URL = os.getenv("NATS_URL", "nats://nats:4222")
NATS_RECONNECT_TIME_WAIT = int(os.getenv("NATS_RECONNECT_TIME_WAIT", "2"))
NATS_CONNECT_TIMEOUT = int(os.getenv("NATS_CONNECT_TIMEOUT", "10"))
NATS_MAX_RECONNECT_ATTEMPTS = int(os.getenv("NATS_MAX_RECONNECT_ATTEMPTS", "60"))

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://mongodb:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "creative_campaign")

S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL", "http://minio:9000")
S3_EXTERNAL_ENDPOINT_URL = os.getenv("S3_EXTERNAL_ENDPOINT_URL", "http://localhost:9000")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY_ID", "minioadmin")
S3_SECRET_KEY = os.getenv("S3_SECRET_ACCESS_KEY", "minioadmin")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "creative-assets")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_TEXT_MODEL = os.getenv("OPENAI_TEXT_MODEL", "gpt-4o-mini")

# Initialize clients
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# S3 client for internal operations (upload/download)
s3_client = boto3.client(
    's3',
    endpoint_url=S3_ENDPOINT_URL,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    config=Config(signature_version='s3v4'),
    region_name='us-east-1'
)

# S3 client for generating external presigned URLs
s3_external_client = boto3.client(
    's3',
    endpoint_url=S3_EXTERNAL_ENDPOINT_URL,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    config=Config(signature_version='s3v4'),
    region_name='us-east-1'
)

# MongoDB client (for storing metadata)
from motor.motor_asyncio import AsyncIOMotorClient
mongo_client = AsyncIOMotorClient(MONGODB_URL)
db = mongo_client[MONGODB_DB_NAME]

# Global readiness probe
readiness_probe = None


# ————— Pydantic Models for Structured LLM Output —————

class TextPlacementResponse(BaseModel):
    """Structured response from LLM for text placement analysis."""
    box_x: int = Field(..., description="Top-left X coordinate of text box in pixels")
    box_y: int = Field(..., description="Top-left Y coordinate of text box in pixels")
    box_width: int = Field(..., description="Width of text box in pixels")
    box_height: int = Field(..., description="Height of text box in pixels")
    font_size: int = Field(..., description="Font size in points (25-80)")
    text_color: str = Field(..., description="Hex color code for text (e.g., #FFFFFF)")
    use_brand_color: bool = Field(..., description="Whether brand color was used")
    background_opacity: float = Field(..., description="Background box opacity (0.0-1.0)")
    alignment: str = Field(..., description="Text alignment: left, center, or right")
    reasoning: str = Field(..., description="Brief explanation of placement decision")


def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def calculate_bottom_middle_placement(width: int, height: int, text: str, brand_color: str) -> dict:
    """
    Calculate optimal text placement in bottom middle using code-based logic.
    
    Returns:
        dict: {
            "box_x": int,  # Top-left X coordinate
            "box_y": int,  # Top-left Y coordinate
            "box_width": int,  # Box width in pixels
            "box_height": int,  # Box height in pixels
            "font_size": int,  # Font size in points
            "text_color": str,  # Hex color for text
            "use_brand_color": bool,  # Whether to use brand color
            "background_opacity": float,  # 0.0-1.0 for text box background
            "alignment": str,  # "left", "center", "right"
            "reasoning": str
        }
    """
    # Calculate font size based on image dimensions and text length
    # Base font size on image width, adjusted for text length
    base_font_size = int(width * 0.05)  # 5% of image width
    
    # Adjust for text length (longer text = smaller font)
    text_length = len(text)
    if text_length > 60:
        font_size = int(base_font_size * 0.7)
    elif text_length > 40:
        font_size = int(base_font_size * 0.85)
    else:
        font_size = base_font_size
    
    # Ensure font size is within reasonable bounds
    font_size = max(25, min(80, font_size))
    
    # Calculate box dimensions
    # Width: 80% of image width with margins
    box_width = int(width * 0.8)
    
    # Height: Estimate based on text length and font size
    # Assume ~40 chars per line at this font size
    chars_per_line = int(box_width / (font_size * 0.6))
    estimated_lines = max(1, (text_length // chars_per_line) + 1)
    line_height = int(font_size * 1.4)
    box_height = (estimated_lines * line_height) + 40  # 40px padding
    
    # Position in bottom middle
    margin_bottom = int(height * 0.05)  # 5% margin from bottom
    box_x = (width - box_width) // 2  # Center horizontally
    box_y = height - box_height - margin_bottom
    
    # Ensure box doesn't go off screen
    box_y = max(0, box_y)
    
    return {
        "box_x": box_x,
        "box_y": box_y,
        "box_width": box_width,
        "box_height": box_height,
        "font_size": font_size,
        "text_color": "#FFFFFF",  # White text for readability
        "use_brand_color": False,
        "background_opacity": 0.7,  # Semi-transparent dark background
        "alignment": "center",
        "reasoning": f"Bottom middle placement: {box_width}x{box_height}px box at ({box_x},{box_y}), font size {font_size}pt for {text_length} chars"
    }


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list:
    """Wrap text to fit within max_width."""
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = font.getbbox(test_line)
        width = bbox[2] - bbox[0]
        
        if width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines


async def overlay_text_on_image(image_request: brand_compose_pb2.BrandComposeDone):
    """
    Add campaign message text to the branded image.
    
    Args:
        image_request: BrandComposeDone protobuf message
        
    Returns:
        dict: Text overlaid image details
    """
    campaign_id = image_request.campaign_id
    locale = image_request.locale
    
    logger.info(f"✉️ Received brand.composed: {campaign_id}:{locale}")
    logger.info(f"📝 Adding text overlay for {campaign_id}:{locale}")
    
    # Get campaign data from MongoDB
    campaign = await db.campaigns.find_one({"_id": campaign_id})
    if not campaign:
        logger.error(f"  ❌ Campaign not found: {campaign_id}")
        return
    
    # Get the LLM-generated creative content for this locale
    creative = await db.creatives.find_one({"campaign_id": campaign_id, "locale": locale})
    
    # Extract headline from creative content
    campaign_message = None
    if creative and creative.get('content'):
        content = creative.get('content', '')
        lines = content.split('\n')
        
        # Try multiple headline patterns (order matters - most specific first)
        headline_patterns = [
            '### 1. Catchy Headline',  # No colon
            '### 1. Catchy Headline:',
            '### Catchy Headline',
            '### Catchy Headline:',
            '### Headline',
            '### Headline:',
            '### Title',
            '### Title:',
            '**1. Catchy Headline:**',
            '**Catchy Headline:**',
            '**Headline:**'
        ]
        
        for pattern in headline_patterns:
            if pattern in content:
                logger.info(f"  🔍 Found pattern: {pattern}")
                for i, line in enumerate(lines):
                    if pattern in line:
                        # Check if headline is on same line
                        if len(line) > len(pattern):
                            headline = line.replace(pattern, '').strip().strip('"').strip('*').strip('«').strip('»')
                            if headline and len(headline) > 5:
                                campaign_message = headline
                                logger.info(f"  ✅ Extracted headline (same line): {campaign_message}")
                                break
                        # Check next line
                        elif i + 1 < len(lines):
                            headline = lines[i + 1].strip().strip('"').strip('*').strip('«').strip('»')
                            if headline and len(headline) > 5:
                                campaign_message = headline
                                logger.info(f"  ✅ Extracted headline (next line): {campaign_message}")
                                break
                if campaign_message:
                    break
    
    # If no headline found, raise an error
    if not campaign_message:
        error_msg = f"Could not extract headline from creative content for {campaign_id}:{locale}"
        logger.error(f"  ❌ {error_msg}")
        raise ValueError(error_msg)
    
    brand_color = campaign.get('brand', {}).get('primary_color', '#FF3355')
    
    logger.info(f"  📝 Message: {campaign_message}")
    logger.info(f"  🎨 Brand color: {brand_color}")
    
    # Download branded image from S3
    branded_s3_uri = image_request.s3_uri_branded
    logger.info(f"  📥 Downloading branded image from: {branded_s3_uri}")
    
    # Parse S3 URI
    s3_parts = branded_s3_uri.replace('s3://', '').split('/', 1)
    bucket, key = s3_parts
    
    # Download image from S3
    branded_obj = s3_client.get_object(Bucket=bucket, Key=key)
    image_data = branded_obj['Body'].read()
    
    logger.info(f"  ✅ Branded image downloaded ({len(image_data)} bytes)")
    
    # Open image with PIL
    img = Image.open(BytesIO(image_data)).convert('RGBA')
    width, height = img.size
    logger.info(f"  📐 Image size: {width}x{height}")
    
    # Calculate text placement in bottom middle (code-based, no LLM)
    logger.info(f"  📐 Calculating text placement for bottom middle...")
    text_placement = calculate_bottom_middle_placement(width, height, campaign_message, brand_color)
    
    # Create drawing context
    draw = ImageDraw.Draw(img)
    
    # Load font (try to use a nice font, fallback to default)
    try:
        # Try to load a bold font for better readability
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", text_placement['font_size'])
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", text_placement['font_size'])
        except:
            logger.warning("  ⚠️  Could not load custom font, using default")
            font = ImageFont.load_default()
    
    # Wrap text to fit box width (with padding)
    text_padding = 20
    max_text_width = text_placement['box_width'] - (text_padding * 2)
    lines = wrap_text(campaign_message, font, max_text_width)
    
    logger.info(f"  📄 Text wrapped into {len(lines)} lines")
    
    # Calculate actual text dimensions
    line_height = text_placement['font_size'] + 10
    total_text_height = len(lines) * line_height
    
    # Adjust box height if needed
    required_box_height = total_text_height + (text_padding * 2)
    if required_box_height > text_placement['box_height']:
        text_placement['box_height'] = required_box_height
        logger.info(f"  📏 Adjusted box height to {required_box_height}px for text")
    
    # Draw semi-transparent background box if opacity > 0
    if text_placement['background_opacity'] > 0:
        # Determine box color (opposite of text color for contrast)
        if text_placement['text_color'].upper() in ['#FFFFFF', '#FFF']:
            box_color = (0, 0, 0, int(255 * text_placement['background_opacity']))
        else:
            box_color = (255, 255, 255, int(255 * text_placement['background_opacity']))
        
        # Create overlay for transparency
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        overlay_draw.rectangle(
            [
                text_placement['box_x'],
                text_placement['box_y'],
                text_placement['box_x'] + text_placement['box_width'],
                text_placement['box_y'] + text_placement['box_height']
            ],
            fill=box_color
        )
        
        img = Image.alpha_composite(img, overlay)
        draw = ImageDraw.Draw(img)
        
        logger.info(f"  ✅ Added background box with {text_placement['background_opacity']} opacity")
    
    # Draw text lines
    text_color = text_placement['text_color']
    if text_placement['use_brand_color']:
        text_color = brand_color
    
    text_rgb = hex_to_rgb(text_color)
    
    # Calculate starting Y position to center text vertically in box
    start_y = text_placement['box_y'] + (text_placement['box_height'] - total_text_height) // 2
    
    for i, line in enumerate(lines):
        # Get text bounding box for this line
        bbox = font.getbbox(line)
        text_width = bbox[2] - bbox[0]
        
        # Calculate X position based on alignment
        if text_placement['alignment'] == 'center':
            text_x = text_placement['box_x'] + (text_placement['box_width'] - text_width) // 2
        elif text_placement['alignment'] == 'right':
            text_x = text_placement['box_x'] + text_placement['box_width'] - text_width - text_padding
        else:  # left
            text_x = text_placement['box_x'] + text_padding
        
        text_y = start_y + (i * line_height)
        
        # Draw text with outline for better readability
        outline_color = (0, 0, 0) if text_color.upper() in ['#FFFFFF', '#FFF'] else (255, 255, 255)
        
        # Draw outline
        for adj_x in [-2, -1, 0, 1, 2]:
            for adj_y in [-2, -1, 0, 1, 2]:
                if adj_x != 0 or adj_y != 0:
                    draw.text((text_x + adj_x, text_y + adj_y), line, font=font, fill=outline_color)
        
        # Draw main text
        draw.text((text_x, text_y), line, font=font, fill=text_rgb)
    
    logger.info(f"  ✅ Text overlay applied: {len(lines)} lines, {text_placement['font_size']}pt, {text_color}")
    
    # Convert back to bytes
    output = BytesIO()
    img.save(output, format='PNG')
    final_image_data = output.getvalue()
    
    logger.info(f"  ✅ Final image created ({len(final_image_data)} bytes)")
    
    # Upload to S3
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    s3_key = f"campaigns/{campaign_id}/{locale}/final_{timestamp}.png"
    s3_uri = f"s3://{S3_BUCKET_NAME}/{s3_key}"
    
    logger.info(f"  📤 Uploading to S3: {s3_uri}")
    
    s3_client.put_object(
        Bucket=S3_BUCKET_NAME,
        Key=s3_key,
        Body=final_image_data,
        ContentType='image/png'
    )
    
    logger.info(f"  ✅ Uploaded to S3: {s3_uri}")
    
    # Generate presigned URL (7 days) using external client for browser access
    presigned_url = s3_external_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': S3_BUCKET_NAME, 'Key': s3_key},
        ExpiresIn=604800
    )
    
    logger.info(f"  🔗 Generated presigned URL (7 days): {presigned_url[:80]}...")
    
    # Save metadata to MongoDB
    # First ensure outputs object exists
    await db.campaigns.update_one(
        {"_id": campaign_id, "outputs": None},
        {"$set": {"outputs": {}}}
    )
    
    # Now update the locale-specific data
    await db.campaigns.update_one(
        {"_id": campaign_id},
        {
            "$set": {
                f"outputs.{locale}.final_image_s3_uri": s3_uri,
                f"outputs.{locale}.final_image_url": presigned_url,
                f"outputs.{locale}.text_overlay_timestamp": datetime.now(timezone.utc),
                f"outputs.{locale}.text_placement": text_placement
            }
        }
    )
    
    logger.info(f"  💾 Saved final image metadata to MongoDB: {campaign_id}:{locale}")
    
    # Check if all locales are complete and update campaign status
    campaign = await db.campaigns.find_one({"_id": campaign_id})
    if campaign:
        target_locales = campaign.get('target_locales', [])
        outputs = campaign.get('outputs', {})
        
        # Check if all locales have final images
        all_complete = all(
            outputs.get(loc, {}).get('final_image_url') is not None 
            for loc in target_locales
        )
        
        if all_complete:
            await db.campaigns.update_one(
                {"_id": campaign_id},
                {
                    "$set": {
                        "status": "completed",
                        "completed_at": datetime.now(timezone.utc)
                    }
                }
            )
            logger.info(f"  🎉 Campaign {campaign_id} marked as COMPLETED - all locales finished!")
    
    return {
        "campaign_id": campaign_id,
        "locale": locale,
        "final_image_s3_uri": s3_uri,
        "final_image_url": presigned_url,
        "text_placement": text_placement
    }


async def main():
    """Main service entry point."""
    global readiness_probe
    
    logger.info("🚀 Text Overlay Service starting up...")
    logger.info("")
    
    # Start readiness probe
    import threading
    readiness_probe = ReadinessProbe(readiness_time_out=30)
    threading.Thread(target=readiness_probe.start_server, daemon=True).start()
    logger.info("  ✅ Readiness probe started on :8080/healthz")
    logger.info("")
    
    # Create publisher for text.overlaid events
    text_overlaid_publisher = JetStreamPublisher(
        subject="text.overlaid",
        stream_name="CREATIVE_PIPELINE",
        nats_url=NATS_URL,
        nats_reconnect_time_wait=NATS_RECONNECT_TIME_WAIT,
        nats_connect_timeout=NATS_CONNECT_TIMEOUT,
        nats_max_reconnect_attempts=NATS_MAX_RECONNECT_ATTEMPTS,
        message_type="TextOverlaid"
    )
    await text_overlaid_publisher.connect()
    logger.info("  ✅ Publisher initialized: text.overlaid")
    
    # Define message handler
    async def handle_brand_composed(msg):
        """Handle brand.composed events."""
        readiness_probe.update_last_seen()
        try:
            # Parse protobuf
            brand_composed = brand_compose_pb2.BrandComposeDone()
            brand_composed.ParseFromString(msg.data)
            
            # Overlay text
            result = await overlay_text_on_image(brand_composed)
            
            if result:
                # Publish text.overlaid event
                text_overlaid = text_overlay_pb2.TextOverlaid(
                    campaign_id=result['campaign_id'],
                    locale=result['locale'],
                    final_image_s3_uri=result['final_image_s3_uri'],
                    final_image_url=result['final_image_url']
                )
                
                await text_overlaid_publisher.publish(text_overlaid)
                logger.info(f"📤 Published text.overlaid for {result['campaign_id']}:{result['locale']}")
            
        except Exception as e:
            logger.error(f"❌ Error processing brand.composed: {e}", exc_info=True)
    
    # Subscribe to brand.composed events
    subscriber = JetStreamEventSubscriber(
        nats_url=NATS_URL,
        stream_name="brand-compose-stream",
        subject="brand.composed",
        connect_timeout=NATS_CONNECT_TIMEOUT,
        reconnect_time_wait=NATS_RECONNECT_TIME_WAIT,
        max_reconnect_attempts=NATS_MAX_RECONNECT_ATTEMPTS,
        ack_wait=180,  # 3 minutes to process
        max_deliver=3,  # Retry up to 3 times
        proto_message_type=brand_compose_pb2.BrandComposeDone
    )
    
    subscriber.set_event_handler(handle_brand_composed)
    
    try:
        await subscriber.connect_and_subscribe()
        logger.info("  ✅ Subscribed to: brand.composed")
    except Exception as e:
        logger.error(f"  ❌ Failed to connect or subscribe to NATS: {e}")
        return
    
    logger.info("")
    logger.info("🎉 Text Overlay Service startup complete - Ready to process!")
    logger.info("")
    
    # Keep-alive loop
    try:
        while True:
            readiness_probe.update_last_seen()
            await asyncio.sleep(10)
    except KeyboardInterrupt:
        logger.info("👋 Shutting down Text Overlay Service...")
    except Exception as e:
        logger.error(f"❌ Error in main loop: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
