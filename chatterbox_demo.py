import tempfile
import os
import logging
import random
import numpy as np
import torch

logger = logging.getLogger(__name__)

# Global variables for TTS system
tts_system = None
vc_system = None
available_voices = []
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

def set_seed(seed: int):
    """Set random seeds for reproducibility"""
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    random.seed(seed)
    np.random.seed(seed)

def initialize_tts():
    """Initialize TTS system and get available voices"""
    global tts_system, available_voices
    
    if tts_system is not None:
        return tts_system, available_voices
    
    try:
        # Try ChatterboxTTS first (the production-grade option)
        logger.info("Attempting to initialize ChatterboxTTS...")
        try:
            from chatterbox.tts import ChatterboxTTS
            import time
            
            # Add retry logic for rate limiting issues
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    logger.info(f"ChatterboxTTS initialization attempt {attempt + 1}/{max_retries}")
                    tts_system = ChatterboxTTS.from_pretrained(DEVICE)
                    logger.info(f"Successfully initialized ChatterboxTTS on {DEVICE}")
                    available_voices = ['ChatterboxTTS Default', 'ChatterboxTTS (with reference)']
                    return tts_system, available_voices
                except Exception as e:
                    if "429" in str(e) or "rate limit" in str(e).lower():
                        wait_time = (attempt + 1) * 10  # Wait 10, 20, 30 seconds
                        logger.warning(f"Rate limited by HuggingFace (attempt {attempt + 1}), waiting {wait_time}s: {e}")
                        if attempt < max_retries - 1:
                            time.sleep(wait_time)
                            continue
                    raise e
                    
        except (ImportError, Exception) as e:
            logger.warning(f"ChatterboxTTS failed: {e}")
            
        # Try Coqui TTS as backup
        try:
            from TTS.api import TTS as CoquiTTS
            tts_system = CoquiTTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")
            logger.info("Successfully initialized Coqui TTS")
            available_voices = ['LJSpeech', 'Default']
            return tts_system, available_voices
        except Exception as e:
            logger.warning(f"Coqui TTS failed: {e}")
        
        # Try gTTS (Google TTS) as backup
        try:
            from gtts import gTTS
            tts_system = gTTS
            logger.info("Fallback: Using gTTS for TTS")
            available_voices = ['Google TTS (English)', 'Google TTS (Spanish)', 'Google TTS (French)']
            return tts_system, available_voices
        except Exception as e:
            logger.warning(f"gTTS failed: {e}")
            
        # Try pyttsx3 as last resort
        try:
            import pyttsx3
            tts_system = pyttsx3.init()
            logger.info("Fallback: Using pyttsx3 for TTS")
            available_voices = []
            return tts_system, available_voices
        except ImportError:
            logger.warning("No TTS libraries available")
            return None, []
            
    except Exception as e:
        logger.error(f"Failed to initialize TTS: {e}")
        return None, []

def initialize_vc():
    """Initialize Voice Conversion system"""
    global vc_system
    
    if vc_system is not None:
        return vc_system
    
    try:
        logger.info("Attempting to initialize ChatterboxVC...")
        from chatterbox.vc import ChatterboxVC
        vc_system = ChatterboxVC.from_pretrained(DEVICE)
        logger.info(f"Successfully initialized ChatterboxVC on {DEVICE}")
        return vc_system
    except (ImportError, Exception) as e:
        logger.warning(f"ChatterboxVC failed: {e}")
        return None

def get_voice_options():
    """Get available voice options for UI"""
    tts, voices = initialize_tts()
    if not voices:
        return ["Default (Fallback)"]
    return voices + ["Default (Fallback)"]

def synthesize_tts(text, voice_selection="Default", audio_prompt_path=None, **kwargs):
    """
    Synthesize text to speech using the initialized TTS system
    """
    if not text or not text.strip():
        return create_fallback_audio("Please provide text to synthesize.")
    
    tts, _ = initialize_tts()
    if tts is None:
        logger.warning("TTS not available")
        return create_fallback_audio(text)
    
    try:
        # Check if this is ChatterboxTTS
        if hasattr(tts, 'generate') and hasattr(tts, 'sr'):
            logger.info("Using ChatterboxTTS for synthesis")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as out:
                # Set default parameters for ChatterboxTTS
                exaggeration = kwargs.get('exaggeration', 0.5)
                temperature = kwargs.get('temperature', 0.8)
                cfg_weight = kwargs.get('cfg_weight', 0.5)
                min_p = kwargs.get('min_p', 0.05)
                top_p = kwargs.get('top_p', 1.0)
                repetition_penalty = kwargs.get('repetition_penalty', 1.2)
                seed_num = kwargs.get('seed_num', 0)
                
                if seed_num != 0:
                    set_seed(int(seed_num))
                
                # Generate audio using ChatterboxTTS
                wav = tts.generate(
                    text,
                    audio_prompt_path=audio_prompt_path,
                    exaggeration=exaggeration,
                    temperature=temperature,
                    cfg_weight=cfg_weight,
                    min_p=min_p,
                    top_p=top_p,
                    repetition_penalty=repetition_penalty,
                )
                
                # Save audio as numpy array
                import soundfile as sf
                sf.write(out.name, wav.squeeze(0).numpy(), tts.sr)
                logger.info(f"ChatterboxTTS synthesis completed for text: {text[:50]}...")
                return out.name
                
        # Handle other TTS systems (fallback)
        elif hasattr(tts, 'tts_to_file'):
            # Coqui TTS style
            logger.info("Using Coqui TTS for synthesis")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as out:
                tts.tts_to_file(text=text, file_path=out.name)
                return out.name
                
        elif tts.__name__ == 'gTTS' if hasattr(tts, '__name__') else str(tts.__class__).find('gTTS') != -1:
            # gTTS style
            logger.info("Using gTTS for synthesis")
            lang = 'en'
            if 'spanish' in voice_selection.lower():
                lang = 'es'
            elif 'french' in voice_selection.lower():
                lang = 'fr'
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as out:
                tts_obj = tts(text=text, lang=lang)
                tts_obj.save(out.name)
                return out.name
                
        elif hasattr(tts, 'say') and hasattr(tts, 'save_to_file'):
            # pyttsx3 style
            logger.info("Using pyttsx3 for synthesis")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as out:
                tts.save_to_file(text, out.name)
                tts.runAndWait()
                return out.name
        else:
            logger.warning("Unknown TTS system, using fallback")
            return create_fallback_audio(text)
            
    except Exception as e:
        logger.error(f"TTS Error: {e}")
        return create_fallback_audio(text)

