from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import uvicorn
import tempfile
import os
import logging
from whisper_demo import transcribe_audio
from chatterbox_demo import synthesize_tts

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Chatterbox Whisper API", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "Chatterbox Whisper API is running on Cloud Run", "status": "healthy"}

@app.get("/health")
async def health():
    return {"status": "healthy", "services": ["transcription", "tts"], "platform": "cloud-run"}

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    """Transcribe audio file to text"""
    tmp_path = None
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="File must be an audio file")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        logger.info(f"Transcribing file: {file.filename}")
        result = transcribe_audio(tmp_path)
        os.unlink(tmp_path)
        
        return JSONResponse({"transcription": result, "filename": file.filename})
    
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@app.post("/synthesize")
async def synthesize(text: str = Form(...)):
    """Synthesize text to speech"""
    try:
        if not text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        logger.info(f"Synthesizing text: {text[:50]}...")
        audio_path = synthesize_tts(text)
        
        if not os.path.exists(audio_path):
            raise HTTPException(status_code=500, detail="Audio synthesis failed")
        
        return FileResponse(
            audio_path, 
            media_type="audio/wav", 
            filename="output.wav",
            headers={"Content-Disposition": "attachment; filename=output.wav"}
        )
    
    except Exception as e:
        logger.error(f"Synthesis error: {e}")
        raise HTTPException(status_code=500, detail=f"Synthesis failed: {str(e)}")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Starting FastAPI server on port {port} (Cloud Run mode)")
    uvicorn.run(app, host="0.0.0.0", port=port)
