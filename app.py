from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
import uvicorn
import tempfile
import os
from whisper_demo import transcribe_audio
from chatterbox_demo import synthesize_tts
import gradio as gr
import threading

app = FastAPI()

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    result = transcribe_audio(tmp_path)
    os.unlink(tmp_path)
    return JSONResponse({"transcription": result})

@app.post("/synthesize")
async def synthesize(text: str = Form(...)):
    audio_path = synthesize_tts(text)
    return FileResponse(audio_path, media_type="audio/wav", filename="output.wav")

def launch_gradio():
    with gr.Blocks() as demo:
        gr.Markdown("## 🗣️ Chatterbox TTS and Faster-Whisper Demo")

        with gr.Tab("Transcribe Audio (Whisper)"):
            audio_input = gr.Audio(type="filepath")
            transcribe_btn = gr.Button("Transcribe")
            transcription_output = gr.Textbox()
            transcribe_btn.click(transcribe_audio, inputs=audio_input, outputs=transcription_output)

        with gr.Tab("Synthesize Speech (Chatterbox)"):
            text_input = gr.Textbox(label="Enter text")
            synthesize_btn = gr.Button("Synthesize")
            audio_output = gr.Audio()
            synthesize_btn.click(synthesize_tts, inputs=text_input, outputs=audio_output)

    demo.launch(server_name="0.0.0.0", server_port=7861)

threading.Thread(target=launch_gradio).start()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
