#!/bin/bash

# Docker Hub Automated Build Setup Script
set -e

DOCKER_HUB_USERNAME="${DOCKER_HUB_USERNAME:-}"
REPO_NAME="chatterbox-whisper"

echo "🐳 Docker Hub Automated Build Setup"
echo "===================================="

# Function to check if Docker Hub username is set
check_username() {
    if [[ -z "$DOCKER_HUB_USERNAME" ]]; then
        read -p "📝 Enter your Docker Hub username: " DOCKER_HUB_USERNAME
        if [[ -z "$DOCKER_HUB_USERNAME" ]]; then
            echo "❌ Username is required"
            exit 1
        fi
    fi
}

# Function to setup GitHub repository
setup_github() {
    echo "📁 Setting up GitHub repository..."
    
    # Initialize git if needed
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        echo "🆕 Initializing git repository..."
        git init
        git add .
        git commit -m "Initial commit - Chatterbox Whisper for Docker Hub"
    fi
    
    # Check if remote exists
    if ! git remote get-url origin > /dev/null 2>&1; then
        echo "🔗 Adding GitHub remote..."
        read -p "📝 Enter your GitHub username: " github_username
        if [[ -z "$github_username" ]]; then
            echo "❌ GitHub username is required"
            exit 1
        fi
        
        git remote add origin https://github.com/$github_username/$REPO_NAME.git
        
        echo "⚠️  Make sure to create the repository on GitHub:"
        echo "   https://github.com/new"
        echo "   Repository name: $REPO_NAME"
        echo ""
        read -p "Press Enter when you've created the GitHub repository..."
    fi
    
    echo "📤 Pushing to GitHub..."
    git push -u origin main
    
    echo "✅ GitHub repository is ready!"
    echo "🔗 Repository URL: $(git remote get-url origin)"
}

# Function to create Docker Hub repository
setup_dockerhub() {
    check_username
    
    echo ""
    echo "🐳 Docker Hub Repository Setup"
    echo "=============================="
    echo ""
    echo "📋 Manual steps to complete on Docker Hub:"
    echo ""
    echo "1. 🌐 Go to: https://hub.docker.com/"
    echo "2. ➕ Click 'Create Repository'"
    echo "3. 📝 Repository name: $REPO_NAME"
    echo "4. 🔗 Choose 'Connected to GitHub'"
    echo "5. 🔍 Select your GitHub account and repository"
    echo "6. ⚙️  Configure build rules (see details below)"
    echo ""
    
    echo "🔧 Build Rules Configuration:"
    echo "=========================="
    echo ""
    printf "%-12s | %-15s | %-12s | %-18s | %s\n" "Type" "Source" "Docker Tag" "Dockerfile" "Context"
    echo "-------------|-----------------|--------------|-------------------|--------"
    printf "%-12s | %-15s | %-12s | %-18s | %s\n" "Branch" "main" "latest" "Dockerfile" "/"
    printf "%-12s | %-15s | %-12s | %-18s | %s\n" "Branch" "develop" "dev" "Dockerfile" "/"
    printf "%-12s | %-15s | %-12s | %-18s | %s\n" "Tag" "/^v([0-9.]+)$/" "{\1}" "Dockerfile" "/"
    printf "%-12s | %-15s | %-12s | %-18s | %s\n" "Tag" "/^v([0-9.]+)$/" "{\1}-gpu" "Dockerfile" "/"
    echo ""
    
    echo "🔧 Advanced Settings:"
    echo "==================="
    echo "• Build timeout: 7200 seconds (2 hours)"
    echo "• Build caching: ✅ Enabled"
    echo "• Automatically build on push: ✅ Enabled"
    echo ""
    
    echo "🔑 Environment Variables (Optional):"
    echo "=================================="
    echo "• DOCKER_BUILDKIT=1"
    echo "• BUILDKIT_INLINE_CACHE=1"
    echo ""
    
    echo "Your repository will be available at:"
    echo "🔗 https://hub.docker.com/r/$DOCKER_HUB_USERNAME/$REPO_NAME"
}

