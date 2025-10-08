# API & Schema Reference

This reference collates the **FastAPI REST surface**, **NATS message contracts (JSON Schemas)**, **MongoDB collection schemas & indexes**, and the **runtime configuration schema** used by the creative automation POC.

> Conventions
>
> * All IDs are lowercase kebab- or snake-case strings unless stated.
> * Timestamps are ISO 8601 with `Z` (UTC) unless stated.
> * S3 URIs use the form `s3://<bucket>/<key>`; when MinIO is used, URIs are still `s3://`.
> * Locales supported: `en`, `de`, `fr`, `it`.
> * Each NATS message includes an envelope with correlation and dedup fields (see **1.4 Message Envelope**).

---

## 1. FastAPI (REST) — OpenAPI surface

The full OpenAPI document is served at:

* `GET /openapi.json`
* `GET /docs` (Swagger UI)

Below is the *canonical* endpoint list with request/response models (Pydantic). Status codes shown are the primary ones; error responses use the **Error** model.

### 1.1 Endpoints

#### POST `/campaigns`

Create or update a campaign brief.

* **Body:** `CampaignBrief`
* **200 OK:** `{ campaign_id: string, revision: integer }`
* **400/422:** `Error`
* **Side effects:** persists brief; publishes `briefs.ingested`.

#### GET `/campaigns/{campaign_id}`

Fetch a campaign brief + summary.

* **200 OK:** `CampaignBrief + summary`
* **404:** `Error`

#### GET `/campaigns`

List campaigns with pagination.

* **Query:** `page`, `page_size`, optional `status`
* **200 OK:** `{ items: CampaignSummary[], next_page: string|null }`

#### GET `/campaigns/{campaign_id}/status`

Get campaign processing status and progress.

* **200 OK:** `StatusResponse` with progress breakdown by locale
* **404:** `Error`

#### GET `/variants`

List variants for a campaign (filterable).

* **Query:** `campaign_id` (req), `product_id?`, `locale?`, `status?`, `best?`
* **200 OK:** `{ items: Variant[] }`

#### POST `/campaigns/{campaign_id}/approve`

Approve the current best for a product/locale.

* **Body:** `{ product_id: string, locale: Locale, revision: int }`
* **200 OK:** `{ ok: true }`
* **404/409:** `Error`
* **Side effects:** publishes `creative.approved`.

#### POST `/campaigns/{campaign_id}/revision`

Request changes for a product/locale (free-text feedback).

* **Body:** `{ product_id: string, locale: Locale, from_revision: int, feedback: string }`
* **200 OK:** `{ ok: true }`
* **Side effects:** publishes `creative.revision.requested`.

#### GET `/healthz`

* **200 OK:** `{ status: "ok" }`

#### GET `/metrics`

* Prometheus exposition format.

### 1.2 Pydantic models (REST)

