# Cloud Build Setup - Fast Docker Hub Publishing

This guide helps you set up cloud-based building so you never have to build Docker images locally again!

## 🚀 Quick Setup (Recommended)

### Option 1: GitHub Actions (Free & Fast)

1. **Run the cloud setup script**:
   ```bash
   chmod +x cloud-deploy.sh
   ./cloud-deploy.sh
   ```
   Choose option 3 to set up GitHub repository automatically.

2. **Or manual setup**:
   ```bash
   # Push your code to GitHub
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/chatterbox-whisper.git
   git push -u origin main
   ```

3. **Add Docker Hub secrets** in GitHub:
   - Go to: `https://github.com/YOUR_USERNAME/chatterbox-whisper/settings/secrets/actions`
   - Add `DOCKER_HUB_USERNAME` (your Docker Hub username)
   - Add `DOCKER_HUB_ACCESS_TOKEN` (create at hub.docker.com → Account Settings → Security)

4. **Trigger cloud builds**:
   ```bash
   ./cloud-deploy.sh  # Choose option 1
   ```

### Option 2: Docker Hub Automated Builds

1. **Connect repository to Docker Hub**:
   - Go to https://hub.docker.com/
   - Create Repository → Connected to GitHub
   - Link your GitHub repository

2. **Configure build rules** (see `dockerhub-autobuild.md`)

## ⚡ Usage

### Trigger Cloud Build & Deploy
```bash
# One command does it all
./cloud-deploy.sh

# Options:
# 1 - Trigger GitHub Actions build
# 2 - Deploy latest from Docker Hub  
# 3 - Setup GitHub repo
# 4 - Check build status
```

### Deploy Only (No Building)
```bash
# Just pull and run latest from Docker Hub
docker pull your-username/chatterbox-whisper:latest
docker run --rm -p 7860:7860 -p 7861:7861 your-username/chatterbox-whisper:latest
```

## 🔄 Automated Workflows

### GitHub Actions Triggers
- **Push to main** → Builds `latest` tag
- **Create tag `v1.0.0`** → Builds `v1.0.0` and `latest` tags  
- **Push to develop** → Builds `dev` tag
- **Manual trigger** → Build any branch

### Docker Hub Auto-Builds
- **Push to main** → `latest` tag
- **Git tag `v1.0.0`** → `1.0.0` tag
- **Push to develop** → `dev` tag

## ⚙️ Cloud Build Features

✅ **Multi-platform builds** (AMD64, ARM64)  
✅ **Build caching** (faster subsequent builds)  
✅ **Automatic testing** (health checks)  
✅ **Build notifications**  
✅ **No local Docker needed**  
✅ **Parallel builds**  

## 📊 Monitoring

### Check Build Status
```bash
# GitHub Actions
./cloud-deploy.sh  # Option 4

# Or view in browser
open https://github.com/YOUR_USERNAME/chatterbox-whisper/actions
```

### Build Times
- **GitHub Actions**: ~5-8 minutes
- **Docker Hub**: ~10-15 minutes
- **Local build**: ~20-30 minutes (avoided! 🎉)

## 🚨 Troubleshooting

### Build Fails
1. Check GitHub Actions logs
2. Verify Docker Hub credentials
3. Check Dockerfile syntax

### Can't Pull Image
```bash
# Check if image exists
docker search your-username/chatterbox-whisper

# Login to Docker Hub
docker login
```

### Secrets Not Working
1. Verify secret names exactly match:
   - `DOCKER_HUB_USERNAME`
   - `DOCKER_HUB_ACCESS_TOKEN`
2. Regenerate Docker Hub access token

## 🎯 Best Practices

### Version Tagging
```bash
# Create version tags for releases
git tag v1.0.0
git push origin v1.0.0  # Triggers versioned build
```

### Branch Strategy
- `main` → Production builds (`latest`)
- `develop` → Development builds (`dev`)
- `feature/*` → No auto-build (save resources)

### Resource Optimization
- GitHub Actions: 2000 free minutes/month
- Docker Hub: Unlimited public builds
- Use build caching for speed

## 🔗 Quick Links

After setup, bookmark these:
- **GitHub Actions**: https://github.com/YOUR_USERNAME/chatterbox-whisper/actions
- **Docker Hub Repo**: https://hub.docker.com/r/YOUR_USERNAME/chatterbox-whisper
- **Latest Image**: `docker pull YOUR_USERNAME/chatterbox-whisper:latest`

---

**No more slow local builds! ⚡**
