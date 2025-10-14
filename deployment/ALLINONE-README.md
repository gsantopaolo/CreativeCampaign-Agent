# 🎯 CreativeCampaign-Agent - All-in-One Container

**One container. Zero external dependencies. Full production features.**

This is a complete, standalone Docker container that includes:
- ✅ All 7 application services (Web UI, Backend API, 5 workers)
- ✅ MongoDB database
- ✅ NATS JetStream messaging
- ✅ MinIO S3-compatible storage
- ✅ Management UIs for all components

---

## 🚀 Quick Start

### 1. Build the image
```bash
cd deployment
./build-allinone.sh
```

This builds: `genmind/creative-campaign:v0.0.1-beta` and `genmind/creative-campaign:latest`

### 2. Run the container
```bash
export OPENAI_API_KEY="sk-your-key-here"
docker compose -f docker-compose-allinone.yml up -d
```

**That's it!** 🎉

---

## 🌐 Access the Application

Once started, open your browser to:

| Service | URL | Credentials |
|---------|-----|-------------|
| **🎨 Web Application** | http://localhost:8501 | - |
| **🗄️ MongoDB UI** | http://localhost:8081 | admin / admin |
| **📨 NATS Monitor** | http://localhost:8222 | - |
| **📦 MinIO Console** | http://localhost:9001 | minioadmin / minioadmin |
| **🎛️ Process Manager** | http://localhost:9002 | admin / admin |

---

## 📋 Requirements

