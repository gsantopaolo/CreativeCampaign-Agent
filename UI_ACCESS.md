# UI Access Guide

This document provides access information for all UI tools in the Creative Campaign system.

## Web UIs (Browser Access)

### 1. Creative Campaign Web UI
- **URL**: http://localhost:8501
- **Purpose**: Main application UI for managing campaigns
- **Features**: Create campaigns, view status, approve variants

### 2. MongoDB Express
- **URL**: http://localhost:8081
- **Username**: `admin`
- **Password**: `admin`
- **Purpose**: Browse and manage MongoDB data
- **Features**: 
  - View collections: campaigns, context_packs, creatives, variants
  - Query and edit documents
  - Database administration

### 3. MinIO Console
- **URL**: http://localhost:9001
- **Username**: `minioadmin`
- **Password**: `minioadmin`
- **Purpose**: S3-compatible object storage UI
- **Features**: Browse buckets, upload/download files, manage access

### 4. NATS NUI
- **URL**: http://localhost:31311
- **Purpose**: Web UI for NATS JetStream monitoring
- **Features**: 
  - View streams and consumers
  - Monitor messages in real-time
  - Inspect stream details
  - View consumer configurations

### 5. Portainer
- **URL**: http://localhost:9000
- **Purpose**: Docker container management
- **Features**: Monitor containers, view logs, manage stacks

## CLI Tools (Docker Exec)

### NATS Box (NATS CLI Tools)

Access the NATS Box container:
```bash
docker exec -it creative-nats-box sh
```

Once inside, you can use these commands:

#### List Streams
```bash
nats stream ls
```

#### View Stream Details
```bash
nats stream info context-request-stream
nats stream info context-ready-stream
```

#### List Consumers
```bash
nats consumer ls context-request-stream
nats consumer ls context-ready-stream
```

#### Subscribe to Messages (Real-time monitoring)
```bash
# Monitor context enrichment requests
nats sub 'context.enrich.request'

# Monitor context enrichment ready events
nats sub 'context.enrich.ready'

# Monitor creative generation requests
nats sub 'creative.generate.request'
```

#### View Stream Messages
```bash
# Get messages from a stream
nats stream get context-request-stream 1
```

#### Stream Statistics
```bash
nats stream report
```

## NATS HTTP Monitoring (Built-in Web UI)

NATS exposes an HTTP monitoring endpoint with JSON data that you can view in your browser:
- **URL**: http://localhost:8222
- **Endpoints**:
  - http://localhost:8222/varz - General server information
  - http://localhost:8222/connz - Connection information  
  - http://localhost:8222/routez - Routing information
  - http://localhost:8222/subsz - Subscription information
  - http://localhost:8222/jsz - **JetStream information** (streams, consumers, messages)

**Recommended**: Use http://localhost:8222/jsz to view JetStream streams and their status in JSON format.

For a better viewing experience, install a JSON formatter browser extension like:
- Chrome: JSON Formatter
- Firefox: JSONView

Example:
```bash
curl http://localhost:8222/jsz | jq
```

## Quick Reference

| Service | Port | URL | Credentials |
|---------|------|-----|-------------|
| Web UI | 8501 | http://localhost:8501 | None |
| API | 8000 | http://localhost:8000 | None |
| MongoDB Express | 8081 | http://localhost:8081 | admin/admin |
| NATS NUI | 31311 | http://localhost:31311 | None |
| MinIO Console | 9001 | http://localhost:9001 | minioadmin/minioadmin |
| Portainer | 9000 | http://localhost:9000 | Set on first login |
| MongoDB | 27017 | mongodb://localhost:27017 | None |
| NATS | 4222 | nats://localhost:4222 | None |

## Useful Commands

### View All Running Services
```bash
docker ps
```

### View Logs
```bash
# API logs
docker logs creative-api -f

# Context Enricher logs
docker logs creative-context-enricher -f

# Creative Generator logs
docker logs creative-generator -f

# MongoDB logs
docker logs creative-mongodb -f

# NATS logs
docker logs creative-nats -f
```

### Restart Services
```bash
cd deployment
docker-compose restart <service-name>
```

### Stop All Services
```bash
cd deployment
docker-compose down
```

### Start All Services
```bash
cd deployment
docker-compose up -d
```
