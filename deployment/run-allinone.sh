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
docker pull gsantopaolo/creative-campaign:v0.0.3-beta
echo ""

# Run the container
echo "🐳 Starting container..."
docker run -d \
  --name creative-campaign \
  -p 8000:8000 \
  -p 8501:8501 \
  -p 8081:8081 \
  -p 9001:9001 \
  -p 9002:9002 \
  -v creative-data:/data \
  -e OPENAI_API_KEY="${OPENAI_API_KEY}" \
  gsantopaolo/creative-campaign:v0.0.3-beta

echo ""
echo "⏳ Waiting for services to start..."
echo ""

# Wait for container to be running
for i in {1..30}; do
    if [ "$(docker ps -q -f name=creative-campaign -f status=running)" ]; then
        break
    fi
    sleep 1
done

# Wait for services to be ready (check if ports are responding)
echo "🔍 Checking service health..."
sleep 5

# Check if Streamlit is responding
for i in {1..30}; do
    if curl -s http://localhost:8501 > /dev/null 2>&1; then
        echo "   ✅ Web UI is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "   ⚠️  Web UI not responding yet (may still be starting)"
    fi
    sleep 2
done

# Check if API is responding
for i in {1..30}; do
    if curl -s http://localhost:8000/healthz > /dev/null 2>&1; then
        echo "   ✅ API is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "   ⚠️  API not responding yet (may still be starting)"
    fi
    sleep 2
done

echo ""
echo "✅ CreativeCampaign-Agent is running!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 Web UIs Available:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📱 Main Web UI:       http://localhost:8501"
echo "   Interactive interface for creating campaigns"
echo ""
echo "🔌 API Gateway:       http://localhost:8000"
echo "   REST API endpoint"
echo ""
echo "📚 API Documentation: http://localhost:8000/docs"
echo "   Swagger/OpenAPI docs"
echo ""
echo "🗄️  MongoDB UI:        http://localhost:8081"
echo "   Database explorer (admin/admin)"
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
echo "📋 View logs:    docker logs -f creative-campaign"
echo "🛑 Stop:         docker stop creative-campaign"
echo "🗑️  Remove:       docker rm -f creative-campaign"
echo ""
echo "💡 Tip: To restart with a different API key:"
echo "   ./run-allinone.sh sk-your-new-key-here"
echo ""
