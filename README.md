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

### What Makes Each Image Unique

| Aspect | How It's Customized |
|--------|---------------------|
| **Product** | Different DALL-E prompt per product |
| **Locale** | Localized copy + culture-aware context |
| **Logo Position** | AI analyzes each image, places logo optimally |
| **Aspect Ratio** | Text overlay repositioned for each format |
| **Brand** | Consistent colors and logo across all variants |

---

## Prereqs

* Docker & Docker Compose
* (Optional dev) Python 3.11, Poetry/uv or pip, Node-free
* Access to **MongoDB**, **MinIO/S3**, **NATS**, and **OpenAI-compatible** endpoint (or set the custom adapter)

---


## 📚 Documentation
* [Requirements](docs/requirements.md)
* [Architecture](docs/architecture.md)
  *   [Architecture Diagram](docs/architecture-diagram.md)
  *   [Architecture-Simplified](docs/architecture-simplified.md)
*   [Agentic System Design](docs/agentic-system-design.md)
*   [AI Logo Placement](docs/ai-logo-placement.md)
*   [Implementation Patterns](docs/implementation-patterns.md)
*   [Simplified Alternative](docs/simplified-alternative.md)
*   [Schemas](docs/schemas.md)

### Services

*   [Service: Brand Composer](docs/service-brand-composer.md)
*   [Service: Context Enricher](docs/service-context-enricher.md)
*   [Service: Creative Generator](docs/service-creative-generator.md)
*   [Service: Image Generator](docs/service-image-generator.md)
*   [Service: Text Overlay](docs/service-text-overlay.md)

### Installation
*   [Setup](docs/setup.md)

### Others
*   [Stakeholder Communication Agent](docs/stakeholder-communication-agent.md)
*   [Why Microservices](docs/why-microservices.md)
*   [Roadmap](docs/roadmap.md)

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



