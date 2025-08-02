# Chatterbox Whisper - Docker Hub Deployment

A powerful AI application combining Chatterbox TTS (Text-to-Speech) and Faster-Whisper (Speech-to-Text) with both FastAPI and Gradio interfaces.

## 🚀 Quick Start

### Pull and Run from Docker Hub

```bash
# Pull the latest image
docker pull your-username/chatterbox-whisper:latest

# Run with CPU only
docker run --rm -p 7860:7860 -p 7861:7861 your-username/chatterbox-whisper:latest

# Run with GPU support (if available)
docker run --rm --gpus all -p 7860:7860 -p 7861:7861 your-username/chatterbox-whisper:latest
```

### Access the Application

- **FastAPI Documentation**: http://localhost:7860/docs
- **Gradio Interface**: http://localhost:7861
- **Health Check**: http://localhost:7860/health

## 🔧 Building and Publishing

### ⚡ Cloud Build (Recommended - Fast!)

**No local building required!** Build in the cloud for speed:

```bash
chmod +x cloud-deploy.sh
./cloud-deploy.sh
```

Choose option 1 to trigger GitHub Actions cloud build.

**Or for quick Docker Hub setup**:
```bash
./dockerhub-quick-setup.sh  # Updated for 2025 - no more GitHub integration
```

**Benefits**: 5-8 min builds vs 20-30 min local, no local resources used, automatic multi-platform builds.

**Note**: Docker Hub removed direct GitHub integration in 2025, but GitHub Actions is actually better!

### Manual Build and Push (Slower)

Only if you prefer local building:

1. **Set your Docker Hub username**:
   ```bash
   export DOCKER_HUB_USERNAME="your-dockerhub-username"
   ```

2. **Build and push**:
   ```bash
   chmod +x docker-build.sh
   ./docker-build.sh
   ```

3. **Or build with custom tag**:
   ```bash
   TAG="v1.0.0" ./docker-build.sh
   ```

### Using GitHub Actions (Automated)

1. **Set up repository secrets** in your GitHub repository:
   - `DOCKER_HUB_USERNAME`: Your Docker Hub username
   - `DOCKER_HUB_ACCESS_TOKEN`: Your Docker Hub access token

2. **Push to main branch** or create a tag:
   ```bash
   git add .
   git commit -m "Release v1.0.0"
   git tag v1.0.0
   git push origin main --tags
   ```

3. **GitHub Actions will automatically**:
   - Build the Docker image
   - Push to Docker Hub
   - Support multi-platform builds (amd64, arm64)

## 📦 Deployment Options

### Option 1: Quick Deploy Script

```bash
chmod +x deploy.sh
./deploy.sh
```

Choose from:
1. Deploy locally (CPU only)
2. Deploy with GPU support
3. Generate docker-compose.yml
4. Pull latest image from Docker Hub
5. Show running containers

### Option 2: Docker Compose

Generate a docker-compose.yml:

```bash
./deploy.sh  # Choose option 3
docker-compose up -d
```

### Option 3: Manual Docker Commands

```bash
# CPU deployment
docker run -d \
  --name chatterbox-whisper \
  -p 7860:7860 \
  -p 7861:7861 \
  your-username/chatterbox-whisper:latest

# GPU deployment
docker run -d \
  --name chatterbox-whisper-gpu \
  --gpus all \
  -p 7860:7860 \
  -p 7861:7861 \
  your-username/chatterbox-whisper:latest
```

## 🔑 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PYTHONUNBUFFERED` | `1` | Python output buffering |
| `PORT` | `7860` | FastAPI port (for cloud deployments) |
| `GRADIO_PORT` | `7861` | Gradio interface port |

## 🐳 Docker Hub Repository

Your image will be available at:
- **Repository**: https://hub.docker.com/r/your-username/chatterbox-whisper
- **Tags**: `latest`, version tags (e.g., `v1.0.0`)

## 📋 Requirements

### System Requirements
- Docker Engine 20.10+
- For GPU support: NVIDIA Docker Runtime

### Hardware Requirements
- **Minimum**: 4GB RAM, 2 CPU cores
- **Recommended**: 8GB RAM, 4 CPU cores
- **GPU**: NVIDIA GPU with CUDA 12.2+ support (optional)

## 🛠️ Development

### Local Development

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd chatterbox-whisper
   ```

2. **Build locally**:
   ```bash
   docker build -t chatterbox-whisper .
   ```

3. **Run for development**:
   ```bash
   docker run --rm -p 7860:7860 -p 7861:7861 -v $(pwd):/app chatterbox-whisper
   ```

### Customization

- **Modify requirements**: Edit `requirements.txt`
- **Change models**: Update `whisper_demo.py` and `chatterbox_demo.py`
- **API changes**: Modify `app.py`
- **Docker optimization**: Edit `Dockerfile`

## 🚨 Troubleshooting

### Common Issues

1. **Chatterbox import errors**: The app includes fallback mechanisms
2. **CUDA not available**: Automatically falls back to CPU
3. **Port conflicts**: Change ports using `-p HOST_PORT:CONTAINER_PORT`
4. **Memory issues**: Increase Docker memory limits

### Logs

```bash
# View container logs
docker logs chatterbox-whisper

# Follow logs in real-time
docker logs -f chatterbox-whisper
```

### Health Check

```bash
# Check application health
curl http://localhost:7860/health
```

## 📄 License

[Add your license information here]

## 🤝 Contributing

[Add contribution guidelines here]