#### `CampaignBrief`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "CampaignBrief",
  "type": "object",
  "required": ["campaign_id", "products", "target_locales", "audience", "localization", "output"],
  "properties": {
    "campaign_id": { "type": "string", "minLength": 1 },
    "products": {
      "type": "array",
      "minItems": 2,
      "items": {
        "type": "object",
        "required": ["id", "name"],
        "properties": {
          "id": { "type": "string" },
          "name": { "type": "string" },
          "description": { "type": "string" }
        }
      }
    },
    "target_locales": { "type": "array", "items": { "enum": ["en","de","fr","it"] }, "minItems": 1 },
    "audience": {
      "type": "object",
      "required": ["region", "audience"],
      "properties": {
        "region": { "type": "string" },
        "audience": { "type": "string" },
        "age_min": { "type": "integer", "minimum": 0 },
        "age_max": { "type": "integer", "minimum": 0 },
        "interests_text": { "type": "string" }
      }
    },
    "localization": {
      "type": "object",
      "required": ["message_en"],
      "properties": {
        "message_en": { "type": "string" },
        "message_de": { "type": "string" },
        "message_fr": { "type": "string" },
        "message_it": { "type": "string" }
      }
    },
    "brand": {
      "type": "object",
      "properties": {
        "primary_color": { "type": "string", "pattern": "^#([0-9A-Fa-f]{6})$" },
        "logo_s3_uri": { "type": "string" },
        "banned_words_en": { "type": "array", "items": { "type": "string" } },
        "banned_words_de": { "type": "array", "items": { "type": "string" } },
        "banned_words_fr": { "type": "array", "items": { "type": "string" } },
        "banned_words_it": { "type": "array", "items": { "type": "string" } },
        "legal_guidelines": { "type": "string" }
      }
    },
    "placement": {
      "type": "object",
      "properties": {
        "logo_position": { "enum": ["top_left","top_right","bottom_left","bottom_right"] },
        "overlay_text_position": { "enum": ["top","center","bottom"] }
      },
      "additionalProperties": false
    },
    "output": {
      "type": "object",
      "required": ["aspect_ratios", "format", "s3_prefix"],
      "properties": {
        "aspect_ratios": { "type": "array", "items": { "enum": ["1x1","9x16","16x9"] }, "minItems": 3, "uniqueItems": true },
        "format": { "enum": ["png","jpeg"] },
        "s3_prefix": { "type": "string" }
      }
    }
  },
  "additionalProperties": false
}
```

#### `Variant` (REST shape)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Variant",
  "type": "object",
  "required": ["variant_id","campaign_id","product_id","locale","revision","status"],
  "properties": {
    "variant_id": { "type": "string" },
    "campaign_id": { "type": "string" },
    "product_id": { "type": "string" },
    "locale": { "enum": ["en","de","fr","it"] },
    "aspect_ratio": { "enum": ["1x1","9x16","16x9"] },
    "revision": { "type": "integer", "minimum": 1 },
    "status": { "enum": ["awaiting_approval","approved","rejected","error"] },
    "source": { "enum": ["reused","generated","generated_branded"] },
    "prompt": { "type": "string" },
    "seed": { "type": "integer" },
    "s3_raw": { "type": "string" },
    "s3_branded": { "type": "string" },
    "final_uris": { "type": "object", "additionalProperties": { "type": "string" } },
    "copy": { "type": "string" },
    "scores": { "type": "object", "additionalProperties": true },
    "best": { "type": "boolean" },
    "compliance": { "type": "object", "additionalProperties": true },
    "feedback_history": { "type": "array", "items": { "type": "string" } },
    "created_at": { "type": "string", "format": "date-time" },
    "updated_at": { "type": "string", "format": "date-time" }
  }
}
```

#### `Error`

```json
{ "code": "string", "message": "string" }
```

### 1.3 Common types

* **Locale**: `en|de|fr|it`
* **AspectRatio**: `1x1|9x16|16x9`

### 1.4 Message Envelope (headers or body fields)

Every NATS payload includes or derives:

```json
{ "corr_id": "uuid", "msg_id": "sha256-of-nature", "campaign_id": "...", "locale": "en", "product_id": "p01", "revision": 1, "ts": "2025-01-01T00:00:00Z" }
```

---

## 2. NATS message contracts — JSON Schemas

> Draft-07 JSON Schemas. Unless noted, all messages require the **Message Envelope** fields.

### 2.1 Context enrichment

**`context.enrich.request`**

```json
{ "campaign_id": "string", "locale": "en", "revision": 1 }
```

**`ContextPack`**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ContextPack",
  "type": "object",
  "required": ["culture_notes","tone","dos","donts","legal","banned"],
  "properties": {
    "culture_notes": { "type": "string" },
    "tone": { "type": "string" },
    "dos": { "type": "array", "items": { "type": "string" } },
    "donts": { "type": "array", "items": { "type": "string" } },
    "legal": { "type": "string" },
    "banned": {
      "type": "object",
      "additionalProperties": { "type": "array", "items": { "type": "string" } }
    }
  }
}
```

**`context.enrich.ready`**

```json
{ "campaign_id": "string", "locale": "en", "revision": 1, "context_pack": { "$ref": "ContextPack#" } }
```

### 2.2 Image generation

**`creative.generate.request`**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "CreativeGenerateRequest",
  "type": "object",
  "required": ["campaign_id","product_id","locale","revision","n","prompt_base","context_pack","provider"],
  "properties": {
    "campaign_id": { "type": "string" },
    "product_id": { "type": "string" },
    "locale": { "enum": ["en","de","fr","it"] },
    "revision": { "type": "integer", "minimum": 1 },
    "n": { "type": "integer", "minimum": 1, "maximum": 8 },
    "prompt_base": { "type": "string" },
    "context_pack": { "$ref": "ContextPack#" },
    "provider": { "type": "object", "required": ["type","model"], "properties": { "type": { "enum": ["openai","custom"] }, "model": { "type": "string" }, "base_url": { "type": "string" } } },
    "seed_policy": { "enum": ["keep","randomize"], "default": "keep" }
  }
}
```

