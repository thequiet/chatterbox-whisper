#!/usr/bin/env python3
"""
Simplified model pre-cache script
Just downloads and caches models without testing them extensively
"""

import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set cache directories
os.environ['HF_HUB_CACHE'] = '/app/.cache/huggingface'
os.environ['TRANSFORMERS_CACHE'] = '/app/.cache/huggingface'
os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'

def cache_chatterbox():
    """Pre-cache ChatterboxTTS models"""
    try:
        logger.info("Pre-caching ChatterboxTTS...")
        
        # Import and trigger model download
        from chatterbox.tts import ChatterboxTTS
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # This will download and cache the model files
        ChatterboxTTS.from_pretrained(device)
        logger.info("✅ ChatterboxTTS cached")
        return True
        
    except Exception as e:
        logger.warning(f"⚠️ ChatterboxTTS caching failed: {e}")
        return False

def cache_whisper():
    """Pre-cache Whisper models"""
    try:
        logger.info("Pre-caching Whisper models...")
        from faster_whisper import WhisperModel
        
        # Cache small model for efficiency
        WhisperModel("small", device="cpu")
        logger.info("✅ Whisper models cached")
        return True
        
    except Exception as e:
        logger.warning(f"⚠️ Whisper caching failed: {e}")
        return False

if __name__ == "__main__":
    logger.info("🔄 Starting model caching...")
    
    success = False
    if cache_chatterbox():
        success = True
    if cache_whisper():
        success = True
        
    if success:
        logger.info("✅ Model caching completed")
    else:
        logger.warning("⚠️ Model caching had issues - will download at runtime")
