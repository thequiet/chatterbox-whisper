from faster_whisper import WhisperModel
import torch
import logging

logger = logging.getLogger(__name__)

# Check CUDA availability and set device accordingly
device = "cuda" if torch.cuda.is_available() else "cpu"
compute_type = "float16" if device == "cuda" else "int8"

logger.info(f"Using device: {device}, compute_type: {compute_type}")

try:
    model = WhisperModel("base", device=device, compute_type=compute_type)
    logger.info("Whisper model loaded successfully")
except Exception as e:
    logger.error(f"Error loading Whisper model with {device}: {e}")
    # Fallback to CPU with different settings
    try:
        model = WhisperModel("base", device="cpu", compute_type="int8")
        logger.info("Fallback to CPU model successful")
    except Exception as e2:
        logger.error(f"Failed to load CPU fallback model: {e2}")
        model = None

def transcribe_audio(audio_path):
    """
    Transcribe audio file to text using Whisper
    """
    if model is None:
        return "Error: Whisper model failed to load"
    
    try:
        segments, info = model.transcribe(audio_path, beam_size=5)
        result = " ".join(segment.text for segment in segments)
        logger.info(f"Transcription completed. Language: {info.language}, confidence: {info.language_probability:.2f}")
        return result
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return f"Error transcribing audio: {str(e)}"
