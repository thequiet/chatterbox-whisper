# Use runtime image instead of devel to save space
FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install minimal system dependencies in stages to save disk space
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    python3-dev \
    git \
    ffmpeg \
    libsndfile1 \
    libportaudio2 \
    espeak-ng \
    espeak-ng-data \
    curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python packages efficiently to minimize disk usage
RUN pip3 install --upgrade pip setuptools wheel --no-cache-dir && \
    # Install torch first with CPU-only to save space
    pip3 install --no-cache-dir torch torchaudio --index-url https://download.pytorch.org/whl/cpu && \
    # Install remaining packages
    pip3 install --no-cache-dir faster-whisper gradio uvicorn fastapi python-multipart numpy pyttsx3 requests && \
    pip3 cache purge 2>/dev/null || true && \
    # Clean up to save disk space
    rm -rf ~/.cache/pip /tmp/* /var/tmp/* /root/.cache

# Copy application files
COPY app.py .
COPY whisper_demo.py .
COPY chatterbox_demo.py .

# Create temp directory for audio files
RUN mkdir -p /tmp/audio

EXPOSE 7860 7861

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

CMD ["python3", "app.py"]