# Function to test the setup
test_setup() {
    check_username
    
    echo "🧪 Testing Docker Hub Automated Build Setup"
    echo "============================================"
    
    # Create a test commit
    echo "# Test commit for Docker Hub build - $(date)" >> test-build.md
    git add test-build.md
    git commit -m "Test commit to trigger Docker Hub build"
    git push origin main
    
    echo ""
    echo "✅ Test commit pushed!"
    echo "🔍 Check build status at:"
    echo "   https://hub.docker.com/r/$DOCKER_HUB_USERNAME/$REPO_NAME/builds"
    echo ""
    echo "⏱️  Docker Hub builds typically take 10-15 minutes"
    echo "📧 You'll receive email notifications when builds complete"
    
    # Clean up test file
    rm -f test-build.md
    git add test-build.md
    git commit -m "Clean up test file"
    git push origin main
}

# Function to create a release tag
create_release() {
    echo "🏷️  Creating Release Tag"
    echo "======================="
    
    read -p "📝 Enter version number (e.g., 1.0.0): " version
    if [[ -z "$version" ]]; then
        echo "❌ Version is required"
        exit 1
    fi
    
    # Validate version format
    if [[ ! $version =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        echo "❌ Version must be in format X.Y.Z (e.g., 1.0.0)"
        exit 1
    fi
    
    echo "📝 Creating git tag v$version..."
    git tag "v$version"
    git push origin "v$version"
    
    echo ""
    echo "✅ Release tag created!"
    echo "🏷️  Tag: v$version"
    echo "🔍 This will trigger builds for:"
    echo "   • $DOCKER_HUB_USERNAME/$REPO_NAME:$version"
    echo "   • $DOCKER_HUB_USERNAME/$REPO_NAME:$version-gpu"
    echo ""
    echo "⏱️  Check build progress at:"
    echo "   https://hub.docker.com/r/$DOCKER_HUB_USERNAME/$REPO_NAME/builds"
}

# Function to show status
show_status() {
    check_username
    
    echo "📊 Docker Hub Repository Status"
    echo "==============================="
    echo ""
    echo "🔗 Repository: https://hub.docker.com/r/$DOCKER_HUB_USERNAME/$REPO_NAME"
    echo "🔍 Builds: https://hub.docker.com/r/$DOCKER_HUB_USERNAME/$REPO_NAME/builds"
    echo "📊 Tags: https://hub.docker.com/r/$DOCKER_HUB_USERNAME/$REPO_NAME/tags"
    echo ""
    
    # Check if we can pull the image
    echo "🧪 Testing image availability..."
    if docker pull "$DOCKER_HUB_USERNAME/$REPO_NAME:latest" >/dev/null 2>&1; then
        echo "✅ Latest image is available and pullable"
        
        # Get image info
        echo ""
        echo "📋 Image Information:"
        docker image inspect "$DOCKER_HUB_USERNAME/$REPO_NAME:latest" --format '
🏷️  Tag: {{.RepoTags}}
📅 Created: {{.Created}}
💾 Size: {{.Size}} bytes
🏗️  Architecture: {{.Architecture}}
🖥️  OS: {{.Os}}'
    else
        echo "⚠️  Latest image not found. Build may still be in progress."
    fi
}

# Main menu
echo ""
echo "Choose an option:"
echo "1) 📁 Setup GitHub repository"
echo "2) 🐳 Setup Docker Hub automated builds"
echo "3) 🧪 Test build (trigger with test commit)"
echo "4) 🏷️  Create release tag"
echo "5) 📊 Show repository status"
echo "6) 🔧 Set Docker Hub username"

read -p "Enter choice (1-6): " choice

case $choice in
    1)
        setup_github
        ;;
    2)
        setup_dockerhub
        ;;
    3)
        test_setup
        ;;
    4)
        create_release
        ;;
    5)
        show_status
        ;;
    6)
        read -p "Enter your Docker Hub username: " username
        echo "export DOCKER_HUB_USERNAME='$username'" >> ~/.zshrc
        echo "✅ Username saved to ~/.zshrc"
        echo "🔄 Restart your terminal or run: source ~/.zshrc"
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac
