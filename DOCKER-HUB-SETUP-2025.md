# Docker Hub Repository Creation Guide (2025 Update)

⚠️ **Important Update**: Docker Hub has removed the direct "Connected to GitHub" option for new repositories. Here's the current best practice:

## 🆕 Modern Approach: Manual Repository + GitHub Actions

This is actually **better** than the old Docker Hub automated builds!

### Step 1: Create Docker Hub Repository Manually

1. **Go to Docker Hub**: <https://hub.docker.com/>
2. **Sign in** to your account
3. **Click "Create Repository"**
4. **Fill out the form**:
   - **Repository name**: `chatterbox-whisper`
   - **Visibility**: Public (for unlimited free pulls)
   - **Description**: "AI-powered TTS and STT with FastAPI and Gradio interfaces"
5. **Click "Create"**

### Step 2: Get Docker Hub Access Token

1. **Go to Account Settings**: <https://hub.docker.com/settings/security>
2. **Click "New Access Token"**
3. **Access token description**: "GitHub Actions for chatterbox-whisper"
4. **Access permissions**: Read, Write, Delete
5. **Generate and copy** the token (save it securely!)

### Step 3: Setup GitHub Actions (Automated Building)

We'll use the scripts I've already created for you:

```bash
./cloud-deploy.sh  # Choose option 1
```

Or manually add secrets to GitHub:

1. **Go to your GitHub repository**: <https://github.com/thequiet/chatterbox-whisper>
2. **Navigate to**: Settings → Secrets and variables → Actions
3. **Add repository secrets**:
   - `DOCKER_HUB_USERNAME`: Your Docker Hub username
   - `DOCKER_HUB_ACCESS_TOKEN`: The token you just created

### Step 4: Trigger First Build

```bash
# Make a small change to trigger the build
echo "# Build triggered $(date)" >> build-trigger.md
git add build-trigger.md
git commit -m "Trigger first Docker Hub build"
git push origin main
```

## ✅ Benefits of This Approach

| Feature | Old Docker Hub Builds | New GitHub Actions |
|---------|----------------------|-------------------|
| **Speed** | 10-15 minutes | 5-8 minutes |
| **Multi-platform** | No | Yes (AMD64 + ARM64) |
| **Build caching** | Limited | Advanced |
| **Debugging** | Poor | Excellent |
| **Control** | Limited | Full control |
| **Cost** | Free | Free (2000 min/month) |

## 🔍 Monitoring Your Builds

### GitHub Actions Dashboard
- **Build logs**: <https://github.com/thequiet/chatterbox-whisper/actions>
- **Workflow files**: `.github/workflows/`

### Docker Hub Repository
- **Your repository**: `https://hub.docker.com/r/YOUR_USERNAME/chatterbox-whisper`
- **Images will appear here** after successful builds

## 🚀 Using Your Built Images

Once the build completes (5-8 minutes), you can:

```bash
# Pull your image
docker pull YOUR_USERNAME/chatterbox-whisper:latest

# Run it
docker run --rm -p 7860:7860 -p 7861:7861 YOUR_USERNAME/chatterbox-whisper:latest
```

## 📋 Quick Reference Commands

```bash
# Setup repository and triggers
./dockerhub-setup.sh

# Deploy and manage
./cloud-deploy.sh

# Check status
./cloud-deploy.sh  # Option 4
```

## 🎯 Why This is Better

1. **Faster builds** - GitHub's infrastructure is optimized
2. **Better debugging** - Full access to build logs
3. **Multi-platform** - Automatic ARM64 + AMD64 builds
4. **More reliable** - GitHub Actions has better uptime
5. **Version control** - Your build configuration is in git

---

**The "Connected to GitHub" option removal is actually a blessing in disguise - GitHub Actions gives you much more power and speed!** 🚀
