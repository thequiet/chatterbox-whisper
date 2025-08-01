FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    python3-pip git ffmpeg wget curl libgl1 libglib2.0-0 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --upgrade pip && pip3 install --no-cache-dir --no-input -r requirements.txt

COPY app.py .
COPY whisper_demo.py .
COPY chatterbox_demo.py .

EXPOSE 7860 7861

CMD ["python3", "app.py"]