**`creative.generate.done`**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "CreativeGenerateDone",
  "type": "object",
  "required": ["campaign_id","product_id","locale","revision","candidates"],
  "properties": {
    "campaign_id": { "type": "string" },
    "product_id": { "type": "string" },
    "locale": { "enum": ["en","de","fr","it"] },
    "revision": { "type": "integer" },
    "candidates": { "type": "array", "minItems": 1, "items": { "type": "object", "required": ["s3_uri","seed"], "properties": { "s3_uri": { "type": "string" }, "seed": { "type": "integer" } } } }
  }
}
```

### 2.3 Brand composition

**`creative.brand.compose.request`**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "BrandComposeRequest",
  "type": "object",
  "required": ["campaign_id","product_id","locale","revision","input_s3_uris","logo","position"],
  "properties": {
    "campaign_id": { "type": "string" },
    "product_id": { "type": "string" },
    "locale": { "enum": ["en","de","fr","it"] },
    "revision": { "type": "integer" },
    "input_s3_uris": { "type": "array", "items": { "type": "string" } },
    "logo": { "type": "string" },
    "position": { "enum": ["top_left","top_right","bottom_left","bottom_right"] },
    "primary_color": { "type": "string" }
  }
}
```

**`creative.brand.compose.done`**

```json
{ "campaign_id": "string", "product_id": "string", "locale": "en", "revision": 1, "outputs": ["s3://.../a_branded.png"] }
```

### 2.4 Copy generation & compliance

**`creative.copy.generate.request`**

```json
{
  "$schema":"http://json-schema.org/draft-07/schema#",
  "title":"CopyGenerateRequest",
  "type":"object",
  "required":["campaign_id","product_id","locale","revision","image","context_pack","length"],
  "properties":{
    "campaign_id":{"type":"string"},
    "product_id":{"type":"string"},
    "locale":{"enum":["en","de","fr","it"]},
    "revision":{"type":"integer"},
    "image":{"type":"string"},
    "context_pack":{"$ref":"ContextPack#"},
    "length":{"enum":["short","medium"]}
  }
}
```

**`creative.copy.generate.done`**

```json
{ "campaign_id":"string", "product_id":"string", "locale":"en", "revision":1, "text":"string" }
```

**`compliance.checked`**

```json
{ "campaign_id":"string", "product_id":"string", "locale":"en", "revision":1, "status":"OK|WARN", "reasons":["..."] }
```

### 2.5 Overlay & selection

**`creative.overlay.request`**

```json
{
  "$schema":"http://json-schema.org/draft-07/schema#",
  "title":"OverlayRequest",
  "type":"object",
  "required":["campaign_id","product_id","locale","revision","image","text","aspects","overlay"],
  "properties":{
    "campaign_id":{"type":"string"},
    "product_id":{"type":"string"},
    "locale":{"enum":["en","de","fr","it"]},
    "revision":{"type":"integer"},
    "image":{"type":"string"},
    "text":{"type":"string"},
    "aspects":{"type":"array","items":{"enum":["1x1","9x16","16x9"]}},
    "overlay":{"type":"object","properties":{"text_position":{"enum":["top","center","bottom"]}}}
  }
}
```

**`creative.overlay.done`**

```json
{ "campaign_id":"string","product_id":"string","locale":"en","revision":1, "final": { "1x1":"s3://...","9x16":"s3://...","16x9":"s3://..." } }
```

**`creative.ready_for_review`**

```json
{
  "$schema":"http://json-schema.org/draft-07/schema#",
  "title":"ReadyForReview",
  "type":"object",
  "required":["campaign_id","product_id","locale","revision","best"],
  "properties":{
    "campaign_id":{"type":"string"},
    "product_id":{"type":"string"},
    "locale":{"enum":["en","de","fr","it"]},
    "revision":{"type":"integer"},
    "best":{"type":"object","additionalProperties":true},
    "alternates":{"type":"array","items":{"type":"object"}}
  }
}
```

