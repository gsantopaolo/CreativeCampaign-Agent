"""
Brand Composer Service
Subscribes to image.generated and adds brand elements (logo, colors) to images.
Follows sentinel-AI production patterns for reliability and observability.
"""

import os
import logging
import asyncio
import threading
import httpx
from datetime import datetime
from dotenv import load_dotenv
from nats.aio.msg import Msg
from PIL import Image, ImageDraw
from io import BytesIO
import boto3
from botocore.client import Config
from openai import AsyncOpenAI
import base64
from pydantic import BaseModel, Field

from motor.motor_asyncio import AsyncIOMotorClient

from src.lib_py.gen_types import image_generate_pb2, brand_compose_pb2
from src.lib_py.middlewares.jetstream_publisher import JetStreamPublisher
from src.lib_py.middlewares.jetstream_event_subscriber import JetStreamEventSubscriber
from src.lib_py.middlewares.readiness_probe import ReadinessProbe

# ————— Environment & Logging —————
load_dotenv()

# Get log level from env
log_level_str = os.getenv('LOG_LEVEL', 'INFO').upper()
log_level = getattr(logging, log_level_str, logging.INFO)

# Get log format from env
log_format = os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Configure logging
logging.basicConfig(level=log_level, format=log_format)
logger = logging.getLogger(__name__)

# ————— Configuration —————
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "creative_campaign")
NATS_URL = os.getenv("NATS_URL", "nats://nats:4222")
NATS_RECONNECT_TIME_WAIT = int(os.getenv("NATS_RECONNECT_TIME_WAIT", "2"))
NATS_CONNECT_TIMEOUT = int(os.getenv("NATS_CONNECT_TIMEOUT", "10"))
NATS_MAX_RECONNECT_ATTEMPTS = int(os.getenv("NATS_MAX_RECONNECT_ATTEMPTS", "60"))

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_TEXT_MODEL = os.getenv("OPENAI_TEXT_MODEL", "gpt-4o-mini")

# MinIO/S3 Configuration
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL", "http://minio:9000")
S3_EXTERNAL_ENDPOINT_URL = os.getenv("S3_EXTERNAL_ENDPOINT_URL", "http://localhost:9000")  # For presigned URLs
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY_ID", "minioadmin")
S3_SECRET_KEY = os.getenv("S3_SECRET_ACCESS_KEY", "minioadmin")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "creative-assets")

# Brand Composer Configuration
LOGO_SIZE_PERCENT = float(os.getenv("LOGO_SIZE_PERCENT", "0.15"))  # Logo is 15% of image width
LOGO_MARGIN_PERCENT = float(os.getenv("LOGO_MARGIN_PERCENT", "0.03"))  # 3% margin from edges

# Readiness Probe Configuration
READINESS_TIME_OUT = int(os.getenv('BRAND_COMPOSER_READINESS_TIME_OUT', 500))

# NATS Stream configuration
IMAGE_GENERATE_STREAM_NAME = "image-generate-stream"
IMAGE_GENERATED_SUBJECT = "image.generated"
BRAND_COMPOSE_STREAM_NAME = "brand-compose-stream"
BRAND_COMPOSED_SUBJECT = "brand.composed"

# Global clients
mongo_client = None
db = None
publisher: JetStreamPublisher = None
subscriber: JetStreamEventSubscriber = None
readiness_probe: ReadinessProbe = None
s3_client = None
s3_external_client = None  # For generating presigned URLs with external endpoint
openai_client: AsyncOpenAI = None


# ————— Pydantic Models for Structured LLM Output —————

class LogoPlacementResponse(BaseModel):
    """Structured response from LLM for logo placement analysis."""
    position: str = Field(..., description="Logo position: bottom_right, bottom_left, top_right, or top_left")
    x_percent: float = Field(..., description="X coordinate as percentage of image width (0.0-1.0)")
    y_percent: float = Field(..., description="Y coordinate as percentage of image height (0.0-1.0)")
    scale: float = Field(..., description="Logo scale factor (0.08-0.25)")
    reasoning: str = Field(..., description="Detailed explanation of placement decision with pixel coordinates")


def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


