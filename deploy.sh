#!/bin/bash

# Quick deployment script for various platforms
set -e

DOCKER_HUB_USERNAME="${DOCKER_HUB_USERNAME:-your-username}"
IMAGE_NAME="chatterbox-whisper"
TAG="${TAG:-latest}"
FULL_IMAGE_NAME="${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${TAG}"

echo "🚀 Quick Deploy Script for Chatterbox Whisper"
echo "============================================="

# Function to deploy locally
deploy_local() {
    echo "🏠 Deploying locally..."
    docker run --rm -d \
        --name chatterbox-whisper-local \
        -p 7860:7860 \
        -p 7861:7861 \
        ${FULL_IMAGE_NAME}
    
    echo "✅ Local deployment started!"
    echo "🌐 FastAPI: http://localhost:7860/docs"
    echo "🌐 Gradio: http://localhost:7861"
    echo "🛑 To stop: docker stop chatterbox-whisper-local"
}

# Function to deploy with GPU
deploy_gpu() {
    echo "🎮 Deploying with GPU support..."
    docker run --rm -d \
        --name chatterbox-whisper-gpu \
        --gpus all \
        -p 7860:7860 \
        -p 7861:7861 \
        ${FULL_IMAGE_NAME}
    
    echo "✅ GPU deployment started!"
    echo "🌐 FastAPI: http://localhost:7860/docs"
    echo "🌐 Gradio: http://localhost:7861"
    echo "🛑 To stop: docker stop chatterbox-whisper-gpu"
}

# Function to generate docker-compose
generate_compose() {
    cat > docker-compose.yml << EOF
version: '3.8'

services:
  chatterbox-whisper:
    image: ${FULL_IMAGE_NAME}
    ports:
      - "7860:7860"
      - "7861:7861"
    environment:
      - PYTHONUNBUFFERED=1
    volumes:
      - ./tmp:/tmp/audio
    restart: unless-stopped
    
  # GPU version (uncomment if you have GPU support)
  # chatterbox-whisper-gpu:
  #   image: ${FULL_IMAGE_NAME}
  #   ports:
  #     - "7860:7860"
  #     - "7861:7861"
  #   environment:
  #     - PYTHONUNBUFFERED=1
  #   volumes:
  #     - ./tmp:/tmp/audio
  #   deploy:
  #     resources:
  #       reservations:
  #         devices:
  #           - driver: nvidia
  #             count: 1
  #             capabilities: [gpu]
  #   restart: unless-stopped
EOF
    
    echo "✅ Generated docker-compose.yml"
    echo "🚀 To start: docker-compose up -d"
    echo "🛑 To stop: docker-compose down"
}

# Menu
echo ""
echo "Choose deployment option:"
echo "1) Deploy locally (CPU only)"
echo "2) Deploy with GPU support"
echo "3) Generate docker-compose.yml"
echo "4) Pull latest image from Docker Hub"
echo "5) Show running containers"

read -p "Enter choice (1-5): " choice

case $choice in
    1)
        deploy_local
        ;;
    2)
        deploy_gpu
        ;;
    3)
        generate_compose
        ;;
    4)
        echo "📥 Pulling latest image..."
        docker pull ${FULL_IMAGE_NAME}
        echo "✅ Image pulled successfully!"
        ;;
    5)
        echo "🔍 Running containers:"
        docker ps --filter "name=chatterbox-whisper"
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac
