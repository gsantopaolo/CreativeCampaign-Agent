# Implementation Patterns

## Overview

This document describes the key implementation patterns used in the CreativeCampaign-Agent system. The architecture demonstrates production-ready patterns for event-driven microservices using Python, NATS JetStream, and OpenAI APIs.

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Streamlit | Campaign creation UI |
| **API** | FastAPI | REST API + orchestration |
| **Message Bus** | NATS JetStream | Event-driven communication |
| **Database** | MongoDB | Campaign metadata |
| **Storage** | MinIO/S3 | Asset storage |
| **AI/ML** | OpenAI (DALL-E 3, GPT-4o-mini) | Image generation + text + vision |
| **Image Processing** | PIL (Pillow) | Logo overlay, text rendering |
| **Infrastructure** | Docker Compose | Local development |

---

## Service Architecture

### 1. API Gateway (FastAPI)

**File**: `src/api/main.py`

**Responsibilities:**
- REST API endpoints
- Campaign orchestration
- NATS event publishing
- MongoDB persistence

**Key Pattern**: Orchestration in API layer (not separate service)

```python
@app.post("/campaigns")
async def create_campaign(brief: CampaignBrief):
    # Save to MongoDB
    await db.campaigns.insert_one(brief.dict())
    
    # Publish to NATS
    await nats.publish("briefs.ingested", brief)
    
    return {"status": "accepted", "campaign_id": brief.campaign_id}
```

### 2. Worker Services (Event-Driven)

All worker services follow the same pattern:

**Pattern**:
1. Subscribe to NATS subject
2. Process message
3. Publish result to next subject
4. ACK/NAK for reliability

**Services:**
- `context-enricher` - Builds locale context using GPT-4o-mini
- `creative-generator` - Generates creative content using GPT-4o-mini
- `image-generator` - Generates images using DALL-E 3
- `brand-composer` - Adds logo using GPT-4o-mini vision + PIL
- `text-overlay` - Adds text and exports using PIL

---

## Key Patterns

### 1. NATS JetStream Publisher/Subscriber

**Implementation**: `src/lib_py/middlewares/jetstream_publisher.py`

**Pattern**:
```python
class JetStreamPublisher:
    def __init__(self, subject, stream_name, nats_url):
        self.subject = subject
        self.stream_name = stream_name
        self.nats_url = nats_url
    
    async def connect(self):
        self.nc = await nats.connect(self.nats_url)
        self.js = self.nc.jetstream()
        
        # Create stream if not exists
        await self.js.add_stream(
            name=self.stream_name,
            subjects=[self.subject]
        )
    
    async def publish(self, message):
        await self.js.publish(self.subject, message.SerializeToString())
```

**Subscriber Pattern**:
```python
class JetStreamEventSubscriber:
    async def connect_and_subscribe(self):
        self.nc = await nats.connect(self.nats_url)
        self.js = self.nc.jetstream()
        
        # Subscribe with queue group (only one replica processes each message)
        await self.js.subscribe(
            self.subject,
            queue=f"q.{self.subject}",
            cb=self.message_handler,
            durable=self.subject.replace(".", "-"),
            manual_ack=True,
            ack_wait=self.ack_wait,
            max_deliver=self.max_deliver
        )
    
    async def message_handler(self, msg):
        try:
            # Process message
            await self.event_handler(msg)
            await msg.ack()
        except Exception as e:
            logger.error(f"Error: {e}")
            await msg.nak()  # Retry
```

### 2. Health Checks (Readiness Probes)

**Implementation**: `src/lib_py/middlewares/readiness_probe.py`

**Pattern**:
```python
class ReadinessProbe:
    def __init__(self, readiness_time_out: int):
        self.readiness_time_out = readiness_time_out
        self.last_seen = time.time()
    
    def update_last_seen(self):
        self.last_seen = time.time()
    
    def is_ready(self) -> bool:
        return (time.time() - self.last_seen) < self.readiness_time_out
    
    def start_server(self):
        # Simple HTTP server on port 8080
        # Returns 200 if ready, 503 if not
```

**Usage in services**:
```python
# Update on every message processed
async def handle_message(msg):
    readiness_probe.update_last_seen()
    # Process message...
```

### 3. OpenAI Integration

**DALL-E 3 Image Generation**:
```python
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

response = await client.images.generate(
    model="dall-e-3",
    prompt=prompt,
    size="1024x1024",
    quality="standard",
    n=1
)

image_url = response.data[0].url
```

**GPT-4o-mini Text Generation**:
```python
response = await client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a creative copywriter"},
        {"role": "user", "content": prompt}
    ]
)

text = response.choices[0].message.content
```

