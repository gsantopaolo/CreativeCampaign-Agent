"""
Creative Campaign API Gateway
FastAPI service for creative automation pipeline with MongoDB + NATS JetStream
"""

import os
import logging
import threading
import asyncio
import uuid
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

from src.lib_py.models.campaign_models import (
    Campaign, Variant, ContextPack,
    CampaignCreateRequest, CampaignCreateResponse,
    CampaignSummary, StatusResponse,
    ApprovalRequest, RevisionRequest,
    CampaignStatus, VariantStatus, Locale,
    ErrorResponse
)
from src.lib_py.middlewares.jetstream_publisher import JetStreamPublisher
from src.lib_py.middlewares.readiness_probe import ReadinessProbe
from src.lib_py.gen_types import (
    campaign_brief_pb2,
    context_enrich_pb2,
    creative_generate_pb2,
    approval_events_pb2
)

# ————— Environment & Logging —————
load_dotenv()
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format=os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger = logging.getLogger("creative-campaign-api")

# ————— MongoDB Setup —————
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "creative_campaign")

mongo_client: Optional[AsyncIOMotorClient] = None
db = None

# ————— NATS JetStream Setup —————
NATS_URL = os.getenv("NATS_URL", "nats://localhost:4222")
NATS_OPTIONS = dict(
    nats_url=NATS_URL,
    nats_reconnect_time_wait=int(os.getenv("NATS_RECONNECT_TIME_WAIT", 10)),
    nats_connect_timeout=int(os.getenv("NATS_CONNECT_TIMEOUT", 10)),
    nats_max_reconnect_attempts=int(os.getenv("NATS_MAX_RECONNECT_ATTEMPTS", 60)),
)

probe: ReadinessProbe
briefs_ingested_publisher: JetStreamPublisher
context_enrich_publisher: JetStreamPublisher
creative_generate_publisher: JetStreamPublisher
creative_approved_publisher: JetStreamPublisher
revision_requested_publisher: JetStreamPublisher

# ————— FastAPI App —————
app = FastAPI(
    title="Creative Campaign API",
    description="API Gateway for Creative Automation Pipeline",
    version="1.0.0",
)


async def update_readiness_continuously(interval_seconds: int = 10):
    """Periodically updates the readiness probe's last seen time."""
    while True:
        if probe:
            probe.update_last_seen()
        await asyncio.sleep(interval_seconds)


