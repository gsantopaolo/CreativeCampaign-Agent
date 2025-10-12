# CreativeCampaign-Agent
Agentic AI for social ads: brand-safe hero images &amp; layouts, generated, resized, localized, and region-customized at scale

---

## Design Philosophy: Production-Ready POC Using Proven Patterns

This POC demonstrates **not just coding ability, but architectural judgment and rapid deployment capability** expected of Principal/Staff Forward Deployed Engineers. Rather than building a toy demo from scratch, this implementation leverages **battle-tested enterprise patterns** to show how a senior engineer approaches customer deployments.

### Key Principles

✅ **Leverage, Don't Rebuild** - Reuses proven microservice patterns from [Sentinel-AI](samples/sentinel-AI)  
✅ **Production Thinking** - Shows scalability, reliability, and observability from day one  
✅ **Agentic Self-Evaluation** - Modern CrewAI agents with built-in quality control and compliance  
✅ **Right-Sized Architecture** - Microservices where it matters; simplicity where it doesn't  

### What Makes This "Production-Ready"

- **Event-Driven Architecture**: NATS JetStream for decoupled, scalable communication
- **Fault Tolerance**: DLQ, retries, health checks, graceful degradation
- **Observability**: Structured logging, metrics, distributed tracing ready
- **Agentic AI**: Self-evaluating agents that improve quality without manual intervention
- **Enterprise Integrations**: S3-compatible storage, MongoDB, multi-provider GenAI

> **For evaluators**: This represents how a 2-day customer POC would look at scale. See [`docs/simplified-alternative.md`](docs/simplified-alternative.md) for a minimal approach, and [`docs/why-microservices.md`](docs/why-microservices.md) for architectural trade-offs.

### Reusable Components from Prior Work

| Component | Source | Purpose |
|-----------|--------|---------|
| NATS JetStream patterns | [Sentinel-AI](samples/sentinel-AI) | Pub/sub, retries, DLQ, queue groups |
| FastAPI + MongoDB | [Sentinel-AI](samples/sentinel-AI) | REST API, persistence, health checks |
| Readiness probes | [Sentinel-AI](samples/sentinel-AI) | K8s-compatible health monitoring |
| Qdrant vector logic | [Sentinel-AI](samples/sentinel-AI) | Adapted for embedding-based search |
| Docker-compose infra | [Sentinel-AI](samples/sentinel-AI) | Multi-service orchestration |

> See [`docs/reused-patterns.md`](docs/reused-patterns.md) for detailed mapping of reused vs. net-new code.

---

# Creative Automation for Localized Social Ads (POC)

End-to-end pipeline that turns a **campaign brief** into **localized creatives** (images + copy) for multiple products and languages, with **brand composition**, **approvals & revisions**, **agentic quality control**, and **observability**. Built for the Adobe FDE take-home.

> Full details:
>
> * **Architecture & orchestration** → [`docs/architecture.md`](docs/architecture.md)
> * **Why this architecture?** → [`docs/why-microservices.md`](docs/why-microservices.md)
> * **Simplified alternative** → [`docs/simplified-alternative.md`](docs/simplified-alternative.md)
> * **API & Schema Reference** → [`docs/schemas.md`](docs/schemas.md)
> * **Reused patterns** → [`docs/reused-patterns.md`](docs/reused-patterns.md)

---

## TL;DR

