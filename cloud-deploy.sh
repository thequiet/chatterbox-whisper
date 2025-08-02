#!/bin/bash

# Cloud-first deployment script - no local building required
set -e

DOCKER_HUB_USERNAME="${DOCKER_HUB_USERNAME:-}"
IMAGE_NAME="chatterbox-whisper"
DEFAULT_TAG="latest"

echo "☁️  Cloud Build & Deploy for Chatterbox Whisper"
echo "==============================================="

# Function to check if Docker Hub username is set
check_username() {
    if [[ -z "$DOCKER_HUB_USERNAME" ]]; then
        echo "❌ Please set your Docker Hub username:"
        echo "   export DOCKER_HUB_USERNAME='your-username'"
        echo "   OR edit this script to set it permanently"
        exit 1
    fi
}

# Function to trigger GitHub Actions build
trigger_github_build() {
    echo "🚀 Triggering GitHub Actions cloud build..."
    
    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        echo "❌ Not in a git repository. Please initialize git and push to GitHub first."
        exit 1
    fi
    
    # Get current branch
    BRANCH=$(git rev-parse --abbrev-ref HEAD)
    
    echo "📝 Current branch: $BRANCH"
    echo "💾 Committing any pending changes..."
    
    # Add all changes and commit
    git add .
    if git diff --staged --quiet; then
        echo "ℹ️  No changes to commit"
    else
        read -p "📝 Enter commit message (or press Enter for default): " commit_msg
        if [[ -z "$commit_msg" ]]; then
            commit_msg="Cloud build trigger - $(date)"
        fi
        git commit -m "$commit_msg"
    fi
    
    echo "📤 Pushing to trigger cloud build..."
    git push origin $BRANCH
    
    # Get repository URL for GitHub Actions
    REPO_URL=$(git config --get remote.origin.url)
    if [[ $REPO_URL == *"github.com"* ]]; then
        # Extract owner/repo from URL
        REPO_PATH=$(echo $REPO_URL | sed 's/.*github\.com[:/]\([^/]*\/[^/]*\)\.git.*/\1/')
        ACTIONS_URL="https://github.com/$REPO_PATH/actions"
        
        echo ""
        echo "✅ Build triggered! Monitor progress at:"
        echo "🔗 $ACTIONS_URL"
        echo ""
        echo "⏱️  The cloud build typically takes 5-10 minutes"
        echo "📦 Your image will be available at: https://hub.docker.com/r/$DOCKER_HUB_USERNAME/$IMAGE_NAME"
    else
        echo "⚠️  Repository doesn't appear to be on GitHub"
    fi
}

# Function to deploy from Docker Hub
deploy_from_hub() {
    check_username
    
    FULL_IMAGE_NAME="$DOCKER_HUB_USERNAME/$IMAGE_NAME:$DEFAULT_TAG"
    
    echo "📥 Pulling latest image from Docker Hub..."
    if ! docker pull $FULL_IMAGE_NAME; then
        echo "❌ Failed to pull image. Make sure:"
        echo "   1. Your Docker Hub username is correct"
        echo "   2. The image has been built and pushed"
        echo "   3. You have internet connectivity"
        exit 1
    fi
    
    echo "🏃 Starting container..."
    
    # Stop any existing container
    docker stop chatterbox-whisper-cloud 2>/dev/null || true
    docker rm chatterbox-whisper-cloud 2>/dev/null || true
    
    # Check for GPU support
    if docker run --rm --gpus all hello-world >/dev/null 2>&1; then
        echo "🎮 GPU support detected - running with GPU acceleration"
        docker run -d \
            --name chatterbox-whisper-cloud \
            --gpus all \
            -p 7860:7860 \
            -p 7861:7861 \
            --restart unless-stopped \
            $FULL_IMAGE_NAME
    else
        echo "💻 Running with CPU only"
        docker run -d \
            --name chatterbox-whisper-cloud \
            -p 7860:7860 \
            -p 7861:7861 \
            --restart unless-stopped \
            $FULL_IMAGE_NAME
    fi
    
    echo ""
    echo "✅ Deployment complete!"
    echo "🌐 FastAPI: http://localhost:7860/docs"
    echo "🌐 Gradio: http://localhost:7861"
    echo "❤️  Health: http://localhost:7860/health"
    echo ""
    echo "📊 Container status:"
    docker ps --filter "name=chatterbox-whisper-cloud"
    
    echo ""
    echo "🛑 To stop: docker stop chatterbox-whisper-cloud"
}

# Function to create/update GitHub repository
setup_github_repo() {
    echo "📁 Setting up GitHub repository for cloud builds..."
    
    # Check if GitHub CLI is installed
    if ! command -v gh &> /dev/null; then
        echo "❌ GitHub CLI not found. Please install it:"
        echo "   brew install gh"
        echo "   OR visit: https://github.com/cli/cli#installation"
        exit 1
    fi
    
    # Check if user is logged in
    if ! gh auth status >/dev/null 2>&1; then
        echo "🔐 Please log in to GitHub:"
        gh auth login
    fi
    
    # Initialize git if needed
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        echo "🆕 Initializing git repository..."
        git init
        git add .
        git commit -m "Initial commit - Chatterbox Whisper"
    fi
    
    # Create GitHub repository
    read -p "📝 Enter repository name (default: chatterbox-whisper): " repo_name
    repo_name=${repo_name:-chatterbox-whisper}
    
    echo "🚀 Creating GitHub repository..."
    gh repo create $repo_name --public --push --source .
    
    echo ""
    echo "✅ Repository created! Now set up secrets:"
    echo "1. Go to: https://github.com/$(gh api user --jq .login)/$repo_name/settings/secrets/actions"
    echo "2. Add these secrets:"
    echo "   - DOCKER_HUB_USERNAME: $DOCKER_HUB_USERNAME"
    echo "   - DOCKER_HUB_ACCESS_TOKEN: (create at hub.docker.com)"
    echo ""
    echo "Then run: $0 build"
}

# Function to check build status
check_build_status() {
    echo "📊 Checking latest build status..."
    
    if ! command -v gh &> /dev/null; then
        echo "❌ GitHub CLI not found. Install with: brew install gh"
        exit 1
    fi
    
    # Get latest workflow run
    gh run list --limit 1 --json conclusion,status,url,displayTitle
}

# Main menu
echo ""
echo "Choose an option:"
echo "1) 🚀 Trigger cloud build (GitHub Actions)"
echo "2) 📥 Deploy latest image from Docker Hub"
echo "3) 📁 Setup GitHub repository for cloud builds"
echo "4) 📊 Check build status"
echo "5) 🔧 Set Docker Hub username"

read -p "Enter choice (1-5): " choice

case $choice in
    1)
        trigger_github_build
        ;;
    2)
        deploy_from_hub
        ;;
    3)
        setup_github_repo
        ;;
    4)
        check_build_status
        ;;
    5)
        read -p "Enter your Docker Hub username: " username
        echo "export DOCKER_HUB_USERNAME='$username'" >> ~/.zshrc
        echo "✅ Username saved! Restart your terminal or run:"
        echo "   source ~/.zshrc"
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac
