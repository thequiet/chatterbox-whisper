#!/usr/bin/env python3
"""
Pre-download script for ChatterboxTTS and Whisper models
This script downloads models during Docker build to avoid runtime downloads
"""

import os
import logging
import sys
import torch

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def download_chatterbox_models():
    """Download ChatterboxTTS models"""
    try:
        logger.info("Downloading ChatterboxTTS models...")
        from chatterbox.tts import ChatterboxTTS
        
        # Determine device
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {device}")
        
        # Add retry logic for rate limiting
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"ChatterboxTTS download attempt {attempt + 1}/{max_retries}")
                model = ChatterboxTTS.from_pretrained(device)
                logger.info("✅ ChatterboxTTS models downloaded successfully")
                
                # Clean up to save memory
                del model
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    
                return True
                
            except Exception as e:
                if "429" in str(e) or "rate limit" in str(e).lower():
                    wait_time = (attempt + 1) * 30  # Wait 30, 60, 90 seconds
                    logger.warning(f"Rate limited (attempt {attempt + 1}), waiting {wait_time}s: {e}")
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(wait_time)
                        continue
                raise e
        
        return False
        
    except Exception as e:
        logger.error(f"❌ Failed to download ChatterboxTTS models: {e}")
        return False

def download_whisper_models():
    """Download Faster-Whisper models"""
    try:
        logger.info("Downloading Faster-Whisper models...")
        from faster_whisper import WhisperModel
        
        # Download commonly used models
        models_to_download = ["base", "small", "medium"]
        
        for model_size in models_to_download:
            try:
                logger.info(f"Downloading Whisper {model_size} model...")
                model = WhisperModel(model_size, device="cpu", compute_type="int8")
                # Test the model briefly
                logger.info(f"✅ Whisper {model_size} model downloaded successfully")
                del model
            except Exception as e:
                logger.warning(f"⚠️ Failed to download Whisper {model_size} model: {e}")
                continue
                
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to download Whisper models: {e}")
        return False

def download_voice_conversion_models():
    """Download ChatterboxVC models if available"""
    try:
        logger.info("Attempting to download ChatterboxVC models...")
        from chatterbox.vc import ChatterboxVC
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = ChatterboxVC.from_pretrained(device)
        logger.info("✅ ChatterboxVC models downloaded successfully")
        
        # Clean up
        del model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            
        return True
        
    except Exception as e:
        logger.warning(f"⚠️ ChatterboxVC not available or failed to download: {e}")
        return False

def main():
    """Main function to download all models"""
    logger.info("🚀 Starting model download process...")
    
    # Set environment variables for optimal downloading
    os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
    os.environ['HF_HUB_CACHE'] = '/app/.cache/huggingface'
    os.environ['TRANSFORMERS_CACHE'] = '/app/.cache/huggingface'
    
    success_count = 0
    total_count = 3
    
    # Download models
    if download_chatterbox_models():
        success_count += 1
        
    if download_whisper_models():
        success_count += 1
        
    if download_voice_conversion_models():
        success_count += 1
    
    logger.info(f"📊 Model download summary: {success_count}/{total_count} successful")
    
    if success_count > 0:
        logger.info("✅ Model download process completed successfully")
        return 0
    else:
        logger.error("❌ All model downloads failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