* **Stack:** Python · **FastAPI** (REST + orchestration) · **Streamlit** (UI) · **NATS** (bus, JetStream) · **MongoDB** (metadata) · **MinIO/S3** (assets via `boto3`)
* **Architecture:** 6 core services + 2 supporting (simplified from 14 via agentic self-evaluation)
* **GenAI:** **CrewAI agents** for image/copy generation with built-in quality control & compliance
* **Providers:** OpenAI, Replicate, Stability AI, or custom adapters
* **Branding:** Separate **BrandComposer** service with **AI-powered logo placement** using GPT-4o-mini vision analysis
* **Localization:** Per-locale **Context Pack** → agentic generation → culturally-aware copy
* **Approvals:** Human-in-the-loop via Streamlit; first revision keeps seed, later randomizes
* **Reliability:** Retries + **DLQ** + **Guardian** for failure monitoring
* **Observability:** Structured logging, health checks, NATS monitoring (optional: Prometheus/Grafana)

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Docker & Docker Compose installed
- OpenAI API key ([get one here](https://platform.openai.com/api-keys))

### Step 1: Clone & Configure

```bash
# Clone the repository
git clone <repo-url>
cd CreativeCampaign-Agent

# Copy environment template
cp deployment/.env.example deployment/.env

# Edit and add your OPENAI_API_KEY
nano deployment/.env  # or use your preferred editor
```

### Step 2: Start All Services

```bash
cd deployment
docker-compose up -d
```

**Services starting:**
- API Gateway (FastAPI) - `http://localhost:8000`
- Web UI (Streamlit) - `http://localhost:8501`
- MongoDB - `localhost:27017`
- MinIO/S3 - `http://localhost:9000`
- NATS JetStream - `localhost:4222`
- 6 worker services (context, image, brand, text, overlay, guardian)

### Step 3: Access the UI

```bash
# Open in your browser
open http://localhost:8501

# Or visit manually
http://localhost:8501
```

### Step 4: Create Your First Campaign

1. Click **"➕ Create New Campaign"**
2. Fill in the form:
   - **Campaign ID**: `my_first_campaign`
   - **Products**: Add at least 2 products (e.g., "Serum X", "Cream Y")
   - **Locales**: Select EN, DE, FR, or IT (or all 4!)
   - **Logo**: Upload your logo or use the default
   - **Brand Color**: Pick your brand color
   - **Aspect Ratios**: Select all 4 (1x1, 4x5, 9x16, 16x9)
3. Click **"🚀 Launch Campaign"**
4. Watch the pipeline execute in real-time!

**Expected time:** 2-5 minutes per locale/product combination

---

## 📸 Example Input & Output

### Example Input (Campaign Brief)

```json
{
  "campaign_id": "fall_2025_promo",
  "products": [
    {
      "id": "p01",
      "name": "Vitamin C Serum",
      "description": "Brightening serum with 20% Vitamin C for radiant skin"
    },
    {
      "id": "p02",
      "name": "Hydration Cream",
      "description": "Deep moisturizing cream with hyaluronic acid"
    }
  ],
  "target_locales": ["en", "de", "fr", "it"],
  "audience": {
    "region": "DACH",
    "audience": "Young professionals interested in skincare",
    "age_min": 25,
    "age_max": 45
  },
  "brand": {
    "primary_color": "#FF3355",
    "logo_s3_uri": "s3://creative-assets/logos/brand-logo.png",
    "banned_words_en": ["miracle", "cure", "medical"],
    "legal_guidelines": "No medical claims. All statements must be verifiable."
  },
  "localization": {
    "message_en": "Shine every day with natural radiance",
    "message_de": "Strahle jeden Tag mit natürlicher Ausstrahlung",
    "message_fr": "Brillez chaque jour avec un éclat naturel",
    "message_it": "Splendi ogni giorno con luminosità naturale"
  },
  "output": {
    "aspect_ratios": ["1x1", "4x5", "9x16", "16x9"],
    "format": "png",
    "s3_prefix": "outputs/"
  }
}
```

### Example Output (Generated Assets)

**32 unique images generated:**
- 4 locales × 2 products × 4 aspect ratios = **32 final assets**

**Each image includes:**
- ✅ AI-generated product visualization (DALL-E 3)
- ✅ AI-optimized logo placement in upper half (GPT-4o-mini vision)
- ✅ Brand colors applied
- ✅ Localized campaign message at bottom
- ✅ Compliance validated (banned words, legal guidelines)

**S3 File Structure:**
```
s3://creative-assets/outputs/fall_2025_promo/
├── en/
│   ├── p01/
│   │   ├── raw/
│   │   │   └── img_abc123.png                    (DALL-E generated)
│   │   ├── branded/
│   │   │   └── img_abc123_branded.png            (+ logo + brand colors)
│   │   └── final/
│   │       ├── 1x1/fall_2025_promo_en_p01_1x1_v1.png
│   │       ├── 4x5/fall_2025_promo_en_p01_4x5_v1.png
│   │       ├── 9x16/fall_2025_promo_en_p01_9x16_v1.png
│   │       └── 16x9/fall_2025_promo_en_p01_16x9_v1.png
│   └── p02/
│       └── final/
│           ├── 1x1/fall_2025_promo_en_p02_1x1_v1.png
│           ├── 4x5/fall_2025_promo_en_p02_4x5_v1.png
│           ├── 9x16/fall_2025_promo_en_p02_9x16_v1.png
│           └── 16x9/fall_2025_promo_en_p02_16x9_v1.png
├── de/ ... (8 more images)
├── fr/ ... (8 more images)
└── it/ ... (8 more images)
```

### What Makes Each Image Unique

| Aspect | How It's Customized |
|--------|---------------------|
| **Product** | Different DALL-E prompt per product |
| **Locale** | Localized copy + culture-aware context |
| **Logo Position** | AI analyzes each image, places logo optimally |
| **Aspect Ratio** | Text overlay repositioned for each format |
| **Brand** | Consistent colors and logo across all variants |

---

## How localization works (per locale)

1. **Brief submitted** → persisted → `briefs.ingested`.
2. **Context Pack** built for each target locale: culture notes, tone, do/don’t, legal/banned words, plus audience & product descriptors.
3. **Image generation** per product×locale: produce **N** candidates using `prompt_base + context_pack`. Upload to `s3://…/raw/`.
4. **BrandComposer** uses **AI vision analysis** (GPT-4o-mini) to determine optimal logo placement, then adds logo/brand colors; writes `*_branded.*` to `s3://…/branded/`.
5. **Copy generation** per candidate (uses the **branded image** + context to produce a short localized line).
6. **Compliance check** (warn-only): banned words & basic legal hints; UI shows warnings.
7. **Overlay & export**: render text with safe margins/contrast → **1:1, 9:16, 16:9** → `s3://…/final/<aspect>/`.
8. **Scoring & selection**: LLM-fit + brand heuristics + compliance; mark **best per locale** (keep alternates).
9. **Approval or revision** in Streamlit; on revision → re-generate (keep seed first, then randomize).

See the sequence and containers diagrams in `docs/architecture.md`.

---

## Required & optional input fields (brief)

**Required**

* `campaign_id`
* `products` (≥2): `{ id, name, description }`
* `target_locales`: one or more of `en,de,fr,it` (English required)
* `audience`: `{ region, audience, age_min?, age_max?, interests_text? }`
* `localization.message_en` (localized fields optional; the system can generate copy)
* `output`: `{ aspect_ratios: ["1x1","9x16","16x9"], format: "png"|"jpeg", s3_prefix }`

**Optional / recommended**

* `brand`: `{ primary_color, logo_s3_uri, banned_words_{en|de|fr|it}[], legal_guidelines }`
* `placement`: `{ overlay_text_position: top|center|bottom }` (logo position is **AI-determined** via vision analysis)
* Generation knobs: `n` candidates per product×locale, seed policy
* Alert routing overrides for this campaign

**Example**

```json
{
  "campaign_id": "fall_2025_promo",
  "products": [
    {"id": "p01", "name": "Serum X", "description": "Vit C brightening"},
    {"id": "p02", "name": "Cream Y", "description": "Deep hydration"}
  ],
  "target_locales": ["en","de","fr"],
  "audience": {
    "region": "CH",
    "audience": "Young professionals",
    "age_min": 25,
    "age_max": 45,
    "interests_text": "women interested in beauty"
  },
  "localization": { "message_en": "Shine every day" },
  "brand": {
    "primary_color": "#FF3355",
    "logo_s3_uri": "s3://brand/logo.png",
    "banned_words_en": ["miracle","free"]
  },
  "placement": { "logo_position": "bottom_right", "overlay_text_position": "bottom" },
  "output": { "aspect_ratios": ["1x1","9x16","16x9"], "format": "png", "s3_prefix": "outputs/" }
}
```

---

## Repository layout

```
/docs
  architecture.md                 # diagrams + Service Responsibilities & I/O matrix
  api-schema-reference.md         # REST models, NATS contracts, Mongo schemas, config

/services
  api-gateway/                    # FastAPI + Pydantic, publishes briefs.ingested etc.
  ui-webapp/                      # Streamlit UI
  orchestration-router/
  context-enricher/
  image-generator/
  brand-composer/
  copy-generator/
  compliance-checker/
  overlay-composer/
  scorer-selector/
  approval-handler/
  alert-dispatcher/               # plugins/alerts/{email.py,sms.py,nats.py,webhook.py}
  guardian-dlq/
  run-logger/

/infra
  docker-compose.yml              # NATS, Mongo, MinIO, Promtail, Prometheus, Grafana
  grafana/                        # dashboards
  promtail/                       # scrape configs

/examples
  briefs/                         # sample briefs
  messages/                       # sample NATS payloads
```

---

## AI-Powered Logo Placement

The **BrandComposer** service uses **GPT-4o-mini with vision** to intelligently determine optimal logo placement for each generated image:

### How It Works

1. **Image Analysis**: After image generation, the brand composer sends the image to GPT-4o-mini with vision capabilities
2. **Intelligent Reasoning**: The AI analyzes:
   - Visual composition and balance
   - Product feature locations (avoiding coverage)
   - Negative space availability
   - Overall aesthetic harmony
3. **Optimal Placement**: Returns position (top_left, top_right, bottom_left, bottom_right), exact coordinates, scale factor, and reasoning
4. **Application**: Logo is overlaid at the AI-determined position with appropriate sizing

### Benefits

- **No manual configuration** needed per campaign
- **Context-aware** placement that adapts to each unique image
- **Transparent reasoning** logged and displayed in UI
- **Consistent quality** across all locales and products

### Example Output

```
🤖 LLM logo placement: bottom_right at (870, 921), scale=0.15
💡 Reasoning: Placing the logo in the bottom right corner allows for a visually 
   balanced composition, keeping it away from the woman's face and ensuring it 
   does not cover any product features. This position utilizes negative space 
   effectively while maintaining logo visibility.
```

---

## Prereqs

* Docker & Docker Compose
* (Optional dev) Python 3.11, Poetry/uv or pip, Node-free
* Access to **MongoDB**, **MinIO/S3**, **NATS**, and **OpenAI-compatible** endpoint (or set the custom adapter)

---

## Configuration

Create `.env` at repo root (see all keys in `docs/api-schema-reference.md`):

```
MONGO_URI=mongodb://mongo:27017
MONGO_DB=creative_automation

S3_ENDPOINT_URL=http://minio:9000
S3_EXTERNAL_ENDPOINT_URL=http://localhost:9000  # For presigned URLs accessible from browser
S3_REGION=us-east-1
S3_ACCESS_KEY_ID=minioadmin
S3_SECRET_ACCESS_KEY=minioadmin
S3_BUCKET=creative-assets

NATS_URL=nats://nats:4222

IMAGE_PROVIDER=openai         # or custom
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1
IMAGE_MODEL=sdxl              # example name

LANGTRACE_API_KEY=...
PROMETHEUS_PORT=9100
LOKI_URL=http://loki:3100
```

Optional `config.yaml` (validated at startup) is documented in `docs/api-schema-reference.md`.

---

## Run it

1. **Start infra**

```bash
docker compose -f infra/docker-compose.yml up -d
```

2. **Start services** (each in its own container)
   Either with the provided compose profile or `make up`. (Service list is in `docs/architecture.md`.)

3. **Open the UI**
   Streamlit at `http://localhost:8501` (default). Create a campaign, upload brand logo (S3), set locales.

4. **Submit brief → watch pipeline**

* NATS events drive the workers; see live alerts in UI.
* Approve or request changes; first revision keeps seed; later randomizes.

5. **Outputs**
   All assets land in S3/MinIO:

```
s3://<bucket>/outputs/<campaign>/<locale>/<product>/
  raw/<guid>.png
  branded/<guid>_branded.png
  final/1x1/<campaign>_<locale>_<product>_1x1_v<rev>.png
  final/9x16/...
  final/16x9/...
```

---

## Observability

* **Metrics:** `:9100/metrics` on each service (Prometheus scrape)
* **Logs:** stdout → Promtail → **Loki** (search by `corr_id`, `campaign_id`, `locale`, `product_id`, `revision`)
* **Dashboards:** Grafana panels for throughput, latency, DLQ, approval latency
* **Tracing:** **Langtrace** around LLM/image calls

---

## Alerts

Pluggable **alert-dispatcher** routes events to sinks configured in `config.yaml`:

* Email (SMTP), SMS (stub), Webhook, **NATS→UI**
* DLQ incidents are enriched by **guardian-dlq** and escalated to ops

---

## NATS subjects (quick view)

* Ingress/control: `briefs.ingested`, `creative.approved`, `creative.revision.requested`
* Context: `context.enrich.request` → `context.enrich.ready`
* Images: `creative.generate.request` → `creative.generate.done`
* Brand: `creative.brand.compose.request` → `creative.brand.compose.done`
* Copy: `creative.copy.generate.request` → `creative.copy.generate.done`
* Compliance: `compliance.checked`
* Overlay: `creative.overlay.request` → `creative.overlay.done`
* Selection/Review: `creative.ready_for_review`
* Alerts: `alerts.ui`, `alerts.ops`
* DLQ: `dlq.creative.(generate|brand.compose|copy|overlay)`

> Full payload schemas are in [`docs/schemas.md`](docs/schemas.md).

---

## Acceptance checklist (maps to FDE)

* ✅ Architecture + roadmap + backend/data integration (**see `docs/architecture.md`**)
* ✅ Working POC with README + example I/O
* ✅ Generates / reuses assets; outputs **1:1, 9:16, 16:9**; overlays copy
* ✅ Per-locale context, image candidates, localized copy; **best per locale**
* ✅ BrandComposer (logo/colors) as a separate step; compliance WARNs
* ✅ Agentic design with NATS, DLQ + **Guardian**, pluggable alerts
* ✅ Demo flow & instructions (record screen of UI + outputs)

---

## Limitations & next steps

* Streamlit auth skipped for POC (add in prod)
* Copy/score heuristics are tunable; hook in A/B metrics later
* Add more providers (Midjourney relay, local Diffusers) behind the same interface
* Harden compliance (geo-specific legal templates)
