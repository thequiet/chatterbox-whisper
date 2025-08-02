# Docker Hub + GitHub Actions - Complete Guide

⚠️ **Important Update**: Docker Hub has removed direct GitHub integration for new repositories. But don't worry - **GitHub Actions is actually better!**

## 🚀 Current Best Practice (2025)

### The Modern Approach: GitHub Actions → Docker Hub

Instead of Docker Hub's old automated builds, we now use GitHub Actions to build and push to Docker Hub. This gives you:

✅ **Faster builds** (5-8 min vs 10-15 min)  
✅ **Multi-platform support** (AMD64 + ARM64)  
✅ **Better caching** and debugging  
✅ **More control** over the build process  
✅ **Free for public repositories**  

## 🔧 Setup Process

### Step 1: Create Docker Hub Repository (Manual)

1. **Go to Docker Hub**: https://hub.docker.com/
2. **Click "Create Repository"**
3. **Repository name**: `chatterbox-whisper`
4. **Visibility**: Public (for free unlimited pulls)
5. **Description**: "AI TTS and STT with FastAPI and Gradio"
6. **Click "Create"**

### Step 2: Setup GitHub Actions (Automated Building)

```bash
./cloud-deploy.sh  # Choose option 1
```

Or manual setup:

1. **Add Docker Hub secrets to GitHub**:
   - Go to: https://github.com/YOUR_USERNAME/chatterbox-whisper/settings/secrets/actions
   - Add `DOCKER_HUB_USERNAME` (your Docker Hub username)
   - Add `DOCKER_HUB_ACCESS_TOKEN` (create at hub.docker.com → Account Settings → Security → New Access Token)

2. **Push code to trigger build**:
   ```bash
   git add .
   git commit -m "Trigger first build"
   git push origin main
   ```

## 🆚 Docker Hub vs GitHub Actions Comparison

| Feature | Docker Hub | GitHub Actions |
|---------|------------|----------------|
| **Build Time** | 10-15 min | 5-8 min |
| **Setup Complexity** | Very Easy | Medium |
| **Cost** | Free (unlimited public) | 2000 min/month free |
| **Multi-platform** | No | Yes (AMD64 + ARM64) |
| **Build Caching** | Limited | Advanced |
| **Custom Workflows** | No | Yes |

## 📋 Step-by-Step Setup

### Step 1: GitHub Repository
```bash
./dockerhub-setup.sh  # Option 1
```

This sets up your GitHub repository and pushes your code.

### Step 2: Docker Hub Configuration

1. **Go to Docker Hub**: https://hub.docker.com/
2. **Create Repository**: Click "Create Repository"
3. **Choose "Connected to GitHub"**
4. **Select your repository**: `your-username/chatterbox-whisper`
5. **Configure Build Rules**:

```
Source Type: Branch
Source: main
Docker Tag: latest
Dockerfile location: Dockerfile
Build context: /
```

```
Source Type: Tag  
Source: /^v([0-9.]+)$/
Docker Tag: {\1}
Dockerfile location: Dockerfile
Build context: /
```

### Step 3: Advanced Settings (Optional)

- **Build timeout**: 7200 seconds (2 hours)
- **Build caching**: Enable
- **Environment variables**:
  - `DOCKER_BUILDKIT=1`
  - `BUILDKIT_INLINE_CACHE=1`

## 🧪 Testing Your Setup

```bash
./dockerhub-setup.sh  # Option 3
```

This creates a test commit to trigger your first build.

## 🏷️ Creating Releases

```bash
./dockerhub-setup.sh  # Option 4
```

Creates version tags that trigger versioned builds:
- `git tag v1.0.0` → Builds `your-username/chatterbox-whisper:1.0.0`

## 📊 Monitoring Builds

### Build Status Dashboard
- **Builds**: https://hub.docker.com/r/your-username/chatterbox-whisper/builds
- **Tags**: https://hub.docker.com/r/your-username/chatterbox-whisper/tags

### Check Status
```bash
./dockerhub-setup.sh  # Option 5
```

## ⚡ Triggering Builds

### Automatic Triggers
```bash
# Trigger latest build
git add .
git commit -m "Update application"
git push origin main

# Trigger versioned build  
git tag v1.2.0
git push origin v1.2.0
```

### Manual Trigger
- Go to Docker Hub → Your Repository → Builds
- Click "Trigger" next to any build rule

## 🎯 Best Practices

### 1. **Optimize Dockerfile for Cloud Builds**
```dockerfile
# Use multi-stage builds to reduce final image size
FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04 as base
# ... build steps ...

# Copy only necessary files
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py whisper_demo.py chatterbox_demo.py ./
```

### 2. **Use .dockerignore**
Already included in your project - reduces build context size.

### 3. **Branch Strategy**
- `main` → `latest` (production)
- `develop` → `dev` (testing)
- `v*` tags → versioned releases

### 4. **Build Notifications**
- Enable email notifications in Docker Hub settings
- Monitor build logs for optimization opportunities

## 🚨 Troubleshooting

### Build Fails
1. **Check build logs** on Docker Hub builds page
2. **Test locally** first: `docker build .`
3. **Verify Dockerfile** syntax

### Build Timeout
- **Increase timeout** to 7200 seconds
- **Optimize Dockerfile** (reduce layers, use smaller base images)
- **Use .dockerignore** to reduce build context

### No Auto-Trigger
1. **Verify webhook** in GitHub repository settings
2. **Check build rules** configuration
3. **Re-link repository** if needed

## 💡 Pro Tips

### Faster Builds
- Use specific package versions in `requirements.txt`
- Layer caching: put stable dependencies first
- Multi-stage builds for smaller final images

### Security
- Use official base images
- Pin specific versions: `ubuntu:22.04` not `ubuntu:latest`
- Scan images for vulnerabilities in Docker Hub

### Resource Management
- Docker Hub gives unlimited public repository builds
- Private repositories have build minute limits
- Consider GitHub Actions for complex workflows

## 🔗 Quick Links

After setup:
- **Repository**: https://hub.docker.com/r/your-username/chatterbox-whisper
- **Builds**: https://hub.docker.com/r/your-username/chatterbox-whisper/builds  
- **Pull Command**: `docker pull your-username/chatterbox-whisper:latest`

---

**✅ Yes, Docker Hub absolutely can build your image! It's free, automatic, and perfect for simple cloud building needs.**
