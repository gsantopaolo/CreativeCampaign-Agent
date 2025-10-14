#!/bin/bash
# ============================================================================
# Build script for all-in-one container
# ============================================================================

set -e

# Version configuration
VERSION="${VERSION:-v0.0.1-beta}"
IMAGE_NAME="genmind/creative-campaign"

echo "🏗️  Building CreativeCampaign-Agent All-in-One Container..."
echo "📦 Image: ${IMAGE_NAME}:${VERSION}"
echo ""

# Build the image with multiple tags
echo "📦 Building Docker image (no cache)..."
cd "$(dirname "$0")/.."
docker build --no-cache -f Dockerfile.allinone \
  -t ${IMAGE_NAME}:${VERSION} \
  -t ${IMAGE_NAME}:latest \
  .

echo ""
echo "✅ Build complete!"
echo ""
echo "🚀 To run the container:"
echo ""
echo "   Using Docker Compose:"
echo "   export OPENAI_API_KEY='sk-your-key-here'"
echo "   docker compose -f deployment/docker-compose-allinone.yml up -d"
echo ""
echo "   Or with docker run:"
echo "   docker run -d \\"
echo "     --name creative-campaign \\"
echo "     -p 8000:8000 -p 8501:8501 -p 8081:8081 -p 9001:9001 -p 9002:9002 \\"
echo "     -v creative-campaign-data:/data \\"
echo "     -e OPENAI_API_KEY=\$OPENAI_API_KEY \\"
echo "     ${IMAGE_NAME}:${VERSION}"
echo ""
echo "🌐 Access URLs:"
echo "   Main App:     http://localhost:8501"
echo "   API Docs:     http://localhost:8000/docs"
echo "   MongoDB UI:   http://localhost:8081 (admin/admin)"
echo "   MinIO Console: http://localhost:9001 (minioadmin/minioadmin)"
echo "   Process Manager: http://localhost:9002 (admin/admin)"
echo ""

# docker login
# docker push genmind/creative-campaign --all-tags