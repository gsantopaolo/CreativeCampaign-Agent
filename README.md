# CreativeCampaign-Agent
Agentic AI for social ads: brand-safe hero images &amp; layouts, generated, resized, localized, and region-customized at scale




# Creative Automation for Localized Social Ads (POC)

End-to-end pipeline that turns a **campaign brief** into **localized creatives** (images + copy) for multiple products and languages, with **brand composition**, **approvals & revisions**, **alerts**, and **observability**. Built for the Adobe FDE take-home.

> Full details:
>
> * **Architecture & orchestration** → `docs/architecture.md`
> * **API & Schema Reference** (REST models, NATS contracts, Mongo schemas, config) → `docs/api-schema-reference.md`

---

## TL;DR

* **Stack:** Python · **FastAPI** (REST) · **Streamlit** (UI) · **NATS** (bus, JetStream queues) · **MongoDB** (metadata) · **MinIO/S3** (assets via `boto3`)
* **GenAI providers:** OpenAI-SDK compatible (via `base_url`), plus a **custom adapter** (e.g., Stability/Midjourney/local Diffusers)
* **Branding:** separate **BrandComposer** service overlays logo/colors; originals remain intact
* **Localization:** per-locale **Context Pack** → generate **N** image candidates + localized short copy → choose **best per locale**
* **Approvals:** human-in-the-loop; first revision keeps seed, later randomizes
* **Reliability:** retries + **DLQ** + **Guardian** with pluggable alert sinks (email/SMS/webhook/NATS→UI)
* **Observability:** Prometheus + Loki/Promtail + Grafana; **Langtrace** for LLM calls

---

## How localization works (per locale)

1. **Brief submitted** → persisted → `briefs.ingested`.
2. **Context Pack** built for each target locale: culture notes, tone, do/don’t, legal/banned words, plus audience & product descriptors.
3. **Image generation** per product×locale: produce **N** candidates using `prompt_base + context_pack`. Upload to `s3://…/raw/`.
4. **BrandComposer** adds logo/accents; writes `*_branded.*` to `s3://…/branded/`.
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
* `placement`: `{ logo_position: top_left|top_right|bottom_left|bottom_right, overlay_text_position: top|center|bottom }`
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
