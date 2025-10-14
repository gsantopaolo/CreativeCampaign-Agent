#!/bin/bash

# ============================================================================
# CreativeCampaign-Agent - All-in-One Container Runner
# ============================================================================
# Usage:
# ./run-allinone.sh sk-proj-abc123...
# or:
# export OPENAI_API_KEY="sk-your-key-here"
# ./run-allinone.sh
# ============================================================================

# Parse command line arguments
if [ "$1" ]; then
    OPENAI_API_KEY="$1"
fi

echo "🚀 Starting CreativeCampaign-Agent All-in-One Container..."
echo ""

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: OPENAI_API_KEY not provided"
    echo "   Usage: ./run-allinone.sh [OPENAI_API_KEY]"
    echo "   Or:    export OPENAI_API_KEY=sk-xxx && ./run-allinone.sh"
    echo ""
    echo "   The container will use the default key (not recommended for production)"
    echo ""
else
    echo "✅ Using provided OpenAI API key: ${OPENAI_API_KEY:0:20}..."
    echo ""
fi

# Remove existing container if it exists
if [ "$(docker ps -aq -f name=creative-campaign)" ]; then
    echo "🗑️  Removing existing creative-campaign container..."
    docker rm -f creative-campaign
    echo ""
fi

# Pull latest image
echo "📥 Pulling latest image..."
docker pull gsantopaolo/creative-campaign:latest
echo ""

# Run the container
echo "🐳 Starting container..."
CONTAINER_ID=$(docker run -d \
  --name creative-campaign \
  -p 8000:8000 \
  -p 8501:8501 \
  -p 8081:8081 \
  -p 8222:8222 \
  -p 9000:9000 \
  -p 9001:9001 \
  -p 9002:9002 \
  -v creative-data:/data \
  -e OPENAI_API_KEY="${OPENAI_API_KEY}" \
  gsantopaolo/creative-campaign:latest)

echo ""
echo "⏳ Waiting for services to start (timeout: 120s)..."
echo ""

# Wait for container to be running with timeout
TIMEOUT=120
ELAPSED=0
CONTAINER_STARTED=false

for i in {1..120}; do
    if [ "$(docker ps -q -f name=creative-campaign -f status=running)" ]; then
        CONTAINER_STARTED=true
        break
    fi
    
    # Check if container exited
    if [ "$(docker ps -aq -f name=creative-campaign -f status=exited)" ]; then
        echo "❌ Container exited unexpectedly!"
        echo ""
        echo "📋 Last 50 lines of logs:"
        docker logs --tail 50 creative-campaign
        echo ""
        echo "💡 Try: docker logs creative-campaign (for full logs)"
        exit 1
    fi
    
    sleep 1
    ELAPSED=$i
done

if [ "$CONTAINER_STARTED" = false ]; then
    echo "❌ Container failed to start within ${TIMEOUT} seconds"
    echo ""
    echo "📋 Container logs:"
    docker logs creative-campaign
    exit 1
fi

# Wait for services to be ready (check if ports are responding)
echo "🔍 Checking service health..."
sleep 5

# Check if Streamlit is responding (timeout: 60s)
STREAMLIT_READY=false
for i in {1..30}; do
    if curl -s http://localhost:8501 > /dev/null 2>&1; then
        echo "   ✅ Web UI is ready"
        STREAMLIT_READY=true
        break
    fi
    sleep 2
done

if [ "$STREAMLIT_READY" = false ]; then
    echo "   ⚠️  Web UI not responding after 60s (may still be starting)"
fi

# Check if API is responding (timeout: 60s)
API_READY=false
for i in {1..30}; do
    if curl -s http://localhost:8000/healthz > /dev/null 2>&1 || curl -s http://localhost:8000 > /dev/null 2>&1; then
        echo "   ✅ API is ready"
        API_READY=true
        break
    fi
    sleep 2
done

if [ "$API_READY" = false ]; then
    echo "   ⚠️  API not responding after 60s (may still be starting)"
fi

echo ""
echo "✅ CreativeCampaign-Agent is running!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 Web UIs Available:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📱 Web Application:   http://localhost:8501"
echo "   Interactive interface for creating campaigns"
echo ""
echo "🗄️  MongoDB UI:        http://localhost:8081"
echo "   Database explorer (admin/admin)"
echo ""
echo "📨 NATS Monitor:      http://localhost:8222"
echo "   Message queue stats"
echo ""
echo "💾 MinIO Console:     http://localhost:9001"
echo "   S3 storage manager (minioadmin/minioadmin)"
echo ""
echo "⚙️  Process Manager:   http://localhost:9002"
echo "   Supervisord dashboard (admin/admin)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Container Status:"
docker ps --filter name=creative-campaign --format "   {{.Names}} - {{.Status}}"
echo ""

# Show startup summary
if [ "$STREAMLIT_READY" = true ] && [ "$API_READY" = true ]; then
    echo "✨ All critical services are healthy!"
elif [ "$STREAMLIT_READY" = false ] && [ "$API_READY" = false ]; then
    echo "⚠️  Warning: Both Web UI and API are not responding yet"
    echo "   Check logs: docker logs -f creative-campaign"
elif [ "$STREAMLIT_READY" = false ]; then
    echo "⚠️  Warning: Web UI is not responding yet"
    echo "   Check logs: docker logs -f creative-campaign"
elif [ "$API_READY" = false ]; then
    echo "⚠️  Warning: API is not responding yet"
    echo "   Check logs: docker logs -f creative-campaign"
fi
echo ""

echo "📋 Useful commands:"
echo "   View logs:    docker logs -f creative-campaign"
echo "   Stop:         docker stop creative-campaign"
echo "   Remove:       docker rm -f creative-campaign"
echo "   Restart:      docker restart creative-campaign"
echo ""
echo "💡 Tip: To restart with a different API key:"
echo "   ./run-allinone.sh sk-your-new-key-here"
echo ""
