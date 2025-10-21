#!/bin/bash
# ============================================================================
# CreativeCampaign-Agent - All-in-One Container Entrypoint
# ============================================================================
set -e

echo "🚀 Starting CreativeCampaign-Agent All-in-One Container..."
echo ""

# ============================================================================
# Create data directories
# ============================================================================
echo "📁 Initializing data directories..."
mkdir -p /data/mongodb /data/nats /data/minio
echo "  ✅ Data directories ready"
echo ""

# ============================================================================
# Initialize MongoDB (first time only)
# ============================================================================
if [ ! -f /data/mongodb/.initialized ]; then
    echo "🗄️  Initializing MongoDB for first time..."
    
    # Start MongoDB temporarily to create initial data structures
    /usr/local/bin/mongod --dbpath=/data/mongodb --bind_ip_all --quiet --logpath=/dev/null --fork
    
    # Wait for MongoDB to initialize (simple wait, MongoDB will be managed by supervisord)
    echo "  ⏳ Waiting for MongoDB to initialize..."
    sleep 5
    
    # Stop MongoDB gracefully (supervisord will restart it)
    echo "  🛑 Stopping temporary MongoDB..."
    /usr/local/bin/mongod --dbpath=/data/mongodb --shutdown || killall mongod 2>/dev/null || true
    sleep 3
    
    # Mark as initialized
    touch /data/mongodb/.initialized
    echo "  ✅ MongoDB initialized"
else
    echo "✅ MongoDB already initialized (skipping setup)"
fi
echo ""

# ============================================================================
# Initialize MinIO (create bucket if needed)
# ============================================================================
if [ ! -f /data/minio/.initialized ]; then
    echo "📦 Initializing MinIO..."
    
    # Start MinIO temporarily in background
    /usr/local/bin/minio server /data/minio --address=:9000 --console-address=:9001 > /dev/null 2>&1 &
    MINIO_PID=$!
    
    # Wait for MinIO to be ready
    echo "  ⏳ Waiting for MinIO to start..."
    for i in {1..30}; do
        if curl -sf http://localhost:9000/minio/health/live > /dev/null 2>&1; then
            echo "  ✅ MinIO ready"
            break
        fi
        sleep 1
    done
    
    # Install MinIO client
    wget -q https://dl.min.io/client/mc/release/linux-$(dpkg --print-architecture)/mc -O /usr/local/bin/mc
    chmod +x /usr/local/bin/mc
    
    # Configure MinIO client and create bucket
    /usr/local/bin/mc alias set local http://localhost:9000 minioadmin minioadmin > /dev/null 2>&1
    /usr/local/bin/mc mb local/creative-assets --ignore-existing > /dev/null 2>&1
    /usr/local/bin/mc anonymous set download local/creative-assets > /dev/null 2>&1
    
    # Stop temporary MinIO
    kill $MINIO_PID
    wait $MINIO_PID 2>/dev/null || true
    
    # Mark as initialized
    touch /data/minio/.initialized
    echo "  ✅ MinIO initialized with bucket 'creative-assets'"
else
    echo "✅ MinIO already initialized"
fi
echo ""

# ============================================================================
# Display configuration
# ============================================================================
echo "🎯 Configuration:"
echo "  📂 Data directory: /data"
echo "  🗄️  MongoDB: localhost:27017"
echo "  📨 NATS: localhost:4222"
echo "  📦 MinIO: localhost:9000"
echo ""

echo "🌐 Access URLs:"
echo "  🎨 Main Application: http://localhost:8501"
echo "  🔌 API Gateway: http://localhost:8000"
echo "  📚 API Docs: http://localhost:8000/docs"
echo "  🗄️  MongoDB UI: http://localhost:8081 (admin/admin)"
echo "  📦 MinIO Console: http://localhost:9001 (minioadmin/minioadmin)"
echo "  🎛️  Supervisord UI: http://localhost:9002 (admin/admin)"
echo ""

# ============================================================================
# Apply environment variables with defaults
# ============================================================================
export OPENAI_API_KEY="${OPENAI_API_KEY:-}"
export OPENAI_TEXT_MODEL="${OPENAI_TEXT_MODEL:-gpt-4o-mini}"
export OPENAI_IMAGE_MODEL="${OPENAI_IMAGE_MODEL:-dall-e-3}"

if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  WARNING: OPENAI_API_KEY not set!"
    echo "   Set it with: -e OPENAI_API_KEY=sk-your-key"
    echo ""
fi

# ============================================================================
# Update supervisord config with actual OPENAI_API_KEY value
# ============================================================================
if [ -n "$OPENAI_API_KEY" ]; then
    # Replace placeholder with actual API key in supervisord config
    sed -i "s|OPENAI_API_KEY=\"%(ENV_OPENAI_API_KEY)s\"|OPENAI_API_KEY=\"${OPENAI_API_KEY}\"|g" /etc/supervisor/conf.d/supervisord.conf
fi

# ============================================================================
# Start Supervisord
# ============================================================================
echo "🎬 Starting all services with Supervisord..."
echo ""

exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
