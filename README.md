# 🎨 CreativeCampaign-Agent

AI-powered creative automation for social ads: generate brand-safe images, add logos intelligently, localize copy, and export in multiple formats—all at scale.

---

## 💡 Why This Approach?

This isn't just a coding exercise—it's built like a real customer deployment. Instead of a toy demo, this POC demonstrates production-ready patterns you'd actually use at scale.

### Design Principles

✅ **Smart Architecture** - Event-driven microservices where they add value  
✅ **Production-Ready** - Scalability, reliability, and observability from day one  
✅ **AI-Powered** - OpenAI DALL-E 3 + GPT-4o-mini for intelligent automation  
✅ **Real-World Ready** - Enterprise tools (S3, MongoDB, NATS) you'd use in production  

### What Makes This Production-Ready?

This POC demonstrates how to build production-ready creative automation at scale:

🔄 **Event-driven architecture** that scales horizontally  
🛡️ **Fault Tolerant**: Retries, health checks, graceful degradation  
🤖 **AI-powered intelligence** for branding, context enrichment, localization and image analysis for optimal logo placement  
✅ **Production patterns** you'd actually deploy to customers  
✅ **Observable & reliable** with health checks and retries  

Built in the spirit of how a Forward Deployed Engineer would approach a 2-day customer POC—showing both technical depth and pragmatic engineering judgment.
See [`docs/simplified-alternative.md`](docs/simplified-alternative.md) for a minimal approach, and [`docs/why-microservices.md`](docs/why-microservices.md) for architectural trade-offs.

---

## 📋 What It Does

Turns a **campaign brief** into **localized creatives** (images + copy) for multiple 
products and languages, with **AI-powered branding**, **multi-format export**, 
and **production-ready reliability**.

> **📚 Documentation:**
>
> * **Requirements** → [`docs/requirements.md`](docs/requirements.md)
> * **Architecture & Design** → [`docs/architecture.md`](docs/architecture.md) · [`docs/architecture-diagram.md`](docs/architecture-diagram.md)
> * **Agentic System Design** → [`docs/agentic-system-design.md`](docs/agentic-system-design.md)
> * **AI-Powered Features** → [`docs/ai-logo-placement.md`](docs/ai-logo-placement.md)
> * **Implementation Patterns** → [`docs/implementation-patterns.md`](docs/implementation-patterns.md)
> * **API & Schema Reference** → [`docs/schemas.md`](docs/schemas.md)
> * **Setup & Configuration** → [`docs/setup.md`](docs/setup.md)
> * **Architecture Trade-offs** → [`docs/why-microservices.md`](docs/why-microservices.md) · [`docs/simplified-alternative.md`](docs/simplified-alternative.md)
> * **Stakeholder Communication** → [`docs/stakeholder-communication-agent.md`](docs/stakeholder-communication-agent.md)


---

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Docker & Docker Compose installed
- OpenAI API key ([get one here](https://platform.openai.com/api-keys))

### Step 1: Clone & Configure

#### Clone the repository
```bash
git clone https://github.com/gsantopaolo/CreativeCampaign-Agent.git
cd CreativeCampaign-Agent
```
#### Copy environment template
```bash
cp deployment/.env.example deployment/.env
```
#### Edit and add your OPENAI_API_KEY in the .env file
- Open the newly created .env file with your favorite editor
- Generate and API key from [OpenAI API Dashboard](https://platform.openai.com/api-keys) 
- Copy the key
- Paste it on OPENAI_API_KEY= 

#### Make scripts executable (first time only)
```bash
chmod +x start.sh stop.sh
```

### Step 2: Start All Services
To start all services:
```bash
./start.sh  
```
To stop all services once you're done:
```bash
./stop.sh  
```

### Step 3: Access the UI

Once all services are running, you can access the following interfaces:

#### Main Application
- **Web UI (Streamlit)** - Create and manage campaigns  
  [http://localhost:8501](http://localhost:8501)


#### Management & Monitoring
- **Portainer** - Container management and logs  
  [http://localhost:9002](http://localhost:9002)  
  *First-time setup: Create admin account on first visit*

- **MongoDB Express** - Database browser  
  [http://localhost:8081](http://localhost:8081)  
  Username: `admin` | Password: `admin`

- **MinIO Console** - S3 storage management  
  [http://localhost:9001](http://localhost:9001)  
  Username: `minioadmin` | Password: `minioadmin`

- **NATS NUI** - Message queue monitoring  
  [http://localhost:31311](http://localhost:31311)

- **API Gateway (FastAPI)** - REST API and interactive docs  
  [http://localhost:8000/docs](http://localhost:8000/docs)

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
4. Watch the pipeline execute in real-time! via [Portainer logs](http://localhost:9002)  

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

/src
  api/                    # FastAPI + Pydantic, publishes briefs.ingested etc.
  web/                      # Streamlit UI
  context-enricher/
  image-generator/
  brand-composer/

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

## ✅ Requirements Checklist

* ✅ **Architecture + roadmap** - See [`docs/architecture.md`](docs/architecture.md)
* ✅ **Working POC** - Docker Compose, full pipeline
* ✅ **Multi-format export** - 4 aspect ratios (1x1, 4x5, 9x16, 16x9)
* ✅ **Localization** - Per-locale context + culturally-aware copy
* ✅ **AI-powered branding** - GPT-4o-mini vision for logo placement
* ✅ **Event-driven** - NATS JetStream with retries & health checks
* ✅ **Production patterns** - Microservices, observability, scalability

---

## 🚧 Known Limitations & Future Enhancements

**Current Limitations:**
- No authentication (Streamlit is open - add OAuth for production)
- Single OpenAI provider (works great, but could add fallbacks)
- Observability only via Portainer, shall be extended to use Grafana/Prometheus/Loki

**Future Enhancements:**
- 🔐 Add authentication & role-based access
- 🎨 Support more AI providers (Midjourney, Stable Diffusion)
- 📊 A/B testing metrics integration
- 🌍 Geo-specific legal compliance templates
- 📈 Prometheus metrics + Grafana dashboards

---



