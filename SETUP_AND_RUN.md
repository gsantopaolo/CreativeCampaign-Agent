# Creative Campaign - Setup & Run Guide

## Prerequisites

✅ Docker and Docker Compose installed
✅ Conda environment `creative-campaign` created
✅ OpenAI API key (for DALL-E 3)

---

## Configuration Files

### Environment Variables Overview

The project uses **two separate .env files**:

| File | Purpose | Used By |
|------|---------|---------|
| `deployment/.env` | Docker container configuration | docker-compose.yml |
| `src/api/.env` | Local development configuration | Running API locally |

**Key Difference**: 
- `deployment/.env` uses Docker service names (e.g., `mongodb://mongodb:27017`)
- `src/api/.env` uses localhost (e.g., `mongodb://localhost:27017`)

### Environment Variables Reference

#### Logging
```bash
LOG_LEVEL=INFO              # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

#### MongoDB (Database)
```bash
MONGODB_URL=mongodb://mongodb:27017    # Docker: mongodb://mongodb:27017
                                       # Local:  mongodb://localhost:27017
MONGODB_DB_NAME=creative_campaign      # Database name (default: creative_campaign)
```

#### NATS JetStream (Message Bus)
```bash
NATS_URL=nats://nats:4222              # Docker: nats://nats:4222
                                       # Local:  nats://localhost:4222
NATS_RECONNECT_TIME_WAIT=10            # Seconds to wait between reconnection attempts
NATS_CONNECT_TIMEOUT=10                # Connection timeout in seconds
NATS_MAX_RECONNECT_ATTEMPTS=60         # Max reconnection attempts before giving up
```

#### Future: OpenAI (for worker services - not yet used by API)
```bash
# OPENAI_API_KEY=sk-your-key-here      # Uncomment when implementing image-generator service
```

---

## Quick Start (Docker - Recommended)

### 1. Configure Environment Variables

```bash
cd deployment
cp .env.example .env
```

The default values are fine for local development. **No changes needed** unless you want to customize:
- Database name
- Log level (DEBUG for troubleshooting)
- NATS connection parameters

**Note**: `OPENAI_API_KEY` is commented out - it will be needed later for worker services.

### 2. Start Everything

```bash
./start.sh
```

This will:
- Start MongoDB (port 27017)
- Start NATS JetStream (port 4222, monitor on 8222)
- Start MinIO (S3-compatible, port 9000, console 9001)
- Build and start API Gateway (port 8000)

### 3. Verify Services

```bash
# Check all services are running
docker-compose ps

# View API logs
docker-compose logs -f api

# Test API
curl http://localhost:8000/healthz
```

### 4. Access Services

- **API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **NATS Monitor**: http://localhost:8222
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin)

### 5. Stop Services

```bash
./stop.sh
```

---

## Local Development (Using Conda)

For local development/debugging without Docker:

### 1. Activate Conda Environment

```bash
conda activate creative-campaign
```

### 2. Install/Update Dependencies

```bash
cd src/api
pip install -r requirements.txt
```

### 3. Start Infrastructure Only (Docker)

```bash
cd deployment
docker-compose up -d mongodb nats minio minio-init
```

Wait for services to be healthy:
```bash
# Check status
docker-compose ps
```

### 4. Configure Local .env

```bash
cd ../src/api
cp .env.example .env
```

The `.env.example` already has correct defaults for local development:
```bash
MONGODB_URL=mongodb://localhost:27017          # ✅ Localhost (not 'mongodb')
NATS_URL=nats://localhost:4222                 # ✅ Localhost (not 'nats')
MONGODB_DB_NAME=creative_campaign
NATS_RECONNECT_TIME_WAIT=10
NATS_CONNECT_TIMEOUT=10
NATS_MAX_RECONNECT_ATTEMPTS=60
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

**No changes needed** - the defaults work out of the box!

### 5. Run API Locally

