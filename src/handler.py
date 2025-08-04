import runpod
import os
import tempfile
import logging
import torch
import numpy as np
import soundfile as sf
from io import BytesIO
import base64
import requests
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for models
tts_model = None
vc_model = None
whisper_model = None
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

def initialize_models():
    """Initialize all models once when the worker starts"""
    global tts_model, vc_model, whisper_model
    
    try:
        # Initialize ChatterboxTTS
        logger.info("Loading ChatterboxTTS...")
        from chatterbox.tts import ChatterboxTTS
        tts_model = ChatterboxTTS.from_pretrained(DEVICE)
        logger.info("✅ ChatterboxTTS loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load ChatterboxTTS: {e}")
        tts_model = None
    
    try:
        # Initialize ChatterboxVC
        logger.info("Loading ChatterboxVC...")
        from chatterbox.vc import ChatterboxVC
        vc_model = ChatterboxVC.from_pretrained(DEVICE)
        logger.info("✅ ChatterboxVC loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load ChatterboxVC: {e}")
        vc_model = None
    
    try:
        # Initialize Faster-Whisper
        logger.info("Loading Faster-Whisper...")
        from faster_whisper import WhisperModel
        whisper_model = WhisperModel("base", device=DEVICE, compute_type="float16" if DEVICE == "cuda" else "int8")
        logger.info("✅ Faster-Whisper loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load Faster-Whisper: {e}")
        whisper_model = None