async def analyze_logo_placement(image_data: bytes, width: int, height: int) -> dict:
    """
    Use GPT-4o-mini with vision to analyze the image and determine optimal logo placement.
    
    Returns:
        dict: {
            "position": "bottom_right|bottom_left|top_right|top_left",
            "x": int,  # X coordinate
            "y": int,  # Y coordinate  
            "scale": float,  # Logo scale factor (0.1 to 0.3)
            "reasoning": str  # Why this position was chosen
        }
    """
    try:
        # Convert image to base64
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        prompt = f"""You are an expert brand designer analyzing a product marketing image to find the BEST position for a brand logo.

IMAGE DIMENSIONS: {width}x{height} pixels

CRITICAL CONSTRAINT: Logo MUST be placed in the UPPER HALF of the image (y_percent < 0.50) because campaign text will be placed at the bottom.

YOUR TASK: Analyze the UPPER HALF of the image and find the optimal position and size for a brand logo that:
1. Does NOT cover or obscure important visual elements (products, faces, key imagery)
2. Has good contrast and visibility
3. Feels natural and professionally placed
4. Maintains brand prominence without being intrusive
5. STAYS IN TOP 50% (y_percent must be between 0.05 and 0.45)

STEP-BY-STEP ANALYSIS:

1. SCAN UPPER HALF (top 50%):
   - Identify visual elements in y: 0 to {int(height * 0.5)}px
   - Note pixel locations of: products, faces, text, decorative elements, focal points
   - Find empty/plain areas suitable for logo placement
   - Consider: top-left, top-center, top-right, middle-left, middle-right
   - Example: "Product centered at 400-600px, clear space in top-right corner 700-950px"

2. IDENTIFY BEST LOGO POSITION IN UPPER HALF:
   - Look for the largest continuous empty space with good visibility
   - Prefer corners or edges with plain/solid backgrounds
   - Best positions: top-right, top-left, top-center (all in upper 50%)
   - Avoid covering faces, products, or key visual elements
   - Estimate boundaries in pixels (x1, y1, x2, y2)
   - Example: "Best area: top-right corner x=700-950px, y=50-200px - plain background, good contrast"

3. CALCULATE LOGO SIZE:
   - Logo should be 8-18% of image width
   - Calculate: logo_size_px = {width} * scale (where scale is 0.08-0.18)
   - Smaller logos (0.08-0.11) for busy images or when placed over textured areas
   - Medium logos (0.11-0.14) for balanced placement
   - Larger logos (0.14-0.18) for plain backgrounds with lots of empty space
   - Example: "Plain background in corner → scale=0.12 → logo 123px for 1024px image"

4. CALCULATE EXACT POSITION (CENTER POINT):
   - Find CENTER of the chosen empty area IN THE UPPER HALF
   - Logo will be centered at: (x_percent, y_percent)
   - Ensure 30-60px margin from edges
   - x_percent: 0.0 (left edge) to 1.0 (right edge)
   - y_percent: 0.05 (near top) to 0.45 (middle) - MUST BE < 0.50
   - Example: "Top-right corner center at x_percent=0.85, y_percent=0.12"

5. VERIFY YOUR CHOICE:
   - Logo is in UPPER HALF? (y_percent < 0.50) ✓
   - Logo does NOT cover important visual elements? ✓
   - Logo has good contrast with background? ✓
   - Logo size is readable but not overwhelming? ✓
   - Position feels natural and professional? ✓
   - Adequate margin from edges (30-60px)? ✓

CRITICAL: Logo MUST be in top 50% of image. y_percent MUST be less than 0.50.

Respond with a JSON object in this EXACT format:
{{
  "position": "top_right",
  "x_percent": 0.85,
  "y_percent": 0.12,
  "scale": 0.12,
  "reasoning": "Detailed explanation: why this position was chosen, what visual elements were avoided, pixel coordinates, and confirmation that y < 50%"
}}

Return ONLY the JSON object."""        
        response = await openai_client.chat.completions.create(
            model=OPENAI_TEXT_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=300
        )
        
        # Parse and validate with Pydantic
        import json
        json_response = json.loads(response.choices[0].message.content)
        result = LogoPlacementResponse(**json_response).model_dump()
        
        # Convert percentages to pixel coordinates
        result["x"] = int(result["x_percent"] * width)
        result["y"] = int(result["y_percent"] * height)
        
        logger.info(f"  🤖 LLM logo placement: {result['position']} at ({result['x']}, {result['y']}), scale={result['scale']}")
        logger.info(f"  💡 Reasoning: {result['reasoning']}")
        
        return result
        
    except Exception as e:
        logger.warning(f"  ⚠️  LLM logo placement failed: {e}, using default top-center")
        # Fallback to top-center
        return {
            "position": "top_center",
            "x": int(width * 0.50),
            "y": int(height * 0.12),
            "scale": 0.15,
            "reasoning": "Default top-center placement (LLM analysis failed)"
        }