- Docker 20.10+ or Docker Desktop
- 4GB RAM minimum (8GB recommended)
- 10GB disk space
- OpenAI API key ([get one here](https://platform.openai.com/api-keys))

---

## 🔧 Configuration

### Required Environment Variable

```bash
export OPENAI_API_KEY="sk-your-api-key-here"
```

### Optional Environment Variables

```bash
export OPENAI_TEXT_MODEL="gpt-4o-mini"      # Default: gpt-4o-mini
export OPENAI_IMAGE_MODEL="dall-e-3"        # Default: dall-e-3
```

---

## 📖 Usage Examples

### Using Docker Compose (Recommended)

**Build and start:**
```bash
cd deployment
./build-allinone.sh

export OPENAI_API_KEY="sk-xxx"
docker compose -f docker-compose-allinone.yml up -d
```

**Stop:**
```bash
docker compose -f docker-compose-allinone.yml down
```

**View logs:**
```bash
docker compose -f docker-compose-allinone.yml logs -f
```

**Stop and remove data:**
```bash
docker compose -f docker-compose-allinone.yml down -v
```

---

### Using Docker CLI

**Run with persistent data:**
```bash
docker volume create creative-campaign-data

docker run -d \
  --name creative-campaign \
  -p 8000:8000 \
  -p 8501:8501 \
  -p 8081:8081 \
  -p 8222:8222 \
  -p 9000:9000 \
  -p 9001:9001 \
  -p 9002:9002 \
  -v creative-campaign-data:/data \
  -e OPENAI_API_KEY="sk-xxx" \
  gsantopaolo/creative-campaign:latest
```

**Run for quick testing (no data persistence):**
```bash
docker run -d \
  --name creative-campaign \
  -p 8501:8501 \
  -e OPENAI_API_KEY="sk-xxx" \
  genmind/creative-campaign:latest
```

---

## 🎛️ Managing Services

### Via Supervisord Web UI (Recommended)

1. Open http://localhost:9002
2. Login: admin / admin
3. See status of all 13 processes
4. Start/stop/restart individual services
5. View real-time logs

### Via CLI (inside container)

```bash
# View all services status
docker exec creative-campaign supervisorctl status

# Restart a specific service
docker exec creative-campaign supervisorctl restart api

# View logs for a service
docker exec creative-campaign supervisorctl tail -f context-enricher

# Stop a service
docker exec creative-campaign supervisorctl stop brand-composer

# Start a service
docker exec creative-campaign supervisorctl start brand-composer
```

---

## 📊 Service Architecture

The container runs **13 processes** managed by Supervisord:

### Infrastructure (3)
1. **MongoDB** - Database (port 27017, internal)
2. **NATS JetStream** - Message queue (port 4222, internal; monitoring port 8222)
3. **MinIO** - S3 storage (ports 9000, 9001)

### Management UIs (3)
4. **MongoDB Express** - Database UI (port 8081)
5. **NATS Monitor** - Messaging stats (port 8222)
6. **Supervisord Web UI** - Process manager (port 9002)

### Application Services (7)
7. **API Backend** - FastAPI (port 8000, internal)
8. **Web UI** - Streamlit (port 8501)
9. **Context Enricher** - Worker
10. **Creative Generator** - Worker
11. **Image Generator** - Worker (DALL-E)
12. **Brand Composer** - Worker
13. **Text Overlay** - Worker

---

## 💾 Data Persistence

All data is stored in `/data` inside the container:

```
/data/
├── mongodb/     # Campaign data, variants, metadata
├── nats/        # JetStream message queues
└── minio/       # Generated images, logos, assets
```

### Backing Up Data

```bash
# Backup to tar.gz
docker run --rm \
  --volumes-from creative-campaign \
  -v $(pwd):/backup \
  ubuntu tar czf /backup/creative-backup-$(date +%Y%m%d).tar.gz /data

# Restore from backup
docker run --rm \
  -v creative-campaign-data:/data \
  -v $(pwd):/backup \
  ubuntu tar xzf /backup/creative-backup-20250114.tar.gz
```

### Inspecting Data

```bash
# Browse MongoDB data
open http://localhost:8081

# Browse S3 storage
open http://localhost:9001

# Or use CLI tools inside container
docker exec -it creative-campaign bash
ls -la /data/mongodb
ls -la /data/minio
```

---

## 🔍 Troubleshooting

### Container won't start

**Check logs:**
```bash
docker logs creative-campaign
```

**Most common issues:**
- ❌ Port already in use → Change port mapping: `-p 8502:8501`
- ❌ Insufficient memory → Increase Docker memory limit to 4GB+
- ❌ Missing OpenAI key → Set `-e OPENAI_API_KEY=sk-xxx`

### Service is not running

1. **Check status in Supervisord UI:** http://localhost:9002
2. **Or via CLI:**
   ```bash
   docker exec creative-campaign supervisorctl status
   ```
3. **View service logs:**
   ```bash
   docker exec creative-campaign supervisorctl tail -f api
   ```
4. **Restart service:**
   ```bash
   docker exec creative-campaign supervisorctl restart api
   ```

### Database is empty after restart

**Check if volume is mounted:**
```bash
docker inspect creative-campaign | grep Mounts -A 10
```

**Ensure you're using a volume:**
```bash
# Named volume (persists)
docker run -v creative-campaign-data:/data ...

# Bind mount (persists)
docker run -v $(pwd)/data:/data ...
```

### High memory usage

The all-in-one container uses ~2-3GB RAM with all services running.

**To reduce memory:**
```bash
# Stop non-essential services
docker exec creative-campaign supervisorctl stop mongo-express
docker exec creative-campaign supervisorctl stop nats-nui
```

---

## 🚢 Publishing to Docker Hub

### Build with version:
```bash
cd deployment
./build-allinone.sh

# Or with custom version:
VERSION=v0.1.0-beta ./build-allinone.sh
```

This creates:
- `genmind/creative-campaign:v0.0.1-beta`
- `genmind/creative-campaign:latest`

### Push to Docker Hub:
```bash
docker login

# Push specific version
docker push genmind/creative-campaign:v0.0.1-beta

# Push latest
docker push genmind/creative-campaign:latest

# Or push all tags
docker push genmind/creative-campaign --all-tags
```

### Users can then run:

# Run with all ports exposed
```bash
./run-allinone.sh sk-your-api-key-here
```
```bash
docker run -d \
  --name creative-campaign \
  -p 8000:8000 \
  -p 8501:8501 \
  -p 8081:8081 \
  -p 8222:8222 \
  -p 9000:9000 \
  -p 9001:9001 \
  -p 9002:9002 \
  -v creative-data:/data \
  -e OPENAI_API_KEY=YOUR-OPENAI_API_KEY
```

```bash
# Pull from Docker Hub
docker pull genmind/creative-campaign:v0.0.1-beta

# Run
docker run -d \
  --name creative-campaign \
  -p 8501:8501 \
  -v creative-data:/data \
  -e OPENAI_API_KEY="sk-xxx" \
  genmind/creative-campaign:v0.0.1-beta
```

### Docker Hub Repository
```
https://hub.docker.com/r/genmind/creative-campaign
```

---

## 📏 Container Specifications

| Metric | Value |
|--------|-------|
| **Base Image** | python:3.11-slim |
| **Image Size** | ~1.0-1.2 GB |
| **Memory Usage (Idle)** | ~500 MB |
| **Memory Usage (Active)** | ~2-3 GB |
| **Startup Time** | ~30-60 seconds |
| **Disk Space (with data)** | ~2-5 GB |

---

## 🎯 Use Cases

### ✅ Perfect For:
- **Demos & POCs** - One command deployment
- **Development** - Full stack in one container
- **Testing** - Isolated environment
- **Quick deployments** - No infrastructure setup
- **Laptop development** - Offline work possible

### ⚠️ Consider Multi-Container For:
- **Production at scale** - Need horizontal scaling
- **High availability** - Need redundancy
- **Managed services** - Using AWS RDS, ElastiCache, etc.
- **Kubernetes** - Native container orchestration

---

## 🆚 Comparison: All-in-One vs Multi-Container

| Feature | All-in-One | Multi-Container |
|---------|------------|-----------------|
| **Startup Command** | 1 command | 8+ services |
| **External Dependencies** | None | MongoDB, NATS, MinIO |
| **Memory Usage** | 2-3 GB | 3-4 GB total |
| **Scaling** | Limited | Excellent |
| **Portability** | Excellent | Good |
| **Production Ready** | POC/Dev | Yes |
| **Backup/Restore** | Simple | Per-service |

---

## 📚 Additional Resources

- [Main README](../README.md) - Project overview
- [Architecture Docs](../docs/architecture.md) - System design
- [Multi-Container Setup](docker-compose.yml) - Scalable deployment

---

## 🐛 Known Limitations

1. **No horizontal scaling** - Single container, single instance
2. **MongoDB not replicated** - No automatic failover
3. **NATS messages in-memory only** - If container stops, queued messages lost
4. **Large image size** - ~1GB (vs ~500MB for service-only images)

---

## 💡 Tips & Best Practices

### Development Workflow
```bash
# Start container
docker compose -f docker-compose-allinone.yml up -d

# Open Web UI
open http://localhost:8501

# Watch logs in real-time
docker compose -f docker-compose-allinone.yml logs -f

# Make code changes (rebuild required)
docker compose -f docker-compose-allinone.yml build
docker compose -f docker-compose-allinone.yml up -d
```

### Production Deployment
```bash
# Use specific version tag
docker run -d yourusername/creative-campaign:v1.0 ...

# Always use named volumes
-v creative-prod-data:/data

# Set resource limits
--memory=4g --cpus=2

# Enable auto-restart
--restart=unless-stopped
```

### Monitoring
```bash
# Check resource usage
docker stats creative-campaign

# Check health status
docker inspect creative-campaign | grep -A 10 Health

# Export metrics (if needed)
curl http://localhost:8000/metrics
```

---

## 📞 Support

- 🐛 **Issues**: GitHub Issues
- 📖 **Documentation**: [docs/](../docs/)
- 💬 **Discussions**: GitHub Discussions

---

**Built with ❤️ for easy deployment**