**GPT-4o-mini Vision (Logo Placement)**:
```python
response = await client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Analyze this image for logo placement"},
                {"type": "image_url", "image_url": {"url": image_url}}
            ]
        }
    ],
    response_format={"type": "json_object"}  # Structured output
)

placement = json.loads(response.choices[0].message.content)
```

### 4. Structured Logging

**Pattern**:
```python
import logging

# Configure from environment
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
log_format = os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logging.basicConfig(level=getattr(logging, log_level), format=log_format)
logger = logging.getLogger(__name__)

# Use emojis for visual scanning
logger.info("🚀 Service starting...")
logger.info("✅ Connected to NATS")
logger.error("❌ Failed to process message")
logger.warning("⚠️  Retrying...")
```

### 5. Error Handling & Retries

**NATS Retry Pattern**:
```python
# Configuration
NATS_MAX_DELIVER = 3  # Try 3 times
NATS_ACK_WAIT = 60    # Wait 60s for ack

async def message_handler(msg: Msg):
    try:
        # Process message
        result = await process(msg.data)
        await msg.ack()  # Success
    except Exception as e:
        logger.error(f"Error: {e}")
        await msg.nak()  # Retry (up to MAX_DELIVER times)
        # After 3 failures, goes to DLQ automatically
```

### 6. Docker Compose Patterns

**Service Template**:
```yaml
services:
  image-generator:
    build:
      context: ../
      dockerfile: src/image_generator/Dockerfile
    container_name: creative-image-generator
    restart: unless-stopped
    environment:
      - MONGODB_URL=mongodb://mongodb:27017
      - NATS_URL=nats://nats:4222
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      mongodb:
        condition: service_healthy
      nats:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:8080/healthz"]
      interval: 10s
      timeout: 3s
      retries: 3
    networks:
      - creative-backend-network
```

### 7. MongoDB Patterns

**Connection**:
```python
from motor.motor_asyncio import AsyncIOMotorClient

mongo_client = AsyncIOMotorClient(MONGODB_URL)
db = mongo_client[MONGODB_DB_NAME]
```

**CRUD Operations**:
```python
# Create
await db.campaigns.insert_one(campaign_dict)

# Read
campaign = await db.campaigns.find_one({"_id": campaign_id})

# Update
await db.campaigns.update_one(
    {"_id": campaign_id},
    {"$set": {"status": "completed"}}
)

# Query
images = await db.images.find({
    "campaign_id": campaign_id,
    "locale": "en"
}).to_list(length=100)
```

### 8. S3/MinIO Patterns

**Upload**:
```python
import boto3

s3_client = boto3.client(
    's3',
    endpoint_url=S3_ENDPOINT_URL,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY
)

s3_client.upload_fileobj(
    image_data,
    S3_BUCKET_NAME,
    s3_key
)
```

**Generate Presigned URL**:
```python
url = s3_client.generate_presigned_url(
    'get_object',
    Params={'Bucket': S3_BUCKET_NAME, 'Key': s3_key},
    ExpiresIn=3600  # 1 hour
)
```

---

## Service Communication Flow

```
1. User creates campaign in Streamlit UI
2. UI calls API: POST /campaigns
3. API saves to MongoDB
4. API publishes: briefs.ingested
5. context-enricher subscribes, processes, publishes: context.enrich.ready
6. creative-generator subscribes, processes, publishes: creative.generate.done
7. image-generator subscribes, processes, publishes: image.generated
8. brand-composer subscribes, processes, publishes: brand.composed
9. text-overlay subscribes, processes, publishes: text.overlay.done
10. API notifies UI: Campaign ready!
```

---

## Reliability Patterns

### 1. Retries
- NATS automatically retries failed messages (max 3 times)
- Exponential backoff between retries

### 2. Dead Letter Queue (DLQ)
- After 3 failures, message goes to DLQ
- Guardian service monitors DLQ and alerts

### 3. Health Checks
- Every service exposes `/healthz` endpoint
- Docker healthcheck monitors service health
- Kubernetes-compatible readiness probes

### 4. Graceful Degradation
- Services continue processing other messages if one fails
- Failed messages don't block the queue

---

## Scalability Patterns

### Horizontal Scaling
```bash
# Scale image-generator to 5 replicas
docker-compose up -d --scale image-generator=5
```

**How it works:**
- NATS queue groups ensure only one replica processes each message
- Load automatically distributed across replicas
- No coordination needed between replicas

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: image-generator
spec:
  replicas: 3
  selector:
    matchLabels:
      app: image-generator
  template:
    spec:
      containers:
      - name: image-generator
        image: creative-campaign/image-generator:latest
        env:
        - name: NATS_URL
          value: "nats://nats:4222"
```

---

## Further Reading

- [Architecture Overview](architecture.md) - System design and data flow
- [Why Microservices?](why-microservices.md) - Architectural trade-offs
- [Schemas Reference](schemas.md) - API models and NATS contracts