@app.on_event("startup")
async def startup_event():
    """Initialize MongoDB, NATS publishers, and readiness probe."""
    global mongo_client, db, probe
    global briefs_ingested_publisher, context_enrich_publisher
    global creative_generate_publisher, creative_approved_publisher
    global revision_requested_publisher
    
    logger.info("🚀 API starting up...")
    logger.info("")
    logger.info("📡 Connecting to infrastructure...")
    
    # ————— MongoDB Connection —————
    try:
        mongo_client = AsyncIOMotorClient(MONGODB_URL)
        db = mongo_client[MONGODB_DB_NAME]
        
        # Test connection
        await mongo_client.admin.command('ping')
        logger.info(f"  ✅ MongoDB connected: {MONGODB_DB_NAME} @ {MONGODB_URL}")
        
        # Create indexes
        await db.campaigns.create_index("campaign_id", unique=True)
        await db.variants.create_index([("campaign_id", 1), ("product_id", 1), ("locale", 1)])
        await db.variants.create_index("is_best")
        await db.context_packs.create_index([("campaign_id", 1), ("locale", 1)], unique=True)
        logger.info(f"  ✅ MongoDB indexes created")
        
    except Exception as e:
        logger.critical(f"❌ MongoDB connection failed: {e}")
        raise RuntimeError(f"MongoDB connection failed: {e}")
    
    # ————— NATS Publishers —————
    try:
        # Temporarily suppress JetStreamPublisher logging
        js_logger = logging.getLogger("JetStreamPublisher")
        original_level = js_logger.level
        js_logger.setLevel(logging.WARNING)
        
        logger.info(f"  🔌 Connecting to NATS @ {NATS_URL}...")
        
        briefs_ingested_publisher = JetStreamPublisher(
            subject="briefs.ingested",
            stream_name="creative-briefs-stream",
            message_type="CampaignBrief",
            **NATS_OPTIONS
        )
        await briefs_ingested_publisher.connect()
        
        context_enrich_publisher = JetStreamPublisher(
            subject="context.enrich.request",
            stream_name="creative-context-stream",
            message_type="ContextEnrichRequest",
            **NATS_OPTIONS
        )
        await context_enrich_publisher.connect()
        
        creative_generate_publisher = JetStreamPublisher(
            subject="creative.generate.request",
            stream_name="creative-generate-stream",
            message_type="CreativeGenerateRequest",
            **NATS_OPTIONS
        )
        await creative_generate_publisher.connect()
        
        creative_approved_publisher = JetStreamPublisher(
            subject="creative.approved",
            stream_name="creative-approval-stream",
            message_type="CreativeApproved",
            **NATS_OPTIONS
        )
        await creative_approved_publisher.connect()
        
        revision_requested_publisher = JetStreamPublisher(
            subject="creative.revision.requested",
            stream_name="creative-revision-stream",
            message_type="RevisionRequested",
            **NATS_OPTIONS
        )
        await revision_requested_publisher.connect()
        
        # Restore logging level
        js_logger.setLevel(original_level)
        
        logger.info(f"  ✅ NATS connected: 5 publishers initialized")
        
    except Exception as e:
        logger.critical(f"❌ NATS connection failed: {e}")
        raise RuntimeError(f"NATS connection failed: {e}")
    
    # ————— Readiness Probe —————
    probe = ReadinessProbe(readiness_time_out=500)
    threading.Thread(target=probe.start_server, daemon=True).start()
    logger.info("  ✅ Readiness probe started on :8080/healthz")
    
    # ————— Background Task —————
    asyncio.create_task(update_readiness_continuously())
    
    logger.info("")
    logger.info("🎉 API startup complete - Ready to accept requests!")
    logger.info("")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup connections on shutdown."""
    logger.info("🛑 API shutting down...")
    
    if mongo_client:
        mongo_client.close()
        logger.info("✅ MongoDB connection closed")
    
    publishers = [
        briefs_ingested_publisher,
        context_enrich_publisher,
        creative_generate_publisher,
        creative_approved_publisher,
        revision_requested_publisher
    ]
    
    for pub in publishers:
        if pub:
            await pub.close()
    
    logger.info("✅ NATS publishers closed")


# ————— Health Check Endpoints —————

@app.get("/healthz", status_code=200)
async def healthz():
    """Kubernetes readiness probe endpoint."""
    return {"status": "ok"}


@app.get("/", status_code=200)
async def root():
    """API root endpoint."""
    return {
        "service": "Creative Campaign API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/metrics", status_code=200)
async def metrics():
    """
    Prometheus-style metrics endpoint.
    Returns basic system metrics in Prometheus exposition format.
    """
    try:
        # Get counts from MongoDB
        total_campaigns = await db.campaigns.count_documents({})
        total_variants = await db.variants.count_documents({})
        
        # Count by status
        campaigns_by_status = {}
        async for doc in db.campaigns.aggregate([
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]):
            campaigns_by_status[doc["_id"]] = doc["count"]
        
        variants_by_status = {}
        async for doc in db.variants.aggregate([
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]):
            variants_by_status[doc["_id"]] = doc["count"]
        
        # Format as Prometheus exposition format
        metrics_text = f"""# HELP creative_campaign_total Total number of campaigns
# TYPE creative_campaign_total gauge
creative_campaign_total {total_campaigns}

# HELP creative_variant_total Total number of variants
# TYPE creative_variant_total gauge
creative_variant_total {total_variants}

