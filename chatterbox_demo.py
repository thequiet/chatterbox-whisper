import tempfile
import os
import logging

logger = logging.getLogger(__name__)

# Global variables for TTS system
tts_system = None
available_voices = []

def initialize_tts():
    """Initialize TTS system and get available voices"""
    global tts_system, available_voices
    
    if tts_system is not None:
        return tts_system, available_voices
    
    try:
        # Try different import patterns for chatterbox
        logger.info("Attempting to initialize Chatterbox TTS...")
        
        # Method 1: Try direct TTS import
        try:
            from chatterbox import TTS
            tts_system = TTS()
            logger.info("Successfully imported chatterbox.TTS")
        except (ImportError, AttributeError) as e:
            logger.warning(f"Method 1 failed: {e}")
            
            # Method 2: Try tts module import
            try:
                from chatterbox.tts import TTS
                tts_system = TTS()
                logger.info("Successfully imported chatterbox.tts.TTS")
            except (ImportError, AttributeError) as e:
                logger.warning(f"Method 2 failed: {e}")
                
                # Method 3: Try different class names
                try:
                    import chatterbox
                    if hasattr(chatterbox, 'TTS'):
                        tts_system = chatterbox.TTS()
                        logger.info("Successfully initialized chatterbox.TTS()")
                    elif hasattr(chatterbox, 'TextToSpeech'):
                        tts_system = chatterbox.TextToSpeech()
                        logger.info("Successfully initialized chatterbox.TextToSpeech()")
                    elif hasattr(chatterbox, 'Synthesizer'):
                        tts_system = chatterbox.Synthesizer()
                        logger.info("Successfully initialized chatterbox.Synthesizer()")
                    else:
                        # List available attributes for debugging
                        attrs = [attr for attr in dir(chatterbox) if not attr.startswith('_')]
                        logger.error(f"No known TTS class found. Available attributes: {attrs}")
                        return None, []
                except (ImportError, AttributeError) as e:
                    logger.warning(f"Method 3 failed: {e}")
                    
                    # Method 4: Try alternative TTS libraries as fallback
                    try:
                        logger.info("Trying alternative TTS libraries...")
                        # Try pyttsx3 as fallback
                        import pyttsx3
                        tts_system = pyttsx3.init()
                        logger.info("Fallback: Using pyttsx3 for TTS")
                        available_voices = []
                        return tts_system, available_voices
                    except ImportError:
                        logger.warning("No TTS libraries available")
                        return None, []
        
        # Get available voices if TTS system was initialized
        if tts_system:
            try:
                if hasattr(tts_system, 'list_voices'):
                    available_voices = tts_system.list_voices() or []
                elif hasattr(tts_system, 'getProperty') and hasattr(tts_system, 'setProperty'):
                    # pyttsx3 style
                    voices = tts_system.getProperty('voices')
                    available_voices = [{'name': v.name, 'id': v.id} for v in voices] if voices else []
                else:
                    available_voices = []
                    
                logger.info(f"Found {len(available_voices)} voices")
                if available_voices:
                    voice_names = []
                    for v in available_voices[:5]:
                        if isinstance(v, dict):
                            voice_names.append(v.get('name', str(v)))
                        else:
                            voice_names.append(str(v))
                    logger.info(f"Sample voices: {voice_names}")
            except Exception as e:
                logger.warning(f"Could not list voices: {e}")
                available_voices = []
                
        return tts_system, available_voices
        
    except Exception as e:
        logger.error(f"Failed to initialize TTS: {e}")
        return None, []

def get_voice_options():
    """Get available voice options for Gradio dropdown"""
    _, voices = initialize_tts()
    
    if not voices:
        return ["Default (Fallback)"]
    
    # Format voice options for dropdown
    voice_options = []
    for i, voice in enumerate(voices):
        if isinstance(voice, dict):
            name = voice.get('name', f'Voice {i+1}')
            lang = voice.get('language', voice.get('lang', ''))
            gender = voice.get('gender', '')
            
            # Create descriptive label
            label = name
            if lang:
                label += f" ({lang})"
            if gender:
                label += f" - {gender}"
                
            voice_options.append(label)
        else:
            voice_options.append(str(voice))
    
    # Add fallback option
    voice_options.append("Default (Fallback)")
    return voice_options

def synthesize_tts(text, voice_selection="Default (Fallback)"):
    """
    Synthesize TTS using chatterbox library with voice selection
    """
    if not text or not text.strip():
        logger.warning("Empty text provided")
        return create_fallback_audio("Please provide some text to synthesize.")
    
    tts, voices = initialize_tts()
    
    if tts is None or not voices:
        logger.warning("TTS not available, using fallback")
        return create_fallback_audio(text)
    
    try:
        # Select voice based on user choice
        selected_voice = None
        
        if voice_selection == "Default (Fallback)" or not voice_selection:
            selected_voice = voices[0] if voices else None
        else:
            # Find matching voice
            for i, voice in enumerate(voices):
                voice_name = voice.get('name', f'Voice {i+1}') if isinstance(voice, dict) else str(voice)
                if voice_selection.startswith(voice_name):
                    selected_voice = voice
                    break
            
            # Fallback to first voice if not found
            if selected_voice is None:
                selected_voice = voices[0]
        
        if selected_voice is None:
            logger.warning("No voice selected, using fallback")
            return create_fallback_audio(text)
        
        logger.info(f"Using voice: {selected_voice}")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as out:
            # Handle different TTS systems
            if hasattr(tts, 'synthesize'):
                # Chatterbox style
                tts.synthesize(text=text, voice=selected_voice, output_path=out.name)
            elif hasattr(tts, 'say') and hasattr(tts, 'save_to_file'):
                # pyttsx3 style
                if isinstance(selected_voice, dict) and 'id' in selected_voice:
                    tts.setProperty('voice', selected_voice['id'])
                tts.save_to_file(text, out.name)
                tts.runAndWait()
            else:
                # Unknown TTS system, try generic approach
                logger.warning("Unknown TTS system, using fallback")
                return create_fallback_audio(text)
            
            logger.info(f"TTS synthesis completed for text: {text[:50]}...")
            return out.name
            
    except Exception as e:
        logger.error(f"TTS Error: {e}")
        return create_fallback_audio(text)

def clone_voice_from_audio(text, reference_audio_path, voice_name="Custom Voice"):
    """
    Clone voice from reference audio and synthesize text
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
        # Check if TTS system supports voice cloning
        if hasattr(tts, 'clone_voice') or hasattr(tts, 'create_voice'):
            logger.info(f"Attempting voice cloning from: {reference_audio_path}")
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as out:
                # Try voice cloning methods
                if hasattr(tts, 'clone_voice'):
                    cloned_voice = tts.clone_voice(reference_audio_path, name=voice_name)
                    tts.synthesize(text=text, voice=cloned_voice, output_path=out.name)
                elif hasattr(tts, 'create_voice'):
                    cloned_voice = tts.create_voice(reference_audio_path, name=voice_name)
                    tts.synthesize(text=text, voice=cloned_voice, output_path=out.name)
                else:
                    # Try generic synthesis with reference
                    tts.synthesize(text=text, reference_audio=reference_audio_path, output_path=out.name)
                
                logger.info(f"Voice cloning completed for: {voice_name}")
                return out.name
                
        else:
            logger.warning("Voice cloning not supported by current TTS system")
            return synthesize_tts(text)  # Fallback to normal synthesis
            
    except Exception as e:
        logger.error(f"Voice cloning error: {e}")
        return synthesize_tts(text)  # Fallback to normal synthesis

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
