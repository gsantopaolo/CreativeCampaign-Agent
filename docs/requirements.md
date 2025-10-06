Perfect—locking in your stack and choices. Below is the **updated requirements analysis** that reflects: Python, **FastAPI** (+Pydantic), **Streamlit** UI, **NATS** bus, **MongoDB**, **MinIO/S3 (via boto3)**, **OpenAI-compatible image provider + secondary adapter**, **BrandComposer** as a separate service, **pluggable alert sinks**, **human-in-the-loop approvals & revisions**, **DLQ + Guardian**, **Grafana/Prometheus/Loki**, **Langtrace**, localization, and richer targeting (age + interests).

If anything feels off, tell me and I’ll tune it.

---

# Requirements Analysis — Rev A (with your specs)

## 1) Scope & objectives

Build a local-but-cloud-ready **creative automation pipeline** for social ad assets that:

* Ingests a **campaign brief** (≥2 products, region, audience, **age**, **interest text**, copy in EN + optional DE/FR/IT).
* Reuses existing assets from **S3-compatible storage** (MinIO/AWS). If missing, **generates** via a pluggable **ImageProvider**.
* Produces **≥3 aspect ratios** (1:1, 9:16, 16:9), overlays copy, and **optionally** applies **brand composition** (logo/colors) in a **separate service** so original generations stay untouched.
* Persists metadata in **MongoDB** (via Pydantic models in FastAPI).
* Orchestrates via **NATS** with **DLQ + Guardian** and **pluggable alert sinks** (email/SMS/webhook/NATS→UI).
* Provides a **Streamlit** UI for submission, preview, approval, and revision.
* Ships **observability** (Prometheus metrics, Loki logs, Grafana dashboards) and **Langtrace** tracing.
* Stores all outputs in **MinIO/S3** (no local outputs required).

## 2) Core components

1. **Streamlit UI**

   * Create/edit briefs; choose localization; set logo placement (top/bottom/left/right corners); approve/reject with feedback.
   * Subscribes to NATS (e.g., `alerts.ui`) to display live alerts.

2. **FastAPI Backend**

   * Pydantic models for all contracts.
   * Endpoints for brief CRUD, variant listing, approval/revision actions, health/metrics.
   * Integrates with **MongoDB** (official FastAPI integration guidance) and **boto3** for S3.

3. **Orchestrator/Worker (NATS consumers)**

   * Steps: ingest → asset lookup → image generation → brand composition → copy overlay → persist → notify.
   * Revision policy: **keep seed on first revision**, randomize on subsequent revisions.

4. **BrandComposer (separate service)**

   * Picks images from S3; writes a **new** branded variant (suffix `*_branded.*`) without altering originals.
   * High-DPI/alpha handling, safe margins, color accents.
   * Logo placement based on user selection from UI.

5. **Alert Service (pluggable sinks)**

   * Interface-based plugin loader (email, SMS, webhook, NATS).
   * Configurable routing rules by event type (READY_FOR_REVIEW, RUN_FAILED, QUOTA_ISSUE, etc.).

6. **Guardian (DLQ listener)**

   * Subscribes `dlq.creative.*`, enriches context, sends notifications via configured sinks.

7. **Storage: MinIO/S3 via boto3**

   * `endpoint_url`, region, keys, bucket from env; compatible with AWS & other S3 vendors.

8. **MongoDB**

   * Collections: `campaigns`, `variants`, `runs`, `events`.
   * Indexes for `campaign_id`, `product_id`, `aspect_ratio`, `status`, timestamps.

9. **Observability**

   * **Prometheus** metrics (FastAPI + worker + BrandComposer).
   * **Loki** logs (structured, with correlation ids and 🎯 concise emojis in messages).
   * **Grafana** dashboards.
   * **Langtrace** via API key for tracing LLM calls.

## 3) Data contracts (Pydantic)

### 3.1 CampaignBrief

```python
class BrandCompliance(BaseModel):
    primary_color: str | None = None
    logo_s3_uri: str | None = None
    banned_words_en: list[str] = []
    banned_words_de: list[str] = []
    banned_words_fr: list[str] = []
    banned_words_it: list[str] = []
    legal_guidelines: str | None = None  # free text or markdown

class AudienceTargeting(BaseModel):
    region: str
    audience: str  # e.g., "Young professionals"
    age_min: int | None = None
    age_max: int | None = None
    interests_text: str | None = None  # e.g., "women interested in beauty"

class ProductRef(BaseModel):
    id: str
    name: str

class OutputSpec(BaseModel):
    aspect_ratios: list[str] = ["1x1", "9x16", "16x9"]
    format: Literal["png", "jpeg"] = "png"
    s3_prefix: str  # e.g., "outputs/"

class Localization(BaseModel):
    message_en: str
    message_de: str | None = None
    message_fr: str | None = None
    message_it: str | None = None

class BrandPlacement(BaseModel):
    logo_position: Literal[
        "top_left","top_right","bottom_left","bottom_right"
    ] = "bottom_right"
    overlay_text_position: Literal["top","center","bottom"] = "bottom"

class CampaignBrief(BaseModel):
    campaign_id: str
    products: list[ProductRef]  # ≥ 2 enforced in validator
    audience: AudienceTargeting
    localization: Localization
    brand: BrandCompliance | None = None
    placement: BrandPlacement = BrandPlacement()
    output: OutputSpec
```

