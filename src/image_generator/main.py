"""
Image Generator Service
Subscribes to creative.generate.request and generates images using OpenAI DALL-E.
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

from motor.motor_asyncio import AsyncIOMotorClient
from openai import AsyncOpenAI

from src.lib_py.gen_types import creative_generate_pb2, image_generate_pb2
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
OPENAI_IMAGE_MODEL = os.getenv("OPENAI_IMAGE_MODEL", "dall-e-3")
OPENAI_IMAGE_QUALITY = os.getenv("OPENAI_IMAGE_QUALITY", "standard")

# DALL-E 3 supported sizes
# Note: DALL-E 3 only supports 1024x1024, 1792x1024, and 1024x1792
# 4:5 ratio (Instagram portrait) uses 1024x1792 (9:16) as closest approximation
DALLE3_SIZES = {
    "1x1": "1024x1024",
    "16x9": "1792x1024",
    "9x16": "1024x1792",
    "4x5": "1024x1792"  # Instagram portrait - using 9:16 as closest match
}

# MinIO/S3 Configuration
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL", "http://minio:9000")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY_ID", "minioadmin")
S3_SECRET_KEY = os.getenv("S3_SECRET_ACCESS_KEY", "minioadmin")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "creative-assets")

# Readiness Probe Configuration
READINESS_TIME_OUT = int(os.getenv('IMAGE_GENERATOR_READINESS_TIME_OUT', 500))

# NATS Stream configuration
CREATIVE_GENERATE_STREAM_NAME = "creative-generate-done-stream"
CREATIVE_GENERATE_DONE_SUBJECT = "creative.generate.done"
IMAGE_GENERATE_STREAM_NAME = "image-generate-stream"
IMAGE_GENERATED_SUBJECT = "image.generated"

# Global clients
mongo_client = None
db = None
publisher: JetStreamPublisher = None
subscriber: JetStreamEventSubscriber = None
openai_client: AsyncOpenAI = None
readiness_probe: ReadinessProbe = None


async def generate_image(creative_request: creative_generate_pb2.CreativeGenerateRequest):
    """
    Generate an image using DALL-E based on the creative content.
    
    Args:
        creative_request: CreativeGenerateRequest protobuf message
        
    Returns:
        dict: Generated image details
    """
    campaign_id = creative_request.campaign_id
    locale = creative_request.locale
    
    logger.info(f"🎨 Generating image for {campaign_id}:{locale}")
    
    try:
        # Get the campaign to fetch aspect ratios
        campaign = await db.campaigns.find_one({"_id": campaign_id})
        if not campaign:
            logger.error(f"❌ No campaign found: {campaign_id}")
            return None
        
        # Get aspect ratios from campaign output configuration
        aspect_ratios = campaign.get("output", {}).get("aspect_ratios", ["1x1"])
        logger.info(f"  📐 Generating {len(aspect_ratios)} aspect ratio(s): {', '.join(aspect_ratios)}")
        
        # Get the creative content from MongoDB
        creative = await db.creatives.find_one({
            "campaign_id": campaign_id,
            "locale": locale
        })
        
        if not creative:
            logger.error(f"❌ No creative found for {campaign_id}:{locale}")
            return None
        
        # Build DALL-E prompt from creative content (same for all aspect ratios)
        # NOTE: NO TEXT should be in the image - text overlay happens in a later pipeline stage
        prompt = f"""Create a professional beauty/cosmetics product advertisement image WITHOUT any text, words, or typography.

Product Context:
{creative.get('content', '')}