```bash
# From src/api/ directory
python main.py

# Or with uvicorn for auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Test API

```bash
# In another terminal (with conda env activated)
cd src/api
python test_api.py
```

---

## Testing the API

### Using the Test Script

```bash
# Make sure API is running (Docker or local)
conda activate creative-campaign
cd src/api
python test_api.py
```

### Using cURL

```bash
# Health check
curl http://localhost:8000/healthz

# Create a campaign
curl -X POST http://localhost:8000/campaigns \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_id": "test_001",
    "products": [
      {"id": "p01", "name": "Product A", "description": "Test product"},
      {"id": "p02", "name": "Product B", "description": "Another product"}
    ],
    "target_locales": ["en", "de"],
    "audience": {
      "region": "DACH",
      "audience": "Young professionals"
    },
    "localization": {
      "message_en": "Test message",
      "message_de": "Testnachricht"
    },
    "output": {
      "aspect_ratios": ["1x1", "9x16"],
      "format": "png",
      "s3_prefix": "test/"
    }
  }'

# List campaigns
curl http://localhost:8000/campaigns

# Get specific campaign
curl http://localhost:8000/campaigns/test_001
```

### Using Swagger UI

Open http://localhost:8000/docs in your browser for interactive API testing.

---

## Monitoring

### View Logs

```bash
# API logs
docker-compose logs -f api

# All services
docker-compose logs -f

# MongoDB logs
docker-compose logs -f mongodb

# NATS logs
docker-compose logs -f nats
```

### MongoDB Access

```bash
# Connect to MongoDB shell
docker-compose exec mongodb mongosh creative_campaign

# List campaigns
db.campaigns.find().pretty()

# Count campaigns
db.campaigns.countDocuments()
```

### NATS Monitoring

```bash
# NATS web interface
open http://localhost:8222

# Subscribe to messages (requires NATS CLI)
nats sub 'briefs.ingested'
nats sub 'context.enrich.request'
nats sub '>'  # Subscribe to all subjects
```

### MinIO (S3) Access

```bash
# Web console
open http://localhost:9001
# Login: minioadmin / minioadmin

# View bucket contents
# Go to "Buckets" → "creative-assets"
```

---

## Troubleshooting

### Verify Environment Variables Are Loaded

**For Docker (check running container):**
```bash
# View all environment variables in API container
docker exec creative-api env | grep -E "^(LOG_|MONGODB_|NATS_)" | sort

# Expected output:
# LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
# LOG_LEVEL=INFO
# MONGODB_DB_NAME=creative_campaign
# MONGODB_URL=mongodb://mongodb:27017
# NATS_CONNECT_TIMEOUT=10
# NATS_MAX_RECONNECT_ATTEMPTS=60
# NATS_RECONNECT_TIME_WAIT=10
# NATS_URL=nats://nats:4222
```

**If values are missing or wrong:**
1. Check `deployment/.env` file exists and has correct values
2. Restart API container: `docker-compose restart api`
3. If still wrong, rebuild: `DOCKER_BUILDKIT=0 docker-compose up -d --build api`

**For Local Development:**
```bash
# Check .env file
cat src/api/.env

# Verify Python loads it correctly (start API and check logs)
# Should see: "✅ Connected to MongoDB: creative_campaign"
```

### API won't start

```bash
# Check if MongoDB is healthy
docker-compose ps mongodb

# Check if NATS is healthy
curl http://localhost:8222/healthz

# View API logs for errors
docker-compose logs api

# Common issues:
# - "MONGODB_URL must be set" → Check deployment/.env file exists
# - "NATS connection failed" → Check NATS container is healthy
```

### Port conflicts

If ports 8000, 4222, 27017, etc. are already in use:

```bash
# Stop conflicting services
docker ps  # Check what's running
docker stop <container-id>

# Or edit docker-compose.yml to use different ports
```

### MongoDB connection issues

```bash
# Test MongoDB connection
docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')"

# Restart MongoDB
docker-compose restart mongodb
```

### Clear all data and restart

```bash
# Stop services
./stop.sh

