#!/bin/bash
# Docker build script with model caching

echo "🚀 Building ChatterboxTTS Docker image with pre-cached models..."

# Build with progress output
docker build \
    --progress=plain \
    -t chatterbox-whisper:latest \
    -t chatterbox-whisper:$(date +%Y%m%d) \
    .

if [ $? -eq 0 ]; then
    echo "✅ Docker build completed successfully!"
    echo "📊 Image sizes:"
    docker images | grep chatterbox-whisper
    echo ""
    echo "🏃 To run the container:"
    echo "docker run -d -p 7860:7860 -p 7861:7861 chatterbox-whisper:latest"
else
    echo "❌ Docker build failed!"
    exit 1
fi
