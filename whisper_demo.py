
# Use OpenAI whisper instead of faster-whisper
import whisper
import torch
import logging

logger = logging.getLogger(__name__)

# Check CUDA availability and set device accordingly
device = "cuda" if torch.cuda.is_available() else "cpu"
logger.info(f"Using device: {device}")

try:
    model = whisper.load_model("base", device=device)
    logger.info("OpenAI Whisper model loaded successfully")
except Exception as e:
    logger.error(f"Error loading OpenAI Whisper model: {e}")
    try:
        model = whisper.load_model("tiny", device="cpu")
        logger.info("Fallback to tiny CPU model successful")
    except Exception as e2:
        logger.error(f"Failed to load any Whisper model: {e2}")
        model = None

def transcribe_audio(audio_path):
    """
    Transcribe audio file to text using OpenAI Whisper
    """
    if model is None:
        return "Error: Whisper model failed to load"
    try:
        result = model.transcribe(audio_path)
        logger.info(f"Transcription completed. Language: {result.get('language')}")
        return result["text"]
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return f"Error transcribing audio: {str(e)}"