### 3.2 Variant & Run

```python
class Variant(BaseModel):
    variant_id: str
    campaign_id: str
    product_id: str
    aspect_ratio: str
    revision: int = 1
    status: Literal["awaiting_approval","approved","rejected","error"]
    source: Literal["reused","generated","generated_branded"]
    prompt: str | None = None
    seed: int | None = None
    s3_uri: str
    s3_uri_branded: str | None = None
    feedback_history: list[str] = []
    created_at: datetime
    updated_at: datetime

class RunEvent(BaseModel):
    event_id: str
    campaign_id: str
    step: str
    level: Literal["INFO","WARN","ERROR"]
    message: str
    details: dict[str, Any] | None = None
    ts: datetime
```

## 4) Message bus (NATS) subjects & retries

* **Primary**

  * `briefs.ingested`
  * `creative.generate.request` / `.progress` / `.done`
  * `creative.brand.compose.request` / `.done`
  * `creative.overlay.request` / `.done`
  * `creative.ready_for_review`
  * `creative.revision.requested`
  * `alerts.*` (fan-out to sinks)
* **DLQ**

  * `dlq.creative.generate`
  * `dlq.creative.brand.compose`
  * `dlq.creative.overlay`
* **Policy**: 3 retries, exponential backoff; on failure, publish to DLQ; **Guardian** notifies sinks.

## 5) Image providers

* **ImageProvider interface** with adapters:

  1. **OpenAI-compatible** (uses OpenAI SDK semantics; `base_url`, `api_key`, `model`).
  2. **Non-OpenAI provider** (custom API or local Diffusers).
* Config chooses provider; both return a common result (`s3_uri`, `prompt`, `seed`, metadata).

## 6) Processing pipeline (happy path)

1. UI submits brief → FastAPI validates/saves → publish `briefs.ingested`.
2. Worker checks S3 for product assets; if missing, **generate** via provider → upload originals.
3. Publish `creative.brand.compose.request` → BrandComposer creates `*_branded.*` assets with logo/colors.
4. Publish `creative.overlay.request` → overlay localized copy (default EN; fallback if missing).
5. Persist **Variant** docs; publish `creative.ready_for_review`.
6. UI shows variants → human **Approve** or **Request changes**:

   * Approve → mark `approved` and alert stakeholders.
   * Request changes → publish `creative.revision.requested` with feedback; **keep seed** on first revision, randomize thereafter; create `revision += 1`; repeat steps 2–5.

### Compliance checks

* Scan final texts against **banned words** (per locale); flag violations (alert + UI badges).
* Optional “contrast/safe-margin” heuristics for readability (warning only in POC).

## 7) Configuration (env)

```
MONGO_URI=mongodb+srv://...
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

## 8) Observability

* **Metrics**: request durations, queue lag, step timings, success/error rates, retries, DLQ counts; FastAPI exposes `/metrics`.
* **Logs**: JSON to stdout → Promtail → **Loki**; include `campaign_id`, `variant_id`, `run_id`, `corr_id` + short emojis (e.g., ✅, ⚠️, ❌).
* **Dashboards**: Grafana panels for throughput, latency, error budget, DLQ trend.
* **Tracing**: Langtrace wraps image calls and major steps; `corr_id` propagates.

## 9) Acceptance criteria

* Briefs with **≥2 products** produce **1:1, 9:16, 16:9** variants per product.
* Originals go to S3; **BrandComposer** writes **separate** branded outputs; copy is overlaid as specified.
* UI supports approval & revision loop; first revision keeps seed, later randomizes.
* Pluggable alert sinks work (at least **email** + **NATS→UI** route).
* DLQ + Guardian notify on hard failures.
* Mongo holds briefs, variants, runs/events with the indexes listed.
* Metrics/logs/traces visible (Prometheus/Grafana/Loki/Langtrace).
* All outputs stored in **MinIO/S3**; human-readable filenames:
  `outputs/<campaign>/<product>/<aspect>/<campaign>_<product>_<aspect>_v<rev>.png`.

## 10) Roadmap (POC-friendly)

* **Day 1–2**: Schemas (Pydantic), FastAPI skeleton, Mongo integration, S3 client, NATS wiring, Streamlit MVP (brief submit + gallery).
* **Day 3**: ImageProvider (OpenAI-compatible) + Custom adapter stub, generation worker, overlay, storage.
* **Day 4**: BrandComposer service, approvals + revisions, DLQ + Guardian, alert plugins (email + NATS).
* **Day 5**: Compliance checks, metrics/logs/traces, dashboards, README + demo script.

---

## Open items (quick picks and I’ll assume defaults)

1. **Email/SMS providers** for alert sinks (SMTP host? SMS vendor?) *(Default: SMTP + console SMS stub).*
2. **Which non-OpenAI image provider** to prewire? *(Default: Stability/SDXL via custom adapter stub).*
3. **Logo format**: will you supply PNG/SVG in S3? *(Default: PNG in `brand/logo.png` with alpha).*
4. **Promtail path** (for Loki): containerized or host-level? *(Default: containerized promtail scraping app logs).*
5. **Compliance failure policy**: **block approval** or **warn only**? *(Default: warn, allow override in UI.)*

I