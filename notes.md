
# TL;DR summary

* It’s a **single take-home assignment** (plan ~**6–8 hours**) with **three tasks** you must complete and present in a **30-minute session**. You also need to **record a short demo** showing your POC running locally and send the deck + recording **the day before your interview**. 
* **Scenario:** Build “creative automation for scalable social ad campaigns” for a global brand that launches hundreds of localized campaigns. The system should speed up production, keep branding consistent, localize content, and surface insights. 

## Business goals & pain points (why this exists)

* Goals: accelerate campaign velocity, ensure brand consistency, localize for relevance, improve ROI, and generate actionable insights. 
* Pain points: manual + slow variant creation, inconsistent quality/voice, slow approvals, hard-to-analyze performance at scale, and creative team overload on repetitive work. 

# What you must deliver (the three tasks)

## Task 1 — Architecture & Roadmap

* Create a **high-level architecture diagram** of the end-to-end content pipeline (ingestion, storage, GenAI asset generation). Include stakeholders: **Creative Lead, Ad Ops, IT, Legal/Compliance**.
* Provide a **1-slide roadmap** (epics + timeline) showing how you’d deliver the system.
* **Deliverables:** architecture diagram + roadmap slide (also included in the 30-min presentation). 

## Task 2 — Working POC: Creative Automation Pipeline

Build a local tool/app that:

* **Accepts a campaign brief** (JSON/YAML) with: at least **two products**, target region/market, target audience, and campaign message. 
* **Ingests/reuses input assets** if available (from a local folder or mock storage). If missing, **generate** with a GenAI image model.
* Produces creatives in **≥3 aspect ratios** (e.g., **1:1, 9:16, 16:9**).
* **Overlays the campaign message** on the final posts (English required; localization is a plus).
* **Runs locally** (CLI or simple local app; any language/framework).
* **Saves outputs** in a clear folder structure by **product** and **aspect ratio**.
* Include a **README** with how to run, example I/O, design decisions, assumptions/limitations.
* **Nice-to-have:** brand checks (logo/colors), simple legal word checks, logging/reporting. 

