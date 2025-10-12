"""
Creative Generator Service

Consumes enriched context and generates creative content using LLM.
"""

import os
import asyncio
import json
import logging
import threading
from datetime import datetime
from dotenv import load_dotenv

from motor.motor_asyncio import AsyncIOMotorClient
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from typing import List

from src.lib_py.gen_types import creative_generate_pb2, context_enrich_pb2
from src.lib_py.middlewares.jetstream_publisher import JetStreamPublisher
from src.lib_py.middlewares.jetstream_event_subscriber import JetStreamEventSubscriber
from src.lib_py.middlewares.readiness_probe import ReadinessProbe

# ————— Environment & Logging —————
load_dotenv()

# Logging configuration
log_level_str = os.getenv('LOG_LEVEL', 'INFO').upper()
log_level = getattr(logging, log_level_str, logging.INFO)
log_format = os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.basicConfig(level=log_level, format=log_format)
logger = logging.getLogger(__name__)

# ————— Configuration —————
NATS_URL = os.getenv("NATS_URL", "nats://nats:4222")
NATS_CONNECT_TIMEOUT = int(os.getenv("NATS_CONNECT_TIMEOUT", "30"))
NATS_RECONNECT_TIME_WAIT = int(os.getenv("NATS_RECONNECT_TIME_WAIT", "2"))
NATS_MAX_RECONNECT_ATTEMPTS = int(os.getenv("NATS_MAX_RECONNECT_ATTEMPTS", "60"))
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://mongodb:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "creative_campaign")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_TEXT_MODEL = os.getenv("OPENAI_TEXT_MODEL", "gpt-4o-mini")
OPENAI_IMAGE_MODEL = os.getenv("OPENAI_IMAGE_MODEL", "dall-e-2")
READINESS_TIME_OUT = int(os.getenv('CREATIVE_GENERATOR_READINESS_TIME_OUT', '500'))

# NATS Stream configuration
CONTEXT_READY_STREAM_NAME = "context-ready-stream"
CONTEXT_ENRICH_READY_SUBJECT = "context.enrich.ready"
CREATIVE_GENERATE_STREAM_NAME = "creative-generate-done-stream"
CREATIVE_GENERATE_DONE_SUBJECT = "creative.generate.done"

# Global clients
mongo_client = None
db = None
publisher = None
subscriber = None
openai_client = None
readiness_probe = None

# ————— Pydantic Models for Structured LLM Output —————

class CampaignContentResponse(BaseModel):
    """Structured response from LLM for campaign creative content."""
    headline: str = Field(..., description="Catchy campaign headline (5-15 words)")
    description: str = Field(..., description="Short campaign description (50-100 words)")
    call_to_action: str = Field(..., description="Call-to-action text (3-8 words)")
    visual_elements: List[str] = Field(..., description="List of 3-5 suggested visual elements")

# ————— Business Logic —————

