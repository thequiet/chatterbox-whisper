# Docker Hub Automated Build Configuration
# Place this in your Docker Hub repository settings

# Build Rules Configuration for Docker Hub
# Repository: your-username/chatterbox-whisper

# Source Type: Git
# Source: https://github.com/your-username/chatterbox-whisper

# Build Rules:
# Type        | Source          | Docker Tag    | Dockerfile Location | Build Context
# ------------|-----------------|---------------|-------------------|---------------
# Branch      | main           | latest        | Dockerfile        | /
# Branch      | develop        | dev           | Dockerfile        | /
# Tag         | /^v([0-9.]+)$/ | {\1}          | Dockerfile        | /
# Tag         | /^v([0-9.]+)$/ | {\1}-gpu      | Dockerfile        | /

# Build Environment Variables:
# DOCKER_BUILDKIT=1
# BUILDKIT_INLINE_CACHE=1

# Advanced Settings:
# Build timeout: 7200 seconds (2 hours)
# Build caching: Enabled
