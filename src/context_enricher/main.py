"""
Context Enricher Service
Subscribes to context.enrich.request and enriches campaign context per locale using OpenAI LLM.
Follows sentinel-AI production patterns for reliability and observability.
"""

import os
import logging
import asyncio
import json
import threading
from datetime import datetime
from dotenv import load_dotenv
from nats.aio.msg import Msg

from motor.motor_asyncio import AsyncIOMotorClient
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from typing import List

from src.lib_py.gen_types import context_enrich_pb2
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
OPENAI_IMAGE_MODEL = os.getenv("OPENAI_IMAGE_MODEL", "dall-e-2")

# Readiness Probe Configuration
READINESS_TIME_OUT = int(os.getenv('CONTEXT_ENRICHER_READINESS_TIME_OUT', 500))

# NATS Stream configuration (following sentinel-AI pattern: separate streams for each stage)
CONTEXT_REQUEST_STREAM_NAME = "context-request-stream"
CONTEXT_ENRICH_REQUEST_SUBJECT = "context.enrich.request"
CONTEXT_READY_STREAM_NAME = "context-ready-stream"
CONTEXT_ENRICH_READY_SUBJECT = "context.enrich.ready"

# Global clients
mongo_client = None
db = None
publisher: JetStreamPublisher = None
subscriber: JetStreamEventSubscriber = None
openai_client: AsyncOpenAI = None
readiness_probe: ReadinessProbe = None


# Removed - initialization moved to main() following sentinel-AI pattern

# ————— Pydantic Models for Structured LLM Output —————

class MarketInsightsResponse(BaseModel):
    """Structured response from LLM for market insights."""
    market_trends: List[str] = Field(..., description="List of 3-5 current market trends")
    seasonal_context: str = Field(..., description="Current seasonal themes and how to leverage them")
    cultural_notes: str = Field(..., description="Cultural sensitivities and preferences")
    color_preferences: List[str] = Field(..., description="List of 3-5 colors that resonate with audience")
    messaging_tone: str = Field(..., description="Recommended tone and style for messaging")
    visual_style: str = Field(..., description="Visual aesthetics that appeal to audience")
    competitor_insights: List[str] = Field(..., description="List of 2-3 competitor strategy insights")
    regulatory_notes: str = Field(..., description="Regulatory or compliance considerations")


