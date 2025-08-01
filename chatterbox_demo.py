from chatterbox import TTS
import tempfile

tts = TTS()
voice = tts.list_voices()[0]

def synthesize_tts(text):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as out:
        tts.synthesize(text=text, voice=voice, output_path=out.name)
        return out.name