def clone_voice_from_audio(text, reference_audio_path, voice_name="Custom Voice"):
    """
    Clone voice from reference audio and synthesize text using ChatterboxTTS
    """
    if not text or not text.strip():
        return create_fallback_audio("Please provide text to synthesize.")
    
    if not reference_audio_path or not os.path.exists(reference_audio_path):
        logger.warning("No reference audio provided for voice cloning")
        return synthesize_tts(text)  # Fallback to normal TTS
    
    tts, _ = initialize_tts()
    if tts is None:
        logger.warning("TTS not available for voice cloning")
        return create_fallback_audio(text)
    
    try:
        # Check if this is ChatterboxTTS (supports voice cloning via reference)
        if hasattr(tts, 'generate') and hasattr(tts, 'sr'):
            logger.info(f"Attempting voice cloning with ChatterboxTTS from: {reference_audio_path}")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as out:
                # Use ChatterboxTTS with audio prompt for voice cloning
                wav = tts.generate(
                    text,
                    audio_prompt_path=reference_audio_path,
                    exaggeration=0.5,
                    temperature=0.8,
                    cfg_weight=0.5,
                    min_p=0.05,
                    top_p=1.0,
                    repetition_penalty=1.2,
                )
                
                # Save audio as numpy array
                import soundfile as sf
                sf.write(out.name, wav.squeeze(0).numpy(), tts.sr)
                logger.info(f"Voice cloning completed using ChatterboxTTS for: {voice_name}")
                return out.name
                
        # Try Coqui TTS voice cloning if available
        elif hasattr(tts, 'tts_to_file'):
            logger.info(f"Attempting voice cloning with Coqui TTS from: {reference_audio_path}")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as out:
                try:
                    tts.tts_to_file(text=text, file_path=out.name, speaker_wav=reference_audio_path)
                    logger.info(f"Voice cloning completed using Coqui TTS for: {voice_name}")
                    return out.name
                except Exception as e:
                    logger.warning(f"Coqui TTS voice cloning failed: {e}, falling back to normal synthesis")
                    return synthesize_tts(text)
        else:
            logger.warning("Voice cloning not supported by current TTS system")
            return synthesize_tts(text)  # Fallback to normal synthesis
            
    except Exception as e:
        logger.error(f"Voice cloning error: {e}")
        return synthesize_tts(text)  # Fallback to normal synthesis

def convert_voice(audio_path, target_voice_path=None):
    """
    Convert voice using ChatterboxVC
    """
    if not audio_path or not os.path.exists(audio_path):
        logger.warning("No input audio provided for voice conversion")
        return None
    
    vc = initialize_vc()
    if vc is None:
        logger.warning("Voice conversion not available")
        return None
    
    try:
        logger.info(f"Converting voice from: {audio_path}")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as out:
            wav = vc.generate(audio_path, target_voice_path=target_voice_path)
            
            # Save audio as numpy array
            import soundfile as sf
            sf.write(out.name, wav.squeeze(0).numpy(), vc.sr)
            logger.info("Voice conversion completed")
            return out.name
            
    except Exception as e:
        logger.error(f"Voice conversion error: {e}")
        return None

def create_fallback_audio(text):
    """
    Create a simple fallback audio file when TTS fails
    """
    try:
        # Try to use gTTS as a last resort if available
        try:
            from gtts import gTTS
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as out:
                tts_obj = gTTS(text=text, lang='en')
                tts_obj.save(out.name)
                logger.info(f"Created gTTS fallback audio for text: {text[:50]}...")
                return out.name
        except Exception as e:
            logger.warning(f"gTTS fallback failed: {e}")
            
        # Create a simple beep or silence as ultimate fallback
        import numpy as np
        import soundfile as sf
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as out:
            # Create 2 seconds of silence
            silence = np.zeros(int(2 * 22050))  # 2 seconds at 22050 Hz
            sf.write(out.name, silence, 22050)
            logger.info("Created silence fallback audio")
            return out.name
            
    except Exception as e:
        logger.error(f"Fallback audio creation failed: {e}")
        return None