async def enrich_context(request: context_enrich_pb2.ContextEnrichRequest):
    """
    Enrich context for a campaign locale using OpenAI LLM.
    Generates market insights, trends, cultural notes, and creative guidance.
    """
    logger.info(f"🔍 Enriching context for {request.campaign_id}:{request.locale} in {request.region}")
    
    try:
        # Build prompt for LLM with explicit region/locale instructions
        current_date = datetime.utcnow().strftime("%B %Y")
        prompt = f"""You are a marketing insights expert. Generate comprehensive context for a beauty/cosmetics campaign.

CRITICAL: Generate insights SPECIFICALLY for the {request.region} region and {request.locale} locale. 
All market trends, cultural notes, and insights MUST be relevant to {request.region}, NOT other regions.

Campaign Details:
- Target Region: {request.region}
- Target Locale: {request.locale}
- Target Audience: {request.audience} in {request.region}
- Age Range: {request.age_min}-{request.age_max} years
- Products: {', '.join(request.product_names)}
- Current Date: {current_date}

Generate market insights and cultural context SPECIFICALLY for the {request.region} market.

Respond with a JSON object in this EXACT format:
{{
  "market_trends": ["trend 1 in {request.region}", "trend 2 in {request.region}", "trend 3 in {request.region}"],
  "seasonal_context": "seasonal themes and timing in {request.region}",
  "cultural_notes": "cultural sensitivities and preferences specific to {request.region}",
  "color_preferences": ["color 1 popular in {request.region}", "color 2", "color 3"],
  "messaging_tone": "recommended tone for {request.region} audience",
  "visual_style": "visual aesthetics that resonate in {request.region}",
  "competitor_insights": ["competitor insight 1 in {request.region}", "insight 2"],
  "regulatory_notes": "regulatory considerations specific to {request.region}"
}}

IMPORTANT: All insights must be relevant to {request.region}. Do NOT include insights from other regions.

Return ONLY the JSON object, no other text."""

        logger.info(f"  🤖 Calling OpenAI {OPENAI_TEXT_MODEL} for {request.region} region...")
        logger.info(f"     Region: {request.region}, Locale: {request.locale}, Audience: {request.audience}")
        
        # Call OpenAI with JSON mode
        response = await openai_client.chat.completions.create(
            model=OPENAI_TEXT_MODEL,
            messages=[
                {"role": "system", "content": "You are a marketing insights expert specializing in beauty and cosmetics campaigns. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=1500
        )
        
        # Parse and validate with Pydantic
        json_response = json.loads(response.choices[0].message.content)
        llm_insights = MarketInsightsResponse(**json_response)
        logger.info(f"  ✅ Received insights from OpenAI ({response.usage.total_tokens} tokens)")
        
        # Build enriched context
        enriched_context = {
            "campaign_id": request.campaign_id,
            "locale": request.locale,
            "region": request.region,
            "audience": request.audience,
            "age_range": {"min": request.age_min, "max": request.age_max},
            "product_names": list(request.product_names),
            
            # LLM-generated insights
            "market_trends": llm_insights.market_trends,
            "seasonal_context": llm_insights.seasonal_context,
            "cultural_notes": llm_insights.cultural_notes,
            "color_preferences": llm_insights.color_preferences,
            "messaging_tone": llm_insights.messaging_tone,
            "visual_style": llm_insights.visual_style,
            "competitor_insights": llm_insights.competitor_insights,
            "regulatory_notes": llm_insights.regulatory_notes,
            
            # Metadata
            "enriched_at": datetime.utcnow().isoformat() + "Z",
            "correlation_id": request.correlation_id,
            "llm_model": OPENAI_TEXT_MODEL,
            "llm_tokens_used": response.usage.total_tokens
        }
        
        # Save to MongoDB
        await db.context_packs.update_one(
            {"campaign_id": request.campaign_id, "locale": request.locale},
            {"$set": enriched_context},
            upsert=True
        )
        logger.info(f"  ✅ Context pack saved to MongoDB: {request.campaign_id}:{request.locale}")
        
        # Build ContextPack protobuf message
        context_pack = context_enrich_pb2.ContextPack(
            locale=request.locale,
            culture_notes=llm_insights.cultural_notes,
            tone=llm_insights.messaging_tone,
            dos=llm_insights.market_trends,
            donts=llm_insights.competitor_insights,
            banned_words=[],  # TODO: Add from brand guidelines
            legal_guidelines=llm_insights.regulatory_notes
        )
        
        # Publish context.enrich.ready
        ready_msg = context_enrich_pb2.ContextEnrichReady(
            campaign_id=request.campaign_id,
            locale=request.locale,
            context_pack=context_pack,
            correlation_id=request.correlation_id,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
        
        await publisher.publish(ready_msg)
        logger.info(f"  📤 Published context.enrich.ready for {request.campaign_id}:{request.locale}")
        
    except Exception as e:
        logger.error(f"  ❌ Error enriching context for {request.campaign_id}:{request.locale}: {e}", exc_info=True)
        raise


async def handle_enrich_request(msg: Msg):
    """
    Event handler for context.enrich.request messages.
    Called by JetStreamEventSubscriber for each message.
    
    CRITICAL: Only ACK if EVERYTHING succeeds (LLM + MongoDB + NATS publish)
    If anything fails, NAK so message is retried on another instance.
    """
    readiness_probe.update_last_seen()
    
    try:
        # Parse protobuf message
        request = context_enrich_pb2.ContextEnrichRequest()
        request.ParseFromString(msg.data)
        
        logger.info(f"✉️ Received context.enrich.request: {request.campaign_id}:{request.locale}")
        logger.info(f"   📍 Region: {request.region}, Audience: {request.audience}, Age: {request.age_min}-{request.age_max}")
        
        # Process request (this must complete successfully INCLUDING NATS publish)
        await enrich_context(request)
        
        # ONLY acknowledge if ALL steps succeeded
        await msg.ack()
        logger.info(f"✅ Acknowledged context.enrich.request: {request.campaign_id}:{request.locale}")
        
    except Exception as e:
        logger.error(f"❌ Error processing context.enrich.request: {e}", exc_info=True)
        # Negative acknowledge to retry on another instance
        await msg.nak()
        logger.warning(f"⚠️ NAKed message for retry (will be redelivered)")


async def main():
    """
    Main service loop following sentinel-AI production pattern.
    Initializes all services, starts readiness probe, and subscribes to NATS.
    """
    global mongo_client, db, publisher, subscriber, openai_client, readiness_probe
    
    logger.info("🛠️ Context Enricher service starting...")
    
    # 1. Start the readiness probe server in a separate thread
    readiness_probe = ReadinessProbe(readiness_time_out=READINESS_TIME_OUT)
    readiness_probe_thread = threading.Thread(target=readiness_probe.start_server, daemon=True)
    readiness_probe_thread.start()
    logger.info("✅ Readiness probe server started.")
    
    # 2. Validate OpenAI API key
    if not OPENAI_API_KEY:
        logger.error("❌ OPENAI_API_KEY not set. Please set it in .env")
        return  # Exit if API key is missing
    
    # 3. Initialize OpenAI client
    try:
        openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        logger.info(f"✅ OpenAI client initialized with model: {OPENAI_TEXT_MODEL}")
    except Exception as e:
        logger.error(f"❌ Failed to initialize OpenAI client: {e}")
        return  # Exit if OpenAI setup fails
    
    # 4. Initialize MongoDB
    try:
        mongo_client = AsyncIOMotorClient(MONGODB_URL)
        db = mongo_client[MONGODB_DB_NAME]
        await mongo_client.admin.command('ping')
        logger.info(f"✅ MongoDB connected: {MONGODB_DB_NAME}")
    except Exception as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}")
        return  # Exit if MongoDB connection fails
    
    # 5. Initialize context.enrich.ready publisher (publishes to separate stream)
    publisher = JetStreamPublisher(
        subject=CONTEXT_ENRICH_READY_SUBJECT,
        stream_name=CONTEXT_READY_STREAM_NAME,
        nats_url=NATS_URL,
        nats_reconnect_time_wait=NATS_RECONNECT_TIME_WAIT,
        nats_connect_timeout=NATS_CONNECT_TIMEOUT,
        nats_max_reconnect_attempts=NATS_MAX_RECONNECT_ATTEMPTS,
        message_type="ContextEnrichReady"
    )
    try:
        await publisher.connect()
        logger.info("✅ Context enrichment publisher connected to NATS.")
    except Exception as e:
        logger.error(f"❌ Failed to connect publisher to NATS: {e}")
        return  # Exit if NATS connection fails
    
    # 6. Initialize context.enrich.request subscriber (subscribes from separate stream)
    subscriber = JetStreamEventSubscriber(
        nats_url=NATS_URL,
        stream_name=CONTEXT_REQUEST_STREAM_NAME,
        subject=CONTEXT_ENRICH_REQUEST_SUBJECT,
        connect_timeout=NATS_CONNECT_TIMEOUT,
        reconnect_time_wait=NATS_RECONNECT_TIME_WAIT,
        max_reconnect_attempts=NATS_MAX_RECONNECT_ATTEMPTS,
        ack_wait=60,  # 60 seconds to process (includes LLM call)
        max_deliver=3,  # Retry up to 3 times
        proto_message_type=context_enrich_pb2.ContextEnrichRequest
    )
    subscriber.set_event_handler(handle_enrich_request)
    
    # 7. Connect and subscribe to NATS (this blocks)
    try:
        await subscriber.connect_and_subscribe()
        logger.info(f"✅ Subscribed to {CONTEXT_ENRICH_REQUEST_SUBJECT}")
    except Exception as e:
        logger.error(f"❌ Failed to connect or subscribe to NATS: {e}")
        return  # Exit if NATS connection fails
    
    # 8. Keep-alive loop (optional - subscriber.connect_and_subscribe already blocks)
    try:
        while True:
            readiness_probe.update_last_seen()
            await asyncio.sleep(10)  # Update readiness every 10 seconds
    except asyncio.CancelledError:
        logger.info("🛑 Context Enricher received shutdown signal.")
    finally:
        # 9. Cleanup
        if subscriber:
            await subscriber.close()
        if publisher:
            await publisher.close()
        if mongo_client:
            mongo_client.close()
        logger.info("✅ NATS connections closed.")


if __name__ == "__main__":
    asyncio.run(main())