# Remove volumes (WARNING: deletes all data)
docker-compose down -v

# Start fresh
./start.sh
```

---

## Project Structure

```
CreativeCampaign-Agent/
├── deployment/
│   ├── docker-compose.yml    # Infrastructure + API
│   ├── start.sh               # Start all services
│   ├── stop.sh                # Stop all services
│   └── .env                   # Environment variables (create from .env.example)
├── src/
│   ├── api/
│   │   ├── main.py            # API Gateway (FastAPI)
│   │   ├── requirements.txt
│   │   ├── Dockerfile
│   │   ├── .env               # Local dev config
│   │   └── test_api.py        # Test script
│   └── lib_py/
│       ├── models/
│       │   └── campaign_models.py  # Pydantic models
│       ├── gen_types/         # Generated protobuf code
│       └── middlewares/       # NATS, health checks (from Sentinel-AI)
└── proto/                     # Protobuf definitions
```

---

## What's Next

After API is running and tested:

1. ✅ **Build Worker Services**:
   - context-enricher
   - image-generator (CrewAI agentic)
   - brand-composer
   - copy-generator (CrewAI agentic)
   - overlay-composer
   - guardian-dlq

2. ✅ **Build UI**:
   - Streamlit web app for campaign submission
   - Approval/revision interface

3. ✅ **Add to Docker Compose**:
   - Update docker-compose.yml with worker services
   - Update docker-compose.yml with UI service

---

## Important Notes

- **Conda Environment**: Always activate `creative-campaign` for local development
- **Environment Files**: 
  - `deployment/.env` → Used by Docker containers (service names like `mongodb://mongodb:27017`)
  - `src/api/.env` → Used for local development (localhost URLs)
  - Both files have `.env.example` templates with all required variables
- **All Environment Variables**: Every variable in `.env` files is actually used by the code - no unused config!
- **OpenAI API Key**: Will be needed for worker services (image-generator, copy-generator)
- **Data Persistence**: Docker volumes store MongoDB, NATS, and MinIO data
- **Logs**: All logs use emoji style (copied from Sentinel-AI)
- **Samples**: Don't modify `samples/sentinel-AI` - it's reference code only

---

## Configuration Quick Reference

### deployment/.env (Docker Containers)
```bash
# Required - all values used by docker-compose.yml
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
MONGODB_URL=mongodb://mongodb:27017           # ← Service name 'mongodb'
MONGODB_DB_NAME=creative_campaign
NATS_URL=nats://nats:4222                     # ← Service name 'nats'
NATS_RECONNECT_TIME_WAIT=10
NATS_CONNECT_TIMEOUT=10
NATS_MAX_RECONNECT_ATTEMPTS=60
```

### src/api/.env (Local Development)
```bash
# Same variables, different URLs (localhost instead of service names)
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
MONGODB_URL=mongodb://localhost:27017         # ← localhost for local dev
MONGODB_DB_NAME=creative_campaign
NATS_URL=nats://localhost:4222                # ← localhost for local dev
NATS_RECONNECT_TIME_WAIT=10
NATS_CONNECT_TIMEOUT=10
NATS_MAX_RECONNECT_ATTEMPTS=60
```

### Verify Variables Are Loaded
```bash
# Docker
docker exec creative-api env | grep -E "^(LOG_|MONGODB_|NATS_)"

# Should show all 8 variables with correct values
```

---

## Quick Commands Cheat Sheet

```bash
# Activate conda env
conda activate creative-campaign

# Start everything (Docker)
cd deployment && ./start.sh

# View logs
docker-compose logs -f api

# Test API
curl http://localhost:8000/healthz
open http://localhost:8000/docs

# Access MongoDB
docker-compose exec mongodb mongosh creative_campaign

# Subscribe to NATS messages
nats sub 'briefs.ingested'

# Stop everything
cd deployment && ./stop.sh

# Restart API only
docker-compose restart api

# Rebuild API after code changes
docker-compose up -d --build api
```
