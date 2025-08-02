#!/bin/bash

# Quick Docker Hub setup for 2025 (no more GitHub integration)
set -e

DOCKER_HUB_USERNAME="${DOCKER_HUB_USERNAME:-}"
REPO_NAME="chatterbox-whisper"

echo "🐳 Docker Hub Setup (2025 Edition)"
echo "=================================="
echo ""
echo "⚠️  Docker Hub removed direct GitHub integration."
echo "✅ But GitHub Actions is better anyway!"
echo ""

# Check username
if [[ -z "$DOCKER_HUB_USERNAME" ]]; then
    read -p "📝 Enter your Docker Hub username: " DOCKER_HUB_USERNAME
    if [[ -z "$DOCKER_HUB_USERNAME" ]]; then
        echo "❌ Username is required"
        exit 1
    fi
fi

echo "🔧 Current Setup Process:"
echo "========================"
echo ""
echo "1️⃣  Create Docker Hub Repository (Manual)"
echo "   🌐 Go to: https://hub.docker.com/"
echo "   ➕ Click 'Create Repository'"
echo "   📝 Name: $REPO_NAME"
echo "   🔓 Visibility: Public"
echo "   ✅ Click 'Create'"
echo ""

echo "2️⃣  Get Access Token"
echo "   🔑 Go to: https://hub.docker.com/settings/security"
echo "   ➕ Click 'New Access Token'"
echo "   📝 Description: 'GitHub Actions for $REPO_NAME'"
echo "   🔐 Permissions: Read, Write, Delete"
echo "   💾 Copy the token!"
echo ""

echo "3️⃣  Add GitHub Secrets"
echo "   🌐 Go to: https://github.com/thequiet/chatterbox-whisper/settings/secrets/actions"
echo "   ➕ Add DOCKER_HUB_USERNAME: $DOCKER_HUB_USERNAME"
echo "   ➕ Add DOCKER_HUB_ACCESS_TOKEN: (paste the token)"
echo ""

echo "4️⃣  Trigger Build"
echo "   🚀 Run: ./cloud-deploy.sh (option 1)"
echo ""

echo "🎯 Quick Links:"
echo "==============="
echo "🐳 Docker Hub: https://hub.docker.com/r/$DOCKER_HUB_USERNAME/$REPO_NAME"
echo "🔑 Access Tokens: https://hub.docker.com/settings/security"
echo "⚙️  GitHub Secrets: https://github.com/thequiet/chatterbox-whisper/settings/secrets/actions"
echo "🚀 GitHub Actions: https://github.com/thequiet/chatterbox-whisper/actions"
echo ""

# Offer to open URLs
read -p "🌐 Open Docker Hub in browser? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if command -v open >/dev/null 2>&1; then
        open "https://hub.docker.com/"
    elif command -v xdg-open >/dev/null 2>&1; then
        xdg-open "https://hub.docker.com/"
    else
        echo "Please open: https://hub.docker.com/"
    fi
fi

echo ""
echo "✅ After completing the manual steps above, run:"
echo "   ./cloud-deploy.sh"
echo ""
echo "💡 Pro tip: GitHub Actions builds are faster and more reliable"
echo "   than the old Docker Hub automated builds!"