### 2.6 Approvals & DLQ

**`creative.revision.requested`**

```json
{ "campaign_id":"string","product_id":"string","locale":"en","from_revision":1,"feedback":"string" }
```

**`creative.approved`**

```json
{ "campaign_id":"string","product_id":"string","locale":"en","revision":1 }
```

**`dlq.creative.*`** (generic form)

```json
{ "campaign_id":"string","product_id":"string","locale":"en","revision":1, "error":"string", "last_payload":{ "type":"object" } }
```

### 2.7 Alerts (pluggable sinks)

**`alert.event`** (internal bus format routed by alert-dispatcher)

```json
{
  "$schema":"http://json-schema.org/draft-07/schema#",
  "title":"AlertEvent",
  "type":"object",
  "required":["severity","code","campaign_id","detail"],
  "properties":{
    "severity":{"enum":["INFO","WARN","ERROR"]},
    "code":{"enum":["READY_FOR_REVIEW","RUN_FAILED","QUOTA_ISSUE","COMPLIANCE_BANNED_WORD","DELIVERY_FAILED"]},
    "campaign_id":{"type":"string"},
    "locale":{"enum":["en","de","fr","it"]},
    "product_id":{"type":"string"},
    "detail":{"type":"string"},
    "routing":{"type":"array","items":{"type":"string"}}
  }
}
```

---

## 3. MongoDB collections & indexes

### 3.1 `campaigns`

* **Key fields:** `campaign_id` (unique), `revision`, `products[]`, `target_locales[]`, `audience`, `localization`, `brand`, `placement`, `output`, `created_at`, `updated_at`.
* **Indexes:** `{ campaign_id: 1 } (unique)`
* **Example:**

