FROM nvidia/cuda:12.2.0-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies including cuDNN
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    git \
    ffmpeg \
    wget \
    curl \
    libgl1 \
    libglib2.0-0 \
    libsndfile1 \
    libportaudio2 \
    libasound2-dev \
    build-essential \
    libcudnn8 \
    libcudnn8-dev \
    espeak-ng \
    espeak-ng-data && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python packages with better error handling
RUN pip3 install --upgrade pip setuptools wheel && \
    pip3 install --no-cache-dir --no-input -r requirements.txt

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
