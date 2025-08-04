from faster_whisper import WhisperModel
import torch
import logging

logger = logging.getLogger(__name__)

# Check CUDA availability and set device accordingly
device = "cuda" if torch.cuda.is_available() else "cpu"
compute_type = "float16" if device == "cuda" else "int8"

logger.info(f"Using device: {device}, compute_type: {compute_type}")

try:
    # Try with CUDA first if available
    if device == "cuda":
        try:
            model = WhisperModel("base", device="cuda", compute_type="float16")
            logger.info("Whisper model loaded successfully with CUDA")
        except Exception as cuda_error:
            logger.warning(f"CUDA initialization failed: {cuda_error}")
            logger.info("Falling back to CPU...")
            model = WhisperModel("base", device="cpu", compute_type="int8")
            logger.info("Whisper model loaded successfully with CPU fallback")
    else:
        model = WhisperModel("base", device="cpu", compute_type="int8")
        logger.info("Whisper model loaded successfully with CPU")
        
except Exception as e:
    logger.error(f"Error loading Whisper model: {e}")
    # Final fallback attempt
    try:
        model = WhisperModel("tiny", device="cpu", compute_type="int8")
        logger.info("Fallback to tiny CPU model successful")
    except Exception as e2:
        logger.error(f"Failed to load any Whisper model: {e2}")
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