def download_audio_from_url(url: str) -> str:
    """Download audio file from URL and save temporarily"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(response.content)
            return tmp_file.name
    except Exception as e:
        logger.error(f"Failed to download audio from {url}: {e}")
        raise

def decode_base64_audio(base64_data: str) -> str:
    """Decode base64 audio data and save temporarily"""
    try:
        audio_data = base64.b64decode(base64_data)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(audio_data)
            return tmp_file.name
    except Exception as e:
        logger.error(f"Failed to decode base64 audio: {e}")
        raise

def encode_audio_to_base64(audio_path: str) -> str:
    """Encode audio file to base64"""
    try:
        with open(audio_path, "rb") as audio_file:
            audio_data = audio_file.read()
            return base64.b64encode(audio_data).decode('utf-8')
    except Exception as e:
        logger.error(f"Failed to encode audio to base64: {e}")
        raise

def text_to_speech(job_input: Dict[str, Any]) -> Dict[str, Any]:
    """Generate speech from text using ChatterboxTTS"""
    if tts_model is None:
        return {"error": "ChatterboxTTS model not available"}
    
    try:
        text = job_input.get("text", "")
        if not text:
            return {"error": "No text provided"}
        
        # Get parameters with defaults
        temperature = job_input.get("temperature", 0.8)
        exaggeration = job_input.get("exaggeration", 0.5)
        cfg_weight = job_input.get("cfg_weight", 0.5)
        min_p = job_input.get("min_p", 0.05)
        top_p = job_input.get("top_p", 1.0)
        repetition_penalty = job_input.get("repetition_penalty", 1.2)
        seed = job_input.get("seed", 0)
        
        # Handle reference audio for voice cloning
        audio_prompt_path = None
        if "reference_audio_url" in job_input:
            audio_prompt_path = download_audio_from_url(job_input["reference_audio_url"])
        elif "reference_audio_base64" in job_input:
            audio_prompt_path = decode_base64_audio(job_input["reference_audio_base64"])
        
        # Set seed for reproducibility
        if seed != 0:
            torch.manual_seed(seed)
            if torch.cuda.is_available():
                torch.cuda.manual_seed(seed)
                torch.cuda.manual_seed_all(seed)
            np.random.seed(seed)
        
        # Generate speech
        wav = tts_model.generate(
            text,
            audio_prompt_path=audio_prompt_path,
            exaggeration=exaggeration,
            temperature=temperature,
            cfg_weight=cfg_weight,
            min_p=min_p,
            top_p=top_p,
            repetition_penalty=repetition_penalty,
        )
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            sf.write(tmp_file.name, wav.squeeze(0).numpy(), tts_model.sr)
            
            # Encode to base64
            audio_base64 = encode_audio_to_base64(tmp_file.name)
            
            # Clean up
            os.unlink(tmp_file.name)
            if audio_prompt_path:
                os.unlink(audio_prompt_path)
        
        return {
            "audio_base64": audio_base64,
            "sample_rate": tts_model.sr,
            "text": text,
            "parameters": {
                "temperature": temperature,
                "exaggeration": exaggeration,
                "cfg_weight": cfg_weight,
                "min_p": min_p,
                "top_p": top_p,
                "repetition_penalty": repetition_penalty,
                "seed": seed
            }
        }
        
    except Exception as e:
        logger.error(f"TTS generation failed: {e}")
        return {"error": f"TTS generation failed: {str(e)}"}

def voice_conversion(job_input: Dict[str, Any]) -> Dict[str, Any]:
    """Convert voice using ChatterboxVC"""
    if vc_model is None:
        return {"error": "ChatterboxVC model not available"}
    
    try:
        # Get input audio
        input_audio_path = None
        if "input_audio_url" in job_input:
            input_audio_path = download_audio_from_url(job_input["input_audio_url"])
        elif "input_audio_base64" in job_input:
            input_audio_path = decode_base64_audio(job_input["input_audio_base64"])
        else:
            return {"error": "No input audio provided"}
        
        # Get target voice (optional)
        target_voice_path = None
        if "target_voice_url" in job_input:
            target_voice_path = download_audio_from_url(job_input["target_voice_url"])
        elif "target_voice_base64" in job_input:
            target_voice_path = decode_base64_audio(job_input["target_voice_base64"])
        
        # Convert voice
        wav = vc_model.generate(input_audio_path, target_voice_path=target_voice_path)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            sf.write(tmp_file.name, wav.squeeze(0).numpy(), vc_model.sr)
            
            # Encode to base64
            audio_base64 = encode_audio_to_base64(tmp_file.name)
            
            # Clean up
            os.unlink(tmp_file.name)
            os.unlink(input_audio_path)
            if target_voice_path:
                os.unlink(target_voice_path)
        
        return {
            "audio_base64": audio_base64,
            "sample_rate": vc_model.sr
        }
        
    except Exception as e:
        logger.error(f"Voice conversion failed: {e}")
        return {"error": f"Voice conversion failed: {str(e)}"}

def speech_to_text(job_input: Dict[str, Any]) -> Dict[str, Any]:
    """Transcribe speech to text using Faster-Whisper"""
    if whisper_model is None:
        return {"error": "Whisper model not available"}
    
    try:
        # Get input audio
        audio_path = None
        if "audio_url" in job_input:
            audio_path = download_audio_from_url(job_input["audio_url"])
        elif "audio_base64" in job_input:
            audio_path = decode_base64_audio(job_input["audio_base64"])
        else:
            return {"error": "No audio provided"}
        
        # Transcribe
        segments, info = whisper_model.transcribe(audio_path)
        
        # Collect results
        transcription = ""
        segments_list = []
        
        for segment in segments:
            transcription += segment.text + " "
            segments_list.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text
            })
        
        # Clean up
        os.unlink(audio_path)
        
        return {
            "transcription": transcription.strip(),
            "segments": segments_list,
            "language": info.language,
            "language_probability": info.language_probability
        }
        
    except Exception as e:
        logger.error(f"Speech transcription failed: {e}")
        return {"error": f"Speech transcription failed: {str(e)}"}

def handler(job):
    """Main RunPod handler function"""
    job_input = job.get("input", {})
    task_type = job_input.get("task", "tts")
    
    logger.info(f"Processing {task_type} task")
    
    try:
        if task_type == "tts" or task_type == "text_to_speech":
            return text_to_speech(job_input)
        elif task_type == "vc" or task_type == "voice_conversion":
            return voice_conversion(job_input)
        elif task_type == "stt" or task_type == "speech_to_text":
            return speech_to_text(job_input)
        else:
            return {"error": f"Unknown task type: {task_type}"}
    
    except Exception as e:
        logger.error(f"Handler error: {e}")
        return {"error": f"Processing failed: {str(e)}"}

if __name__ == "__main__":
    logger.info("Starting ChatterboxTTS RunPod worker...")
    logger.info(f"Using device: {DEVICE}")
    
    # Initialize models
    initialize_models()
    
    # Start the worker
    logger.info("Worker ready, starting RunPod serverless...")
    runpod.serverless.start({"handler": handler})
