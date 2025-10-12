# Creative Campaign Agent - Message Flow Chain

This document describes the complete event-driven message flow through all services in the Creative Campaign Agent system.

## Message Flow Diagram

```
API → Context Enricher → Creative Generator → Image Generator → Brand Composer → Text Overlay → Web UI
```

## Detailed Message Chain

### 1. **API Service** → Context Enricher
**Event Published:** `context.enrich.request`  
**Proto Message:** `ContextEnrichRequest`  
**Stream:** `context-request-stream`  
**Trigger:** User creates a campaign via API  
**Fields:**
- `campaign_id`: Campaign identifier
- `locale`: Target locale (en, de, fr, it)
- `region`: Geographic region
- `audience`: Target audience description
- `age_min`, `age_max`: Age range
- `product_names`: List of products
- `correlation_id`: Request tracking ID
- `timestamp`: Event timestamp

---

### 2. **Context Enricher** → Creative Generator
**Event Published:** `context.enrich.ready`  
**Proto Message:** `ContextEnrichReady`  
**Stream:** `context-ready-stream`  
**Trigger:** Context enrichment completed (market insights generated)  
**Fields:**
- `campaign_id`: Campaign identifier
- `locale`: Target locale
- `context_pack`: Enriched context with:
  - `culture_notes`: Cultural sensitivities
  - `tone`: Messaging tone
  - `dos`: List of recommended practices
  - `donts`: List of things to avoid
  - `banned_words`: Words to exclude
  - `legal_guidelines`: Regulatory notes
- `correlation_id`: Request tracking ID
- `timestamp`: Event timestamp

**LLM Used:** GPT-4o-mini with **Structured Outputs**  
**Pydantic Model:** `MarketInsightsResponse`

---

### 3. **Creative Generator** → Image Generator
**Event Published:** `creative.generate.done`  
**Proto Message:** `CreativeGenerateDone`  
**Stream:** `creative-generate-done-stream`  
**Trigger:** Creative content generated (headline, description, CTA)  
**Fields:**
- `campaign_id`: Campaign identifier
- `locale`: Target locale
- `product_id`: Product identifier (optional)
- `revision`: Revision number
- `candidates`: List of generated candidates (optional)
- `correlation_id`: Request tracking ID
- `timestamp`: Event timestamp

**LLM Used:** GPT-4o-mini with **Structured Outputs**  
**Pydantic Model:** `CampaignContentResponse`  
**Data Stored in MongoDB:** `creatives` collection with structured fields:
- `headline`: Campaign headline
- `description`: Campaign description
- `call_to_action`: CTA text
- `visual_elements`: List of visual elements

---

### 4. **Image Generator** → Brand Composer
**Event Published:** `image.generated`  
**Proto Message:** `ImageGenerated`  
**Stream:** `image-generate-stream`  
**Trigger:** AI-generated image created via DALL-E  
**Fields:**
- `campaign_id`: Campaign identifier
- `locale`: Target locale
- `product_id`: Product identifier
- `image_url`: Public URL to generated image
- `s3_uri`: S3 storage URI
- `prompt_used`: DALL-E prompt
- `status`: Generation status
- `error_message`: Error details (if failed)
- `correlation_id`: Request tracking ID
- `generated_at`: Generation timestamp

**LLM Used:** DALL-E-3 for image generation

---

### 5. **Brand Composer** → Text Overlay
**Event Published:** `brand.composed`  
**Proto Message:** `BrandComposeDone`  
**Stream:** `brand-compose-stream`  
**Trigger:** Brand logo added to generated image  
**Fields:**
- `campaign_id`: Campaign identifier
- `locale`: Target locale
- `branded_image_s3_uri`: S3 URI of branded image
- `branded_image_url`: Public URL of branded image
- `correlation_id`: Request tracking ID
- `timestamp`: Event timestamp

**LLM Used:** GPT-4o-mini with **Structured Outputs** (vision)  
**Pydantic Model:** `LogoPlacementResponse`  
**Purpose:** Analyze image to find optimal logo placement

---

### 6. **Text Overlay** → Final Output
**Event Published:** `text.overlaid`  
**Proto Message:** `TextOverlaid`  
**Stream:** `text-overlay-stream`  
**Trigger:** Campaign headline overlaid on branded image  
**Fields:**
- `campaign_id`: Campaign identifier
- `locale`: Target locale
- `final_image_s3_uri`: S3 URI of final image
- `final_image_url`: Public URL of final image

**LLM Used:** GPT-4o-mini with **Structured Outputs** (vision)  
**Pydantic Model:** `TextPlacementResponse`  
**Purpose:** Analyze image to find optimal text placement

**Final Output:** Complete creative asset ready for use!

---

## NATS JetStream Configuration

### Streams Created:
1. `context-request-stream` → Subject: `context.enrich.request`
2. `context-ready-stream` → Subject: `context.enrich.ready`
3. `creative-generate-done-stream` → Subject: `creative.generate.done`
4. `image-generate-stream` → Subject: `image.generated`
5. `brand-compose-stream` → Subject: `brand.composed`
6. `text-overlay-stream` → Subject: `text.overlaid`

### Message Guarantees:
- **At-least-once delivery** with acknowledgments
- **Retry logic** with exponential backoff
- **Dead letter queue** after max retries
- **Message persistence** in JetStream

---

## Structured Outputs Implementation

All LLM services use **OpenAI JSON mode** with **Pydantic validation**:

```python
# Pattern used across all services:
response = await openai_client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[...],
    response_format={"type": "json_object"}
)

json_response = json.loads(response.choices[0].message.content)
validated_data = PydanticModel(**json_response)
```

### Benefits:
- ✅ **No parsing errors** - JSON structure guaranteed
- ✅ **Type safety** - Pydantic validates all fields
- ✅ **Required fields** - LLM must provide all data
- ✅ **Clear contracts** - Explicit schemas in prompts

---

## Data Storage

### MongoDB Collections:
1. **campaigns** - Campaign metadata and configuration
2. **creatives** - Generated creative content (structured)
3. **context_packs** - Enriched market insights

### S3/MinIO Storage:
1. **campaigns/{campaign_id}/{locale}/generated/** - AI-generated images
2. **campaigns/{campaign_id}/{locale}/branded/** - Logo-branded images
3. **campaigns/{campaign_id}/{locale}/final/** - Final text-overlaid images

---

## Error Handling

Each service implements:
- ✅ **Graceful degradation** with fallback values
- ✅ **Message NAK** for retries on failure
- ✅ **Detailed logging** with correlation IDs
- ✅ **Health checks** via readiness probes
- ✅ **Circuit breakers** for external API calls

---

## Monitoring & Observability

- **Readiness Probes:** HTTP endpoint `/healthz` on port 8080
- **Correlation IDs:** Track requests across services
- **Structured Logging:** JSON logs with timestamps
- **NATS Metrics:** Stream lag, message rates, ack rates