*Data sources you can assume:* manual user inputs (brief + assets), storage (e.g., **Azure/AWS/****Dropbox**), GenAI APIs for hero image + variants. 

## Task 3 — Agentic System Design & Stakeholder Comms

Design an AI-driven **agent** that:

* Monitors incoming briefs, **triggers generation**, tracks **count/diversity** of variants, flags **missing/insufficient assets** (e.g., <3 variants), and sends **alerts/logs**.
* Define the **Model Context Protocol (MCP)**—what info the LLM sees to draft helpful human-readable alerts.
* Write a **sample email** to customer leadership explaining delays (e.g., GenAI API provisioning/licensing).
* **Deliverables:** agentic system design + sample stakeholder email (also summarized in the presentation). 

# Are these two separate projects or only one?

**It’s one integrated assignment** with **three parts**: (1) design + roadmap, (2) a working pipeline POC (code), and (3) agent design + comms. You can (and should) coordinate them together—for example, one GitHub repo for the POC with a `/docs` folder for the architecture, agent design, and the presentation deck, plus a short demo recording. 

# What to actually do (practical game plan)

1. **Design (Task 1)**

* Draw the system: **Brief Ingestion → Asset Store (e.g., local/Dropbox) → GenAI Image Generation → Variant Resizing/Composition → Brand/Legal checks → Output Publisher (local folders) → Logging/Report → (future) Analytics**.
* Note stakeholder touchpoints (Creative reviews, Legal approval loops) on the diagram.
* Build a one-slide **roadmap**: e.g., Week 1 POC, Week 2 brand checks + agent alerting, Week 3 analytics hooks.

2. **Build the POC (Task 2)**

* Define a **brief schema** (example):

  ```json
  {
    "campaign_id": "fall_2025_promo",
    "products": [
      {"id": "p01", "name": "SuperBrush X"},
      {"id": "p02", "name": "Whitening Paste"}
    ],
    "region": "DACH",
    "audience": "Young professionals",
    "message_en": "Smile brighter this fall",
    "brand": {"primary_color": "#FF3355", "logo_path": "assets/logo.png"}
  }
  ```
* **Asset ingestion:** look for `assets/<product_id>/source/*`.
* **Generate if missing:** call your chosen GenAI image endpoint for a “hero image” per product.
* **Compose variants:** render message text; ensure **1:1**, **9:16**, **16:9**; export PNG/JPEG.
* **Output structure:**

  ```
  outputs/
    fall_2025_promo/
      p01/
        1x1/..., 9x16/..., 16x9/...
      p02/
        1x1/..., 9x16/..., 16x9/...
  ```
* **README:** how to run (CLI flags or a tiny local UI), sample brief, sample outputs, decisions & limitations.
* **Bonus hooks:** check brand color usage, verify logo present, flag banned words, write a simple `report.json` per campaign.

3. **Agent design + comms (Task 3)**

* **Agent loop:** watch `/briefs/*.json` (or a queue), validate, trigger the POC, count variants per product/aspect, flag if `<3`, write logs, and send alert (console/email stub).
* **Model Context Protocol:** include brief metadata, product list, variant counts, last error, SLA, and stakeholder mapping to let the LLM craft concise alerts.
* **Sample email:** explain a realistic delay (e.g., API quota/licensing) and the mitigation/ETA.

4. **Presentation & demo**

* **Deck (30 min):** architecture, roadmap, technical design, live/walkthrough screenshots, agent design, and lessons learned.
* **Short demo recording:** start with sample brief → run pipeline → show outputs → show logs/alerts. 

# Quick acceptance checklist (so you know you’re “done”)

* [ ] 30-min deck with architecture + roadmap + backend/data integration. 
* [ ] GitHub repo with runnable POC, clear README, example brief/outputs. 
* [ ] Demo recording of the POC running locally. 
* [ ] Agent design + sample stakeholder email. 

---

## A few decisions for you (so I tailor the solution)

1. **Language / framework preference** for the POC (e.g., Python CLI/Streamlit vs. Node).
2. **Image model/API** you want to use locally (e.g., SDXL) vs. hosted (given this is a demo).
3. **Storage choice** for mock assets (local folders vs. Dropbox; Dropbox is allowed). 
4. **Brand inputs**: do you want me to enforce a sample brand color + logo? If yes, share a hex + logo file.

If you share those preferences, I’ll draft the brief schema, folder skeleton, and a minimal run flow next.

---

## Presentation Structure (30 minutes)

### 5 min: Business Requirements Mapping
- **Challenge overview**: Pain points of manual creative production at scale
- **Our solution mapping**: 
  - Accelerate velocity → Automated generation + reuse
  - Brand consistency → BrandComposer + compliance checks
  - Localization → Context-aware copy generation per locale
  - ROI optimization → Agentic self-evaluation reduces manual iterations
  - Actionable insights → Structured logging + observability hooks
- **Requirements traceability matrix**: Show how each service maps to business goals

### 8 min: Architecture Deep-dive
- **WHY microservices?**
  - **Scale**: Horizontal scaling via K8s + NATS queue groups (handle 10K+ campaigns/day)
  - **Fault isolation**: Image generation failure doesn't block copy generation
  - **Team velocity**: Different teams can own different services
  - **Cost optimization**: Scale only what's needed (more image workers, fewer brand composers)
- **WHEN to simplify?**
  - Low volume (<100 campaigns/month) → Monolithic Python app sufficient
  - Single team → Shared codebase easier to manage
  - Prototype phase → Reduce operational complexity
- **HOW we leverage proven patterns**:
  - Reused 70% from Sentinel-AI (NATS, FastAPI, health checks)
  - Agentic self-evaluation vs. separate validator services (modern pattern)
  - Event-driven vs. REST orchestration (better for async operations)

### 5 min: Live Demo (with backup recording)
1. **Brief submission** (2 products, 3 locales: en, de, fr)
2. **Watch NATS dashboard**: Events flowing through the pipeline
3. **Show generated creatives**: Raw → Branded → Final (3 aspect ratios)
4. **Approval/revision workflow**: Request changes → observe seed policy
5. **Observability**: View logs, metrics, correlation IDs

**Backup**: Pre-recorded video walkthrough if live demo fails

### 7 min: Production Considerations

**Scaling**:
- Horizontal: K8s HPA on queue depth (NATS metrics)
- Vertical: GPU nodes for image generation
- Geographic: Regional deployments for latency

**Cost**:
- On-demand vs. reserved instances for predictable workloads
- GenAI API quotas and rate limiting strategies
- S3 lifecycle policies (archive old campaigns after 90 days)

**Security**:
- API keys in secret managers (Vault, AWS Secrets Manager)
- RBAC for campaign access (who can approve?)
- Data encryption at rest (S3) and in transit (TLS)
- Network policies in K8s (service-to-service auth)

**Monitoring**:
- Metrics: Campaign velocity, generation latency, approval SLA, cost per campaign
- Logs: Structured JSON with correlation IDs (search by campaign, locale, product)
- Traces: LLM call latency, image generation time, end-to-end pipeline duration
- Alerts: DLQ depth, API quota exhaustion, approval queue backlog

### 5 min: Q&A + "Simplified Path" Discussion
- **Address concerns**: "Is this over-engineered?"
  - Response: "For Adobe customer scale, this is right-sized. I can also show a 300-line monolithic version."
- **Show**: `docs/simplified-alternative.md` (single Python app)
- **Discuss trade-offs**:
  - Monolith: Easier to debug, faster initial development
  - Microservices: Better scaling, fault isolation, team ownership
  - Hybrid: Start monolithic, extract services as scale demands

