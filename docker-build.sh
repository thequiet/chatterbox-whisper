#!/bin/bash

# Docker Hub build and publish script
set -e

# Configuration
DOCKER_HUB_USERNAME="${DOCKER_HUB_USERNAME:-your-username}"
IMAGE_NAME="chatterbox-whisper"
TAG="${TAG:-latest}"
FULL_IMAGE_NAME="${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${TAG}"

echo "🐳 Building Docker image for Docker Hub..."
echo "Image: ${FULL_IMAGE_NAME}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Build the image
echo "📦 Building image..."
docker build -t ${FULL_IMAGE_NAME} .

# Also tag as latest if not already latest
if [ "${TAG}" != "latest" ]; then
    docker tag ${FULL_IMAGE_NAME} ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:latest
fi

echo "✅ Build completed successfully!"
echo "Image tagged as: ${FULL_IMAGE_NAME}"

# Ask if user wants to push to Docker Hub
read -p "🚀 Do you want to push to Docker Hub? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔐 Logging into Docker Hub..."
    docker login
    
    echo "📤 Pushing to Docker Hub..."
    docker push ${FULL_IMAGE_NAME}
    
    if [ "${TAG}" != "latest" ]; then
        docker push ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:latest
    fi
    
    echo "✅ Successfully pushed to Docker Hub!"
    echo "🌐 Your image is available at: https://hub.docker.com/r/${DOCKER_HUB_USERNAME}/${IMAGE_NAME}"
else
    echo "ℹ️  Image built locally. To push later, run:"
    echo "   docker login"
    echo "   docker push ${FULL_IMAGE_NAME}"
fi

echo ""
echo "🏃 To run the image locally:"
echo "   docker run --rm -p 7860:7860 -p 7861:7861 ${FULL_IMAGE_NAME}"
echo ""
echo "🏃 To run with GPU support:"
echo "   docker run --rm --gpus all -p 7860:7860 -p 7861:7861 ${FULL_IMAGE_NAME}"
