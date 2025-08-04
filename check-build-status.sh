#!/bin/bash

# Quick build status checker for Chatterbox Whisper
echo "🚀 Chatterbox Whisper - Build Status Check"
echo "=========================================="
echo ""

# Check if GitHub CLI is available
if command -v gh &> /dev/null; then
    echo "📊 Latest GitHub Actions runs:"
    gh run list --limit 3 --repo thequiet/chatterbox-whisper
    echo ""
    
    echo "🔗 View all runs: https://github.com/thequiet/chatterbox-whisper/actions"
else
    echo "💡 Install GitHub CLI for detailed status: brew install gh"
    echo "🔗 Manual check: https://github.com/thequiet/chatterbox-whisper/actions"
fi

echo ""
echo "📦 Current Docker Hub setup status:"
if [ -n "$DOCKER_HUB_USERNAME" ]; then
    echo "✅ DOCKER_HUB_USERNAME: $DOCKER_HUB_USERNAME"
else
    echo "❌ DOCKER_HUB_USERNAME not set"
fi

echo ""
echo "🛠️ Next steps:"
echo "1. Add GitHub repository secrets:"
echo "   - DOCKER_HUB_USERNAME: your-dockerhub-username"  
echo "   - DOCKER_HUB_ACCESS_TOKEN: your-access-token"
echo ""
echo "2. Monitor build at: https://github.com/thequiet/chatterbox-whisper/actions"
echo ""
echo "3. Once build completes, test with:"
echo "   docker pull your-username/chatterbox-whisper:latest"
echo "   docker run --rm -p 7860:7860 -p 7861:7861 your-username/chatterbox-whisper:latest"
