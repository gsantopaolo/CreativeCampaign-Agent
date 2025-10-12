# Environment Variables Reference

This document lists all environment variables used across the Creative Campaign Agent system.

## 📁 Configuration Files

- **Main deployment**: `deployment/.env.example`
- **Individual services**: `src/{service}/.env.example`

## 🔧 Global Variables (All Services)

### Logging
| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `LOG_FORMAT` | `%(asctime)s - %(name)s - %(levelname)s - %(message)s` | Python logging format string |

### MongoDB
| Variable | Default | Description |
|----------|---------|-------------|
| `MONGODB_URL` | `mongodb://localhost:27017` | MongoDB connection string |
| `MONGODB_DB_NAME` | `creative_campaign` | Database name |

### NATS JetStream
| Variable | Default | Description |
|----------|---------|-------------|
| `NATS_URL` | `nats://localhost:4222` | NATS server URL |
| `NATS_RECONNECT_TIME_WAIT` | `2` | Seconds to wait between reconnection attempts |
| `NATS_CONNECT_TIMEOUT` | `10` | Connection timeout in seconds |
| `NATS_MAX_RECONNECT_ATTEMPTS` | `60` | Maximum reconnection attempts |

## 🤖 OpenAI Configuration

### Text Generation (Context Enricher, Creative Generator, Brand Composer, Text Overlay)
| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | **REQUIRED** | OpenAI API key from https://platform.openai.com/api-keys |
| `OPENAI_TEXT_MODEL` | `gpt-4o-mini` | Model for text generation (gpt-4o-mini, gpt-4o, gpt-4-turbo) |

### Image Generation (Image Generator)
| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | **REQUIRED** | OpenAI API key |
| `OPENAI_IMAGE_MODEL` | `dall-e-3` | DALL-E model (dall-e-3, dall-e-2) |
| `OPENAI_IMAGE_QUALITY` | `standard` | Image quality (standard, hd) |

**Note:** DALL-E 3 supports three sizes: `1024x1024`, `1792x1024`, `1024x1792`

## 💾 MinIO/S3 Storage

| Variable | Default | Description |
|----------|---------|-------------|
| `S3_ENDPOINT_URL` | `http://localhost:9000` | MinIO/S3 endpoint (internal) |
| `S3_EXTERNAL_ENDPOINT_URL` | `http://localhost:9000` | External endpoint for presigned URLs |
| `S3_ACCESS_KEY_ID` | `minioadmin` | S3 access key |
| `S3_SECRET_ACCESS_KEY` | `minioadmin` | S3 secret key |
| `S3_BUCKET_NAME` | `creative-assets` | Bucket name for storing assets |

**Used by:** API, Image Generator, Brand Composer, Text Overlay

## 🎨 Brand Composer Specific

| Variable | Default | Description |
|----------|---------|-------------|
| `LOGO_SIZE_PERCENT` | `0.15` | Logo size as percentage of image width (0.10-0.20) |
| `LOGO_MARGIN_PERCENT` | `0.03` | Margin from edges as percentage (0.02-0.05) |

## 🌐 Web UI

| Variable | Default | Description |
|----------|---------|-------------|
| `API_BASE_URL` | `http://localhost:8000` | API service URL |

## 🏥 Readiness Probes

| Variable | Default | Description |
|----------|---------|-------------|
| `CONTEXT_ENRICHER_READINESS_TIME_OUT` | `500` | Timeout in seconds |
| `CREATIVE_GENERATOR_READINESS_TIME_OUT` | `500` | Timeout in seconds |
| `IMAGE_GENERATOR_READINESS_TIME_OUT` | `500` | Timeout in seconds |
| `BRAND_COMPOSER_READINESS_TIME_OUT` | `500` | Timeout in seconds |
| `TEXT_OVERLAY_READINESS_TIME_OUT` | `500` | Timeout in seconds |

## 📋 Service-Specific Requirements

### API Service
- MongoDB
- NATS
- S3/MinIO

### Context Enricher
- MongoDB
- NATS
- OpenAI (Text)

### Creative Generator
- MongoDB
- NATS
- OpenAI (Text)

### Image Generator
- MongoDB
- NATS
- OpenAI (Image)
- S3/MinIO

### Brand Composer
- MongoDB
- NATS
- OpenAI (Text - for vision)
- S3/MinIO

### Text Overlay
- MongoDB
- NATS
- OpenAI (Text - for vision)
- S3/MinIO

### Web UI
- API URL only

## 🚀 Quick Start

1. **Copy the example file:**
   ```bash
   cp deployment/.env.example deployment/.env
   ```

2. **Set your OpenAI API key:**
   ```bash
   # Edit deployment/.env
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

3. **Start the services:**
   ```bash
   cd deployment
   docker-compose up -d
   ```

## 🔐 Security Notes

- **Never commit `.env` files** to version control
- **Rotate API keys regularly**
- **Use different credentials** for production vs development
- **Restrict S3 bucket access** in production environments
- **Use secrets management** (e.g., AWS Secrets Manager, HashiCorp Vault) for production

## 📊 Aspect Ratio Configuration

Aspect ratios are configured per campaign (not via environment variables):

| Ratio | Name | DALL-E Size | Use Case |
|-------|------|-------------|----------|
| `1x1` | Square | 1024x1024 | Instagram Feed, Facebook |
| `4x5` | Instagram Portrait | 1024x1792* | Instagram Feed (vertical) |
| `9x16` | Story | 1024x1792 | Instagram/Facebook Stories |
| `16x9` | Landscape | 1792x1024 | YouTube, Desktop |

*4:5 uses 9:16 (1024x1792) as closest DALL-E 3 approximation