```json
{
  "campaign_id": "fall_2025_promo",
  "revision": 1,
  "products": [{"id":"p01","name":"Serum X","description":"Vit C"},{"id":"p02","name":"Cream Y"}],
  "target_locales": ["en","de","fr"],
  "audience": {"region":"CH","audience":"Young professionals","age_min":25,"age_max":45,"interests_text":"women interested in beauty"},
  "localization": {"message_en":"Shine daily"},
  "brand": {"primary_color":"#FF3355","logo_s3_uri":"s3://brand/logo.png"},
  "placement": {"logo_position":"bottom_right","overlay_text_position":"bottom"},
  "output": {"aspect_ratios":["1x1","9x16","16x9"],"format":"png","s3_prefix":"outputs/"},
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

### 3.2 `variants`

* One doc per **candidate/final** asset per product×locale×revision.
* **Key fields:** `variant_id` (uuid), `campaign_id`, `product_id`, `locale`, `aspect_ratio`, `revision`, `status`, `source`, `prompt`, `seed`, `s3_raw`, `s3_branded`, `final_uris{}`, `copy`, `scores{}`, `best`, `compliance{}`, `feedback_history[]`, timestamps.
* **Indexes:** `{ campaign_id:1, product_id:1, locale:1, status:1 }`, `{ campaign_id:1, best:1 }`.
* **Example:**

```json
{
  "variant_id": "v-123",
  "campaign_id": "fall_2025_promo",
  "product_id": "p01",
  "locale": "de",
  "aspect_ratio": "1x1",
  "revision": 1,
  "status": "awaiting_approval",
  "source": "generated_branded",
  "prompt": "beauty promo ...",
  "seed": 12345,
  "s3_raw": "s3://.../raw/a.png",
  "s3_branded": "s3://.../branded/a_branded.png",
  "final_uris": {"1x1":"s3://.../final/1x1/file.png","9x16":"s3://.../final/9x16/file.png","16x9":"s3://.../final/16x9/file.png"},
  "copy": "Strahlend jeden Tag.",
  "scores": {"llm_fit":0.82,"brand":0.91,"compliance":1.0,"total":0.88},
  "best": true,
  "compliance": {"status":"OK","reasons":[]},
  "feedback_history": ["lighter background"],
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

### 3.3 `runs`

* One doc per orchestration run; aggregates timings and counts.
* **Indexes:** `{ campaign_id:1, started_at: -1 }`.

### 3.4 `events`

* Append-only log of step-level events, alerts, and DLQ.
* **Indexes:** `{ campaign_id:1, ts:-1 }`.

---

## 4. Runtime configuration schema

Provide via `.env` and `config.yaml` (12-factor). Pydantic/Settings can validate.

### 4.1 Environment variables

```
MONGO_URI=...
MONGO_DB=creative_automation

S3_ENDPOINT_URL=http://minio:9000
S3_REGION=us-east-1
S3_ACCESS_KEY_ID=...
S3_SECRET_ACCESS_KEY=...
S3_BUCKET=creative-assets

NATS_URL=nats://user:pass@nats:4222

IMAGE_PROVIDER=openai|custom
OPENAI_API_KEY=...
OPENAI_BASE_URL=https://api.openai.com/v1
IMAGE_MODEL=dall-e-3|sdxl|...

LANGTRACE_API_KEY=...
PROMETHEUS_PORT=9100
LOKI_URL=http://loki:3100
```

### 4.2 `config.yaml` (validated at startup)

```yaml
mongo:
  uri: ${MONGO_URI}
  db: ${MONGO_DB}

s3:
  endpoint_url: ${S3_ENDPOINT_URL}
  region: ${S3_REGION}
  access_key: ${S3_ACCESS_KEY_ID}
  secret_key: ${S3_SECRET_ACCESS_KEY}
  bucket: ${S3_BUCKET}

nats:
  url: ${NATS_URL}
  queue_prefix: q.
  retries: 3
  backoff_ms: [500, 2000, 5000]
  dlq_prefix: dlq.creative.

providers:
  image:
    type: ${IMAGE_PROVIDER}
    model: ${IMAGE_MODEL}
    base_url: ${OPENAI_BASE_URL}
    api_key: ${OPENAI_API_KEY}

alerts:
  sinks:
    - name: email_default
      type: plugins.alerts.email.EmailSink
      config:
        smtp_server: smtp.example.com
        from: noreply@example.com
        to: [ops@example.com]
    - name: bus_streamlit
      type: plugins.alerts.nats.NATSSink
      config:
        subject: alerts.ui
  routing:
    - on: [RUN_FAILED, QUOTA_ISSUE]
      sinks: [email_default, bus_streamlit]
    - on: [READY_FOR_REVIEW]
      sinks: [bus_streamlit]
```

### 4.3 Plugin loading (alerts)

* Python entry-point or module path in config. Each sink implements:

```python
class AlertSink:
    def send(self, event: dict) -> None: ...
```

---

## 5. NATS subjects (publisher → consumer)

* `briefs.ingested` — api-gateway → orchestration-router
* `context.enrich.request` → context-enricher
* `context.enrich.ready` — context-enricher → orchestration-router
* `creative.generate.request` — router/approval-handler → image-generator
* `creative.generate.done` — image-generator → orchestration-router
* `creative.brand.compose.request` → brand-composer
* `creative.brand.compose.done` — brand-composer → orchestration-router
* `creative.copy.generate.request` → copy-generator
* `creative.copy.generate.done` — copy-generator → compliance-checker
* `compliance.checked` — compliance-checker → orchestration-router
* `creative.overlay.request` → overlay-composer
* `creative.overlay.done` — overlay-composer → scorer-selector
* `creative.ready_for_review` — scorer-selector → ui-webapp
* `creative.revision.requested` — api-gateway → approval-handler
* `creative.approved` — api-gateway → approval-handler
* `alerts.ui`, `alerts.ops` — alert-dispatcher → UI/external
* `dlq.creative.*` — any worker → guardian-dlq

---

## 6. Validation & idempotency

* JetStream durable consumers, queue groups (`q.<service>`), `maxDeliver=3`, exponential backoff.
* Message de-dup via `msg_id` header or body; recommended key: `sha256(campaign_id|locale|product_id|step|revision)`.
* All write handlers upsert on natural keys and keep immutable history via `revision` increments.

---

## 7. Examples & fixtures

* `examples/briefs/` — sample `CampaignBrief` JSONs.
* `examples/messages/` — valid message payloads for each subject.
* `examples/mongo/` — seed docs for `campaigns` and `variants`.