async def generate_creative(context_ready, context_pack):
    """
    Generate creative content using the enriched context.
    
    Args:
        context_ready: ContextEnrichReady protobuf message
        context_pack: ContextPack protobuf message
        
    Returns:
        dict: Generated creative content
    """
    campaign_id = context_ready.campaign_id
    locale = context_ready.locale
    
    logger.info(f"🎨 Generating creative for {campaign_id}:{locale}")
    
    try:
        # Prepare the prompt for creative generation
        prompt = f"""Based on the following context, generate creative content:
        
        Campaign ID: {campaign_id}
        Locale: {locale}
        
        Cultural Notes: {context_pack.culture_notes}
        Tone: {context_pack.tone}
        Do's: {', '.join(context_pack.dos)}
        Don'ts: {', '.join(context_pack.donts)}
        Banned Words: {', '.join(context_pack.banned_words)}
        Legal Guidelines: {context_pack.legal_guidelines}
        
        Respond with a JSON object in this EXACT format:
        {{
          "headline": "catchy headline here (5-15 words)",
          "description": "compelling description here (50-100 words)",
          "call_to_action": "clear CTA here (3-8 words)",
          "visual_elements": ["element 1", "element 2", "element 3"]
        }}
        
        Ensure ALL content respects the guidelines and cultural notes. Return ONLY the JSON object."""
        
        # Call OpenAI with structured output
        logger.info(f"  🤖 Calling OpenAI {OPENAI_TEXT_MODEL}...")
        response = await openai_client.chat.completions.create(
            model=OPENAI_TEXT_MODEL,
            messages=[
                {"role": "system", "content": "You are a creative director for digital marketing campaigns. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=500,
            temperature=0.7
        )
        
        # Parse and validate with Pydantic
        json_response = json.loads(response.choices[0].message.content)
        parsed_content = CampaignContentResponse(**json_response)
        
        # Format as markdown for storage (backward compatible)
        creative_content = f"""### 1. Catchy Headline
{parsed_content.headline}

### 2. Short Description
{parsed_content.description}

### 3. Call-to-Action
{parsed_content.call_to_action}

### 4. Suggested Visual Elements
{chr(10).join(f'- {elem}' for elem in parsed_content.visual_elements)}
"""
        logger.info(f"  ✅ Generated creative content: {parsed_content.headline}")
        
        # Save to MongoDB
        creative_doc = {
            "campaign_id": campaign_id,
            "locale": locale,
            "content": creative_content,
            "headline": parsed_content.headline,
            "description": parsed_content.description,
            "call_to_action": parsed_content.call_to_action,
            "visual_elements": parsed_content.visual_elements,
            "status": "generated",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.creatives.update_one(
            {"campaign_id": campaign_id, "locale": locale},
            {"$set": creative_doc},
            upsert=True
        )
        
        logger.info(f"  💾 Saved creative to MongoDB: {campaign_id}:{locale}")
        
        return creative_content
        
    except Exception as e:
        logger.error(f"❌ Error generating creative: {e}", exc_info=True)
        raise

async def handle_creative_request(msg):
    """
    Handle incoming creative generation requests.
    """
    readiness_probe.update_last_seen()
    
    try:
        # Parse the message
        context_ready = context_enrich_pb2.ContextEnrichReady()
        context_ready.ParseFromString(msg.data)
        context_pack = context_ready.context_pack
        
        logger.info(f"✉️ Received context.enrich.ready: {context_ready.campaign_id}:{context_ready.locale}")
        
        # Generate creative
        creative_content = await generate_creative(context_ready, context_pack)
        
        # Publish creative.generate.done event
        done_msg = creative_generate_pb2.CreativeGenerateDone(
            campaign_id=context_ready.campaign_id,
            locale=context_ready.locale,
            correlation_id=context_ready.correlation_id,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
        
        await publisher.publish(done_msg)
        logger.info(f"📤 Published creative.generate.done for {context_ready.campaign_id}:{context_ready.locale}")
        
        # Acknowledge the message
        await msg.ack()
        logger.info(f"✅ Acknowledged context.enrich.ready: {context_ready.campaign_id}:{context_ready.locale}")
        
    except Exception as e:
        logger.error(f"❌ Error processing creative request: {e}", exc_info=True)
        # Negative acknowledge to retry
        await msg.nak()
        logger.warning(f"⚠️ NAKed message for retry (will be redelivered)")

# ————— Service Lifecycle —————

async def update_readiness_continuously():
    """Update readiness probe in the background."""
    while True:
        readiness_probe.update_last_seen()
        await asyncio.sleep(10)

async def main():
    """Main service entry point."""
    global mongo_client, db, publisher, subscriber, openai_client, readiness_probe
    
    logger.info("🛠️ Creative Generator service starting...")
    
    # 1. Start Readiness Probe
    readiness_probe = ReadinessProbe(readiness_time_out=READINESS_TIME_OUT)
    threading.Thread(target=readiness_probe.start_server, daemon=True).start()
    logger.info("✅ Readiness probe server started.")
    
    # 2. Initialize OpenAI client
    if not OPENAI_API_KEY:
        logger.error("❌ OPENAI_API_KEY not set. Please set it in .env")
        return
        
    openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    logger.info(f"✅ OpenAI client initialized with model: {OPENAI_TEXT_MODEL}")
    
    # 3. Initialize MongoDB
    try:
        mongo_client = AsyncIOMotorClient(MONGODB_URL)
        db = mongo_client[MONGODB_DB_NAME]
        await mongo_client.admin.command('ping')
        logger.info(f"✅ MongoDB connected: {MONGODB_DB_NAME}")
    except Exception as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}")
        return
    
    # 4. Initialize creative.generate.done publisher
    publisher = JetStreamPublisher(
        subject=CREATIVE_GENERATE_DONE_SUBJECT,
        stream_name=CREATIVE_GENERATE_STREAM_NAME,
        nats_url=NATS_URL,
        nats_reconnect_time_wait=NATS_RECONNECT_TIME_WAIT,
        nats_connect_timeout=NATS_CONNECT_TIMEOUT,
        nats_max_reconnect_attempts=NATS_MAX_RECONNECT_ATTEMPTS,
        message_type="CreativeGenerateDone"
    )
    
    try:
        await publisher.connect()
        logger.info("✅ Creative generation publisher connected to NATS.")
    except Exception as e:
        logger.error(f"❌ Failed to connect publisher to NATS: {e}")
        return
    
    # 5. Initialize context.enrich.ready subscriber
    subscriber = JetStreamEventSubscriber(
        nats_url=NATS_URL,
        stream_name=CONTEXT_READY_STREAM_NAME,
        subject=CONTEXT_ENRICH_READY_SUBJECT,
        connect_timeout=NATS_CONNECT_TIMEOUT,
        reconnect_time_wait=NATS_RECONNECT_TIME_WAIT,
        max_reconnect_attempts=NATS_MAX_RECONNECT_ATTEMPTS,
        ack_wait=120,  # 2 minutes to process (includes LLM call)
        max_deliver=3,  # Retry up to 3 times
        proto_message_type=context_enrich_pb2.ContextPack
    )
    
    subscriber.set_event_handler(handle_creative_request)
    
    try:
        await subscriber.connect_and_subscribe()
        logger.info(f"✅ Subscribed to {CONTEXT_ENRICH_READY_SUBJECT}")
    except Exception as e:
        logger.error(f"❌ Failed to connect or subscribe to NATS: {e}")
        return
    
    # 6. Keep-alive loop
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
        logger.info("Cleaning up resources...")
        if subscriber:
            await subscriber.close()
        if publisher:
            await publisher.close()
        if mongo_client:
            mongo_client.close()
        logger.info("✅ Cleanup complete")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nShutting down gracefully...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise
