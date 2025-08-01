from faster_whisper import WhisperModel

model = WhisperModel("base", device="cuda", compute_type="float16")

def transcribe_audio(audio_path):
    segments, _ = model.transcribe(audio_path, beam_size=5)
    return " ".join(segment.text for segment in segments)