Requirements:
- NO text, words, letters, or typography of any kind
- High-quality, professional product photography
- Soft, flattering lighting with clean aesthetics
- Product-centric composition
- Minimalist and elegant style
- Clean background suitable for text overlay later
- Leave space for text overlay (avoid cluttered edges)
"""
        
        # Generate images for ALL aspect ratios
        generated_images = []
        
        for aspect_ratio in aspect_ratios:
            image_size = DALLE3_SIZES.get(aspect_ratio, "1024x1024")
            logger.info(f"  📐 Generating {aspect_ratio} ({image_size})...")
            
            logger.info(f"  🤖 Calling OpenAI DALL-E {OPENAI_IMAGE_MODEL}...")
            
            # Call DALL-E
            response = await openai_client.images.generate(
                model=OPENAI_IMAGE_MODEL,
                prompt=prompt,
                size=image_size,
                quality=OPENAI_IMAGE_QUALITY,
                n=1
            )
            
            image_url = response.data[0].url
            revised_prompt = response.data[0].revised_prompt if hasattr(response.data[0], 'revised_prompt') else prompt
            
            logger.info(f"  ✅ Image generated: {image_url}")
            
            # Download the image
            logger.info(f"  📥 Downloading image...")
            async with httpx.AsyncClient() as client:
                img_response = await client.get(image_url)
                img_response.raise_for_status()
                image_data = img_response.content
            
            logger.info(f"  ✅ Image downloaded ({len(image_data)} bytes)")
            
            # Upload to MinIO/S3
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            s3_key = f"campaigns/{campaign_id}/{locale}/{aspect_ratio}/generated_{timestamp}.png"
            s3_uri = f"s3://{S3_BUCKET_NAME}/{s3_key}"
            
            logger.info(f"  📤 Uploading to S3: {s3_uri}")
            
            # TODO: Implement S3 upload using boto3
            # For now, just log it
            logger.info(f"  ⚠️  S3 upload not yet implemented, would upload to: {s3_uri}")
            
            # Save image metadata to MongoDB
            image_doc = {
                "campaign_id": campaign_id,
                "locale": locale,
                "aspect_ratio": aspect_ratio,
                "image_url": image_url,
                "s3_uri": s3_uri,
                "prompt_used": revised_prompt,
                "model": OPENAI_IMAGE_MODEL,
                "size": image_size,
                "quality": OPENAI_IMAGE_QUALITY,
                "status": "generated",
                "generated_at": datetime.utcnow(),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            await db.images.insert_one(image_doc)
            logger.info(f"  💾 Saved image metadata to MongoDB: {campaign_id}:{locale}:{aspect_ratio}")
            
            generated_images.append({
                "aspect_ratio": aspect_ratio,
                "image_url": image_url,
                "s3_uri": s3_uri
            })
        
        logger.info(f"  🎉 Generated {len(generated_images)} images for {campaign_id}:{locale}")
        
        return {
            "campaign_id": campaign_id,
            "locale": locale,
            "images": generated_images
        }
        
    except Exception as e:
        logger.error(f"❌ Error generating image: {e}", exc_info=True)
        raise

async def handle_creative_request(msg: Msg):
    """
    Handle incoming creative generation requests.
    """
    readiness_probe.update_last_seen()
    
    try:
        # Parse the message
        creative_done = creative_generate_pb2.CreativeGenerateDone()
        creative_done.ParseFromString(msg.data)
        
        logger.info(f"✉️ Received creative.generate.done: {creative_done.campaign_id}:{creative_done.locale}")
        
        # Generate image (convert done message to request-like object for compatibility)
        class CreativeRequest:
            def __init__(self, done_msg):
                self.campaign_id = done_msg.campaign_id
                self.locale = done_msg.locale
                self.correlation_id = done_msg.correlation_id
        
        result = await generate_image(CreativeRequest(creative_done))
        
        if result and "images" in result:
            # Publish one message per aspect ratio
            for img in result["images"]:
                image_generated = image_generate_pb2.ImageGenerated(
                    campaign_id=creative_done.campaign_id,
                    locale=creative_done.locale,
                    product_id="",  # TODO: Get from campaign data
                    image_url=img["image_url"],
                    s3_uri=img["s3_uri"],
                    prompt_used="",  # Stored in MongoDB
                    status="generated",
                    generated_at=datetime.utcnow().isoformat() + "Z"
                )
                
                await publisher.publish(image_generated)
                logger.info(f"📤 Published image.generated for {creative_done.campaign_id}:{creative_done.locale}:{img['aspect_ratio']}")
        
        # Acknowledge the message
        await msg.ack()
        logger.info(f"✅ Acknowledged creative.generate.done: {creative_done.campaign_id}:{creative_done.locale}")
        
    except Exception as e:
        logger.error(f"❌ Error processing creative request: {e}", exc_info=True)
        # Negative acknowledge to retry
        await msg.nak()
        logger.warning(f"⚠️ NAKed message for retry (will be redelivered)")


# ————— Service Lifecycle —————

async def main():
    """Main service entry point."""
    global mongo_client, db, publisher, subscriber, openai_client, readiness_probe
    
    logger.info("🛠️ Image Generator service starting...")
    
    # Initialize readiness probe
    readiness_probe = ReadinessProbe(readiness_time_out=READINESS_TIME_OUT)
    threading.Thread(target=readiness_probe.start_server, daemon=True).start()
    logger.info("✅ Readiness probe server started.")
    
    # Initialize OpenAI client
    openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    logger.info(f"✅ OpenAI client initialized with model: {OPENAI_IMAGE_MODEL}")
    
    # Initialize MongoDB
    mongo_client = AsyncIOMotorClient(MONGODB_URL)
    db = mongo_client[MONGODB_DB_NAME]
    logger.info(f"✅ MongoDB connected: {MONGODB_DB_NAME}")
    
    # Initialize NATS publisher
    publisher = JetStreamPublisher(
        subject=IMAGE_GENERATED_SUBJECT,
        stream_name=IMAGE_GENERATE_STREAM_NAME,
        nats_url=NATS_URL,
        nats_reconnect_time_wait=NATS_RECONNECT_TIME_WAIT,
        nats_connect_timeout=NATS_CONNECT_TIMEOUT,
        nats_max_reconnect_attempts=NATS_MAX_RECONNECT_ATTEMPTS,
        message_type="ImageGenerated"
    )
    await publisher.connect()
    logger.info("✅ Image generation publisher connected to NATS.")
    
    # Initialize NATS subscriber
    subscriber = JetStreamEventSubscriber(
        nats_url=NATS_URL,
        stream_name=CREATIVE_GENERATE_STREAM_NAME,
        subject=CREATIVE_GENERATE_DONE_SUBJECT,
        connect_timeout=NATS_CONNECT_TIMEOUT,
        reconnect_time_wait=NATS_RECONNECT_TIME_WAIT,
        max_reconnect_attempts=NATS_MAX_RECONNECT_ATTEMPTS,
        ack_wait=180,  # 3 minutes to process (includes DALL-E call and image download)
        max_deliver=3,  # Retry up to 3 times
        proto_message_type=creative_generate_pb2.CreativeGenerateDone
    )
    
    subscriber.set_event_handler(handle_creative_request)
    
    try:
        await subscriber.connect_and_subscribe()
        logger.info(f"✅ Subscribed to {CREATIVE_GENERATE_DONE_SUBJECT}")
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
        logger.info("✅ Image Generator service stopped.")


if __name__ == "__main__":
    asyncio.run(main())
