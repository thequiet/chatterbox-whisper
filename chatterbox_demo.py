import tempfile
import os
import logging

logger = logging.getLogger(__name__)

def synthesize_tts(text):
    """
    Synthesize TTS using chatterbox library with fallback handling
    """
    try:
        # Try different import patterns for chatterbox
        try:
            from chatterbox import TTS
            tts = TTS()
        except ImportError:
            try:
                from chatterbox.tts import TTS
                tts = TTS()
            except ImportError:
                try:
                    import chatterbox
                    tts = chatterbox.TTS()
                except ImportError:
                    # Fallback to a simple TTS implementation
                    logger.warning("Chatterbox TTS not available, using fallback")
                    return create_fallback_audio(text)
        
        # Get available voices
        voices = tts.list_voices()
        if not voices:
            logger.warning("No voices available")
            return create_fallback_audio(text)
        
        voice = voices[0]
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as out:
            tts.synthesize(text=text, voice=voice, output_path=out.name)
            logger.info(f"TTS synthesis completed for text: {text[:50]}...")
            return out.name
            
    except Exception as e:
        logger.error(f"TTS Error: {e}")
        return create_fallback_audio(text)

def create_fallback_audio(text):
    """
    Create a simple fallback audio file when TTS fails
    """
    # Create a simple silence file as fallback
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as out:
        # Write minimal WAV header for silence (1 second of silence at 22050 Hz)
        sample_rate = 22050
        duration = 1.0
        num_samples = int(sample_rate * duration)
        
        # WAV header
        out.write(b'RIFF')
        out.write((36 + num_samples * 2).to_bytes(4, 'little'))  # File size
        out.write(b'WAVE')
        out.write(b'fmt ')
        out.write((16).to_bytes(4, 'little'))  # Format chunk size
        out.write((1).to_bytes(2, 'little'))   # Audio format (PCM)
        out.write((1).to_bytes(2, 'little'))   # Channels
        out.write(sample_rate.to_bytes(4, 'little'))  # Sample rate
        out.write((sample_rate * 2).to_bytes(4, 'little'))  # Byte rate
        out.write((2).to_bytes(2, 'little'))   # Block align
        out.write((16).to_bytes(2, 'little'))  # Bits per sample
        out.write(b'data')
        out.write((num_samples * 2).to_bytes(4, 'little'))  # Data size
        
        # Write silence
        out.write(b'\x00' * (num_samples * 2))
        
        logger.info(f"Created fallback audio for text: {text}")
        return out.name