async def compose_brand_elements(image_request: image_generate_pb2.ImageGenerated):
    """
    Add brand elements (logo, colors) to the generated image.
    
    Args:
        image_request: ImageGenerated protobuf message
        
    Returns:
        dict: Branded image details
    """
    campaign_id = image_request.campaign_id
    locale = image_request.locale
    
    # Extract aspect ratio from S3 URI: s3://bucket/campaigns/{campaign_id}/{locale}/{aspect_ratio}/...
    aspect_ratio = "unknown"
    try:
        s3_uri = image_request.s3_uri
        # S3 URI format: s3://bucket/campaigns/id/locale/ASPECT/file.png
        # Split:         ['s3:', '', 'bucket', 'campaigns', 'id', 'locale', 'ASPECT', 'file.png']
        # Index:         [  0     1     2         3          4      5         6         7      ]
        parts = s3_uri.split('/')
        if len(parts) >= 7:
            aspect_ratio = parts[6]  # Extract aspect ratio at index 6
            logger.info(f"  📐 Extracted aspect ratio '{aspect_ratio}' from S3 URI")
    except Exception as e:
        logger.warning(f"  ⚠️  Could not extract aspect ratio from S3 URI: {e}")
    
    logger.info(f"🏷️ Adding brand elements for {campaign_id}:{locale}:{aspect_ratio}")
    
    try:
        # Get the campaign to fetch brand configuration
        campaign = await db.campaigns.find_one({"_id": campaign_id})
        if not campaign:
            logger.error(f"❌ No campaign found: {campaign_id}")
            return None
        
        brand = campaign.get("brand", {})
        primary_color = brand.get("primary_color", "#FF3355")
        
        logger.info(f"  🎨 Brand color: {primary_color}")
        
        # Download the original image
        image_url = image_request.image_url
        logger.info(f"  📥 Downloading image from: {image_url[:80]}...")
        
        async with httpx.AsyncClient() as client:
            img_response = await client.get(image_url)
            img_response.raise_for_status()
            image_data = img_response.content
        
        logger.info(f"  ✅ Image downloaded ({len(image_data)} bytes)")
        
        # Open image with PIL
        img = Image.open(BytesIO(image_data)).convert('RGBA')
        width, height = img.size
        logger.info(f"  📐 Image size: {width}x{height}")
        
        draw = ImageDraw.Draw(img)
        rgb_color = hex_to_rgb(primary_color)
        
        # Use LLM to analyze optimal logo placement
        logger.info(f"  🤖 Analyzing image for optimal logo placement...")
        logo_placement = await analyze_logo_placement(image_data, width, height)
        
        # Add logo overlay using LLM-determined placement
        logo_s3_uri = brand.get('logo_s3_uri')
        
        if not logo_s3_uri:
            logger.warning(f"  ⚠️  No logo_s3_uri provided in campaign brand configuration")
        else:
            try:
                # Download logo from S3
                if not logo_s3_uri.startswith('s3://'):
                    logger.error(f"  ❌ Invalid S3 URI format: {logo_s3_uri}")
                else:
                    # Parse S3 URI: s3://bucket/key
                    s3_parts = logo_s3_uri.replace('s3://', '').split('/', 1)
                    if len(s3_parts) != 2:
                        logger.error(f"  ❌ Invalid S3 URI format: {logo_s3_uri}")
                    else:
                        bucket, key = s3_parts
                        
                        logger.info(f"  📥 Downloading logo from S3: {logo_s3_uri}")
                        logo_obj = s3_client.get_object(Bucket=bucket, Key=key)
                        logo_data = logo_obj['Body'].read()
                        
                        # Open logo image
                        logo_img = Image.open(BytesIO(logo_data))
                        logger.info(f"  📊 Original logo size: {logo_img.size}, mode: {logo_img.mode}")
                        
                        # Convert to RGBA
                        if logo_img.mode != 'RGBA':
                            logo_img = logo_img.convert('RGBA')
                        
                        # Calculate target logo size using LLM recommendation directly
                        target_logo_width = int(width * logo_placement["scale"])
                        
                        # Resize logo maintaining aspect ratio
                        logo_aspect = logo_img.width / logo_img.height
                        target_logo_height = int(target_logo_width / logo_aspect)
                        logo_img = logo_img.resize((target_logo_width, target_logo_height), Image.Resampling.LANCZOS)
                        
                        logger.info(f"  📏 Logo resized to: {target_logo_width}x{target_logo_height} (LLM scale: {logo_placement['scale']} = {logo_placement['scale']*100}% of image width)")
                        
                        # Use LLM-provided coordinates directly
                        # LLM provides the bottom-right corner of the logo, so adjust for logo size
                        logo_x = logo_placement["x"] - target_logo_width
                        logo_y = logo_placement["y"] - target_logo_height
                        
                        # Ensure logo stays within bounds
                        logo_x = max(20, min(logo_x, width - target_logo_width - 20))
                        logo_y = max(20, min(logo_y, height - target_logo_height - 20))
                        
                        logger.info(f"  📍 Logo position: ({logo_x}, {logo_y}) from LLM coords ({logo_placement['x']}, {logo_placement['y']})")
                        
                        # Composite logo onto image with transparency preserved
                        # Using the logo's alpha channel as the mask preserves transparency
                        img.paste(logo_img, (logo_x, logo_y), logo_img)
                        
                        logger.info(f"  ✅ Logo composited at ({logo_x}, {logo_y}) - {logo_placement['position']} with transparency")
                        
            except Exception as e:
                logger.error(f"  ❌ Failed to load and apply logo from S3: {e}", exc_info=True)
        
        # Convert back to bytes
        output = BytesIO()
        img.save(output, format='PNG')
        branded_image_data = output.getvalue()
        
        logger.info(f"  ✅ Branded image created ({len(branded_image_data)} bytes)")
        
        # Upload to S3/MinIO with aspect ratio in path
        s3_key = f"campaigns/{campaign_id}/{locale}/{aspect_ratio}/branded_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.png"
        branded_s3_uri = f"s3://{S3_BUCKET_NAME}/{s3_key}"
        
        try:
            logger.info(f"  📤 Uploading to S3: {branded_s3_uri}")
            s3_client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=s3_key,
                Body=branded_image_data,
                ContentType='image/png'
            )
            logger.info(f"  ✅ Uploaded to S3: {branded_s3_uri}")
            
            # Generate presigned URL for viewing (valid for 7 days) using external endpoint
            branded_image_url = s3_external_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': S3_BUCKET_NAME, 'Key': s3_key},
                ExpiresIn=604800  # 7 days
            )
            logger.info(f"  🔗 Generated presigned URL (7 days): {branded_image_url[:80]}...")
        except Exception as e:
            logger.error(f"  ❌ Failed to upload to S3: {e}")
            # Fallback to original image URL
            branded_image_url = image_url
        
        # Save branded image metadata to MongoDB
        branded_doc = {
            "campaign_id": campaign_id,
            "locale": locale,
            "aspect_ratio": aspect_ratio,
            "original_image_url": image_url,
            "original_s3_uri": image_request.s3_uri,
            "branded_image_url": branded_image_url,
            "branded_s3_uri": branded_s3_uri,
            "brand_color": primary_color,
            "logo_position": logo_placement["position"],
            "logo_placement_reasoning": logo_placement["reasoning"],
            "logo_scale": logo_placement["scale"],
            "status": "composed",
            "composed_at": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.branded_images.insert_one(branded_doc)
        logger.info(f"  💾 Saved branded image metadata to MongoDB: {campaign_id}:{locale}:{aspect_ratio}")
        
        return {
            "aspect_ratio": aspect_ratio,
            "branded_image_url": branded_image_url,
            "branded_s3_uri": branded_s3_uri,
            "original_image_url": image_url,
            "original_s3_uri": image_request.s3_uri
        }
        
    except Exception as e:
        logger.error(f"❌ Error composing brand elements: {e}", exc_info=True)
        raise


async def handle_image_generated(msg: Msg):
    """
    Handle incoming image.generated messages.
    """
    readiness_probe.update_last_seen()
    
    try:
        # Parse the message
        image_request = image_generate_pb2.ImageGenerated()
        image_request.ParseFromString(msg.data)
        
        logger.info(f"✉️ Received image.generated: {image_request.campaign_id}:{image_request.locale}")
        
        # Compose brand elements
        result = await compose_brand_elements(image_request)
        
        if result:
            # Publish to next stage
            brand_composed = brand_compose_pb2.BrandComposeDone(
                campaign_id=image_request.campaign_id,
                locale=image_request.locale,
                s3_uri_branded=result["branded_s3_uri"],
                correlation_id="",
                timestamp=datetime.utcnow().isoformat() + "Z"
            )
            
            await publisher.publish(brand_composed)
            aspect_ratio = result.get("aspect_ratio", "unknown")
            logger.info(f"📤 Published brand.composed for {image_request.campaign_id}:{image_request.locale}:{aspect_ratio}")
        
        # Acknowledge the message
        await msg.ack()
        logger.info(f"✅ Acknowledged image.generated: {image_request.campaign_id}:{image_request.locale}")
        
    except Exception as e:
        logger.error(f"❌ Error processing image.generated: {e}", exc_info=True)
        # Negative acknowledge to retry
        await msg.nak()
        logger.warning(f"⚠️ NAKed message for retry (will be redelivered)")


# ————— Service Lifecycle —————

async def main():
    """Main service entry point."""
    global mongo_client, db, publisher, subscriber, readiness_probe, s3_client, s3_external_client, openai_client
    
    logger.info("🛠️ Brand Composer service starting...")
    
    # Initialize readiness probe
    readiness_probe = ReadinessProbe(readiness_time_out=READINESS_TIME_OUT)
    threading.Thread(target=readiness_probe.start_server, daemon=True).start()
    logger.info("✅ Readiness probe server started.")
    
    # Initialize OpenAI client
    openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    logger.info(f"✅ OpenAI client initialized with model: {OPENAI_TEXT_MODEL}")
    
    # Initialize S3/MinIO client (internal endpoint for uploads)
    s3_client = boto3.client(
        's3',
        endpoint_url=S3_ENDPOINT_URL,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY,
        config=Config(signature_version='s3v4'),
        region_name='us-east-1'
    )
    logger.info(f"✅ S3 client initialized: {S3_ENDPOINT_URL}")
    
    # Initialize S3/MinIO client with external endpoint (for presigned URLs)
    s3_external_client = boto3.client(
        's3',
        endpoint_url=S3_EXTERNAL_ENDPOINT_URL,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY,
        config=Config(signature_version='s3v4'),
        region_name='us-east-1'
    )
    logger.info(f"✅ S3 external client initialized: {S3_EXTERNAL_ENDPOINT_URL}")
    
    # Ensure bucket exists
    try:
        s3_client.head_bucket(Bucket=S3_BUCKET_NAME)
        logger.info(f"✅ S3 bucket exists: {S3_BUCKET_NAME}")
    except:
        try:
            s3_client.create_bucket(Bucket=S3_BUCKET_NAME)
            logger.info(f"✅ S3 bucket created: {S3_BUCKET_NAME}")
        except Exception as e:
            logger.warning(f"⚠️  Could not create bucket (may already exist): {e}")
    
    # Initialize MongoDB
    mongo_client = AsyncIOMotorClient(MONGODB_URL)
    db = mongo_client[MONGODB_DB_NAME]
    logger.info(f"✅ MongoDB connected: {MONGODB_DB_NAME}")
    
    # Initialize NATS publisher
    publisher = JetStreamPublisher(
        subject=BRAND_COMPOSED_SUBJECT,
        stream_name=BRAND_COMPOSE_STREAM_NAME,
        nats_url=NATS_URL,
        nats_reconnect_time_wait=NATS_RECONNECT_TIME_WAIT,
        nats_connect_timeout=NATS_CONNECT_TIMEOUT,
        nats_max_reconnect_attempts=NATS_MAX_RECONNECT_ATTEMPTS,
        message_type="BrandComposeDone"
    )
    await publisher.connect()
    logger.info("✅ Brand composition publisher connected to NATS.")
    
    # Initialize NATS subscriber
    subscriber = JetStreamEventSubscriber(
        nats_url=NATS_URL,
        stream_name=IMAGE_GENERATE_STREAM_NAME,
        subject=IMAGE_GENERATED_SUBJECT,
        connect_timeout=NATS_CONNECT_TIMEOUT,
        reconnect_time_wait=NATS_RECONNECT_TIME_WAIT,
        max_reconnect_attempts=NATS_MAX_RECONNECT_ATTEMPTS,
        ack_wait=180,  # 3 minutes to process (includes image download and processing)
        max_deliver=3,  # Retry up to 3 times
        proto_message_type=image_generate_pb2.ImageGenerated
    )
    
    subscriber.set_event_handler(handle_image_generated)
    
    try:
        await subscriber.connect_and_subscribe()
        logger.info(f"✅ Subscribed to {IMAGE_GENERATED_SUBJECT}")
    except Exception as e:
        logger.error(f"❌ Failed to connect or subscribe to NATS: {e}")
        return
    
    # Keep-alive loop
    try:
        while True:
            readiness_probe.update_last_seen()
            await asyncio.sleep(10)
    except asyncio.CancelledError:
        logger.info("Shutdown signal received...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
    finally:
        # Cleanup
        if subscriber:
            await subscriber.disconnect()
        if publisher:
            await publisher.disconnect()
        if mongo_client:
            mongo_client.close()
        logger.info("✅ Brand Composer service stopped.")


if __name__ == "__main__":
    asyncio.run(main())
