# Universal Dockerfile for ChatterboxTTS (supports regular deployment and RunPod)
FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04

# Set environment variables for non-interactive installs
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PYTHONDONTWRITEBYTECODE=1
# HuggingFace settings to help with rate limiting and caching
ENV HF_HUB_DISABLE_TELEMETRY=1
ENV HF_HUB_CACHE=/app/.cache/huggingface
ENV TRANSFORMERS_CACHE=/app/.cache/huggingface
ENV HF_HUB_DOWNLOAD_TIMEOUT=300
ENV PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128

# Install system dependencies, add PPA for Python 3.11, and install Python 3.11
RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y --no-install-recommends \
    python3.11 \
    python3.11-dev \
    python3.11-venv \
    python3-pip \
    git \
    build-essential \
    libsndfile1 \
    ffmpeg \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/bin/python3.11 /usr/bin/python3 \
    && ln -sf /usr/bin/python3.11 /usr/bin/python \
    && python -m pip install --upgrade pip setuptools wheel

# Install PyTorch and torchaudio with CUDA 12.1 support
RUN pip install torch==2.5.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu121

# Install ChatterboxTTS and core dependencies
RUN pip install chatterbox-tts gradio faster-whisper whisper uvicorn fastapi python-multipart runpod

# Create cache directories for HuggingFace models
RUN mkdir -p /app/.cache/huggingface

# Create app directory and copy the application files
WORKDIR /app
COPY app.py .
COPY whisper_demo.py .
COPY chatterbox_demo.py .
COPY gradio_tts_app.py .
COPY voice_conversion_app.py .
COPY download_models.py .
COPY cache_models.py .

# Copy RunPod handler (if exists) for serverless compatibility
COPY src/handler.py /handler.py

# Create temp directory for audio files
RUN mkdir -p /tmp/audio

# Pre-download and cache models to avoid runtime downloads and rate limiting
# This will significantly speed up container startup and avoid HuggingFace 429 errors
RUN echo "🔄 Pre-caching models..." && \
    python cache_models.py || echo "⚠️ Model pre-caching failed, will download at runtime"

# Expose both FastAPI and Gradio ports
EXPOSE 7860 7861

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

# Default command runs the main application, but can be overridden for RunPod
CMD ["python", "app.py"]