# HELP creative_campaign_by_status Campaigns by status
# TYPE creative_campaign_by_status gauge
"""
        for status_val, count in campaigns_by_status.items():
            metrics_text += f'creative_campaign_by_status{{status="{status_val}"}} {count}\n'
        
        metrics_text += """
# HELP creative_variant_by_status Variants by status
# TYPE creative_variant_by_status gauge
"""
        for status_val, count in variants_by_status.items():
            metrics_text += f'creative_variant_by_status{{status="{status_val}"}} {count}\n'
        
        return JSONResponse(
            content=metrics_text,
            media_type="text/plain; version=0.0.4"
        )
    except Exception as e:
        logger.error(f"❌ Error generating metrics: {e}")
        return JSONResponse(
            content="# Error generating metrics\n",
            media_type="text/plain"
        )


# ————— Campaign Endpoints —————

@app.post("/campaigns", status_code=status.HTTP_202_ACCEPTED, response_model=CampaignCreateResponse)
async def create_campaign(request: CampaignCreateRequest):
    """
    Create a new campaign brief.
    Validates, saves to MongoDB, publishes to NATS, returns 202 Accepted.
    """
    correlation_id = str(uuid.uuid4())
    logger.info(f"✉️  Received campaign brief: {request.campaign_id} (correlation: {correlation_id})")
    
    try:
        # Check if campaign already exists
        existing = await db.campaigns.find_one({"_id": request.campaign_id})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Campaign {request.campaign_id} already exists"
            )
        
        # Create campaign document
        campaign = Campaign(
            campaign_id=request.campaign_id,
            products=request.products,
            target_locales=request.target_locales,
            audience=request.audience,
            localization=request.localization,
            brand=request.brand,
            placement=request.placement,
            output=request.output,
            status=CampaignStatus.PROCESSING,
            correlation_id=correlation_id
        )
        
        # Save to MongoDB
        campaign_dict = campaign.model_dump(by_alias=True)
        await db.campaigns.insert_one(campaign_dict)
        logger.info(f"✅ Campaign {request.campaign_id} saved to MongoDB")
        
        # Publish to NATS: briefs.ingested
        brief_pb = campaign_brief_pb2.CampaignBrief(
            campaign_id=campaign.campaign_id,
            products=[
                campaign_brief_pb2.Product(
                    id=p.id,
                    name=p.name,
                    description=p.description
                ) for p in campaign.products
            ],
            target_locales=campaign.target_locales,
            audience=campaign_brief_pb2.Audience(
                region=campaign.audience.region,
                audience=campaign.audience.audience,
                age_min=campaign.audience.age_min or 0,
                age_max=campaign.audience.age_max or 0,
                interests_text=campaign.audience.interests_text or ""
            ),
            localization=campaign_brief_pb2.Localization(
                message_en=campaign.localization.message_en,
                message_de=campaign.localization.message_de or "",
                message_fr=campaign.localization.message_fr or "",
                message_it=campaign.localization.message_it or ""
            ),
            correlation_id=correlation_id,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
        
        if campaign.brand:
            brief_pb.brand.CopyFrom(campaign_brief_pb2.BrandCompliance(
                primary_color=campaign.brand.primary_color or "",
                logo_s3_uri=campaign.brand.logo_s3_uri or "",
                banned_words_en=campaign.brand.banned_words_en or [],
                banned_words_de=campaign.brand.banned_words_de or [],
                banned_words_fr=campaign.brand.banned_words_fr or [],
                banned_words_it=campaign.brand.banned_words_it or [],
                legal_guidelines=campaign.brand.legal_guidelines or ""
            ))
        
        if campaign.placement:
            brief_pb.placement.CopyFrom(campaign_brief_pb2.BrandPlacement(
                logo_position=campaign.placement.logo_position.value,
                overlay_text_position=campaign.placement.overlay_text_position.value
            ))
        
        if campaign.output:
            brief_pb.output.CopyFrom(campaign_brief_pb2.OutputSpec(
                aspect_ratios=[ar.value for ar in campaign.output.aspect_ratios],
                format=campaign.output.format.value,
                s3_prefix=campaign.output.s3_prefix
            ))
        
        await briefs_ingested_publisher.publish(
            subject="briefs.ingested",
            data=brief_pb.SerializeToString(),
            headers={"correlation_id": correlation_id}
        )
        logger.info(f"📤 Published briefs.ingested for {request.campaign_id}")
        
        # Trigger orchestration (async)
        asyncio.create_task(orchestrate_campaign(campaign, correlation_id))
        
        return CampaignCreateResponse(
            campaign_id=campaign.campaign_id,
            status=campaign.status,
            message=f"Campaign {campaign.campaign_id} accepted and processing started"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creating campaign: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create campaign: {str(e)}"
        )


async def orchestrate_campaign(campaign: Campaign, correlation_id: str):
    """
    Orchestration logic: trigger context enrichment and image generation.
    Runs asynchronously after campaign creation.
    """
    logger.info(f"🔄 Starting orchestration for {campaign.campaign_id}")
    
    try:
        # For each locale, trigger context enrichment
        for locale in campaign.target_locales:
            context_request = context_enrich_pb2.ContextEnrichRequest(
                campaign_id=campaign.campaign_id,
                locale=locale.value,
                region=campaign.audience.region,
                audience=campaign.audience.audience,
                age_min=campaign.audience.age_min or 0,
                age_max=campaign.audience.age_max or 0,
                interests_text=campaign.audience.interests_text or "",
                product_names=[p.name for p in campaign.products],
                correlation_id=correlation_id,
                timestamp=datetime.utcnow().isoformat() + "Z"
            )
            
            await context_enrich_publisher.publish(
                subject="context.enrich.request",
                data=context_request.SerializeToString(),
                headers={"correlation_id": correlation_id}
            )
            logger.info(f"📤 Published context.enrich.request for {campaign.campaign_id}:{locale.value}")
        
        logger.info(f"✅ Orchestration triggered for {campaign.campaign_id}")
        
    except Exception as e:
        logger.error(f"❌ Orchestration error for {campaign.campaign_id}: {e}", exc_info=True)
        # Update campaign status to failed
        await db.campaigns.update_one(
            {"_id": campaign.campaign_id},
            {"$set": {"status": CampaignStatus.FAILED.value, "updated_at": datetime.utcnow()}}
        )


@app.get("/campaigns/{campaign_id}", response_model=Campaign)
async def get_campaign(campaign_id: str):
    """Get campaign details by ID."""
    campaign_doc = await db.campaigns.find_one({"_id": campaign_id})
    
    if not campaign_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign {campaign_id} not found"
        )
    
    return Campaign(**campaign_doc)


@app.get("/campaigns", response_model=List[CampaignSummary])
async def list_campaigns(
    page: int = 1,
    page_size: int = 20,
    status_filter: Optional[CampaignStatus] = None
):
    """List campaigns with pagination."""
    skip = (page - 1) * page_size
    
    query = {}
    if status_filter:
        query["status"] = status_filter.value
    
    cursor = db.campaigns.find(query).skip(skip).limit(page_size).sort("created_at", -1)
    campaigns = await cursor.to_list(length=page_size)
    
    summaries = [
        CampaignSummary(
            campaign_id=c["_id"],
            status=CampaignStatus(c["status"]),
            total_variants=c.get("total_variants", 0),
            approved_variants=c.get("approved_variants", 0),
            created_at=c["created_at"],
            products=[Product(**p) for p in c["products"]],
            target_locales=[Locale(loc) for loc in c["target_locales"]]
        )
        for c in campaigns
    ]
    
    return summaries


@app.get("/campaigns/{campaign_id}/status", response_model=StatusResponse)
async def get_campaign_status(campaign_id: str):
    """Get campaign processing status."""
    campaign_doc = await db.campaigns.find_one({"_id": campaign_id})
    
    if not campaign_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign {campaign_id} not found"
        )
    
    # Get variant counts per product/locale
    variants_cursor = db.variants.find({"campaign_id": campaign_id})
    variants = await variants_cursor.to_list(length=1000)
    
    progress = {}
    for variant in variants:
        key = f"{variant['product_id']}:{variant['locale']}"
        if key not in progress:
            progress[key] = {
                "status": variant["status"],
                "is_best": variant.get("is_best", False),
                "approved": variant.get("approved", False)
            }
    
    return StatusResponse(
        campaign_id=campaign_id,
        status=CampaignStatus(campaign_doc["status"]),
        progress=progress
    )


@app.get("/variants", response_model=List[Variant])
async def list_variants(
    campaign_id: str,
    product_id: Optional[str] = None,
    locale: Optional[Locale] = None,
    is_best: Optional[bool] = None
):
    """List variants for a campaign."""
    query = {"campaign_id": campaign_id}
    
    if product_id:
        query["product_id"] = product_id
    if locale:
        query["locale"] = locale.value
    if is_best is not None:
        query["is_best"] = is_best
    
    cursor = db.variants.find(query).sort("created_at", -1)
    variants_docs = await cursor.to_list(length=100)
    
    variants = [Variant(**v) for v in variants_docs]
    return variants


@app.post("/campaigns/{campaign_id}/approve", status_code=status.HTTP_200_OK)
async def approve_campaign(campaign_id: str, request: ApprovalRequest):
    """Approve a creative variant."""
    logger.info(f"✅ Approval request for {campaign_id}:{request.product_id}:{request.locale.value}")
    
    # Update variant in MongoDB
    update_result = await db.variants.update_one(
        {"_id": request.variant_id, "campaign_id": campaign_id},
        {
            "$set": {
                "approved": True,
                "approved_by": request.approved_by,
                "approved_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    if update_result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Variant {request.variant_id} not found"
        )
    
    # Update campaign approved count
    await db.campaigns.update_one(
        {"_id": campaign_id},
        {"$inc": {"approved_variants": 1}, "$set": {"updated_at": datetime.utcnow()}}
    )
    
    # Publish approval event
    approval_pb = approval_events_pb2.CreativeApproved(
        campaign_id=campaign_id,
        product_id=request.product_id,
        variant_id=request.variant_id,
        locale=request.locale.value,
        approved_by=request.approved_by,
        correlation_id=str(uuid.uuid4()),
        timestamp=datetime.utcnow().isoformat() + "Z"
    )
    
    await creative_approved_publisher.publish(
        subject="creative.approved",
        data=approval_pb.SerializeToString()
    )
    
    logger.info(f"📤 Published creative.approved for {campaign_id}:{request.variant_id}")
    
    return {"ok": True, "message": f"Variant {request.variant_id} approved"}


@app.post("/campaigns/{campaign_id}/revision", status_code=status.HTTP_202_ACCEPTED)
async def request_revision(campaign_id: str, request: RevisionRequest):
    """Request changes to a creative variant."""
    correlation_id = str(uuid.uuid4())
    logger.info(f"🔄 Revision request for {campaign_id}:{request.product_id}:{request.locale.value}")
    
    # Publish revision event
    revision_pb = approval_events_pb2.RevisionRequested(
        campaign_id=campaign_id,
        product_id=request.product_id,
        locale=request.locale.value,
        from_revision=request.from_revision,
        feedback=request.feedback,
        requested_by=request.requested_by,
        correlation_id=correlation_id,
        timestamp=datetime.utcnow().isoformat() + "Z"
    )
    
    await revision_requested_publisher.publish(
        subject="creative.revision.requested",
        data=revision_pb.SerializeToString(),
        headers={"correlation_id": correlation_id}
    )
    
    logger.info(f"📤 Published creative.revision.requested for {campaign_id}")
    
    return {"ok": True, "message": "Revision request accepted, new generation will start"}


# ————— Main Entry Point —————

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
