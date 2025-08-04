from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import uvicorn
import tempfile
import os
import logging
from whisper_demo import transcribe_audio
from chatterbox_demo import synthesize_tts, get_voice_options, clone_voice_from_audio
import gradio as gr
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Chatterbox Whisper API", version="1.0.0")

# Error handling wrapper functions for Gradio
def safe_transcribe_audio(audio_path):
    """Safe wrapper for transcription to prevent Gradio crashes"""
    try:
        if not audio_path:
            return "Error: No audio file provided"
        
        if not os.path.exists(audio_path):
            return "Error: Audio file not found"
        
        result = transcribe_audio(audio_path)
        return result if result else "Error: Transcription failed"
    except Exception as e:
        logger.error(f"Gradio transcription error: {e}")
        return f"Error: {str(e)}"

def safe_synthesize_tts(text, voice_selection="Default (Fallback)"):
    """Safe wrapper for TTS synthesis to prevent Gradio crashes"""
    try:
        if not text or not text.strip():
            return None, "Error: Please provide text to synthesize"
        
        audio_path = synthesize_tts(text, voice_selection)
        
        if audio_path and os.path.exists(audio_path):
            return audio_path, "✅ Speech generated successfully!"
        else:
            return None, "❌ Speech synthesis failed"
    except Exception as e:
        logger.error(f"Gradio TTS error: {e}")
        return None, f"❌ Error: {str(e)}"

def safe_clone_voice(text, reference_audio, voice_name="Custom Voice"):
    """Safe wrapper for voice cloning to prevent Gradio crashes"""
    try:
        if not text or not text.strip():
            return None, "Error: Please provide text to synthesize"
        
        if not reference_audio:
            return safe_synthesize_tts(text)  # Fallback to normal TTS
        
        audio_path = clone_voice_from_audio(text, reference_audio, voice_name)
        
        if audio_path and os.path.exists(audio_path):
            return audio_path, f"✅ Voice cloning completed for '{voice_name}'"
        else:
            return None, "❌ Voice cloning failed"
    except Exception as e:
        logger.error(f"Gradio voice cloning error: {e}")
        return None, f"❌ Error: {str(e)}"

def safe_refresh_voices():
    """Safe wrapper to refresh voice options"""
    try:
        # Reset TTS system to reload voices
        from chatterbox_demo import initialize_tts
        global tts_system, available_voices
        tts_system = None
        available_voices = []
        
        new_choices = get_voice_options()
        return gr.Dropdown.update(choices=new_choices, value=new_choices[0] if new_choices else "Default (Fallback)")
    except Exception as e:
        logger.error(f"Voice refresh error: {e}")
        return gr.Dropdown.update(choices=["Default (Fallback)"], value="Default (Fallback)")

@app.get("/")
async def root():
    return {"message": "Chatterbox Whisper API is running", "status": "healthy"}

@app.get("/health")
async def health():
    return {"status": "healthy", "services": ["transcription", "tts"]}

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    """Transcribe audio file to text"""
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
        if os.path.exists(tmp_path):
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

def launch_gradio():
    """Launch Gradio interface with enhanced voice options"""
    try:
        # Test imports first
        try:
            from chatterbox_demo import get_voice_options, synthesize_tts, clone_voice_from_audio
            enhanced_mode = True
        except ImportError as e:
            logger.warning(f"Enhanced mode not available: {e}")
            enhanced_mode = False
        
        if not enhanced_mode:
            return launch_simple_gradio()
        
        with gr.Blocks(title="Chatterbox TTS and Faster-Whisper Demo", theme=gr.themes.Soft()) as demo:
            gr.Markdown("## 🗣️ Chatterbox TTS and Faster-Whisper Demo")

            with gr.Tab("🎧 Transcribe Audio (Whisper)"):
                gr.Markdown("### Upload an audio file to transcribe it to text using Faster-Whisper")
                
                with gr.Row():
                    with gr.Column():
                        audio_input = gr.Audio(
                            type="filepath", 
                            label="Upload Audio File",
                            sources=["upload", "microphone"]
                        )
                        transcribe_btn = gr.Button("🔍 Transcribe", variant="primary", size="lg")
                    
                    with gr.Column():
                        transcription_output = gr.Textbox(
                            label="Transcription Result", 
                            lines=8, 
                            placeholder="Transcribed text will appear here...",
                            show_copy_button=True
                        )
                
                # Add examples
                gr.Examples(
                    examples=[],  # You can add example audio files here
                    inputs=audio_input,
                    label="Example Audio Files"
                )
                
                transcribe_btn.click(
                    fn=safe_transcribe_audio, 
                    inputs=audio_input, 
                    outputs=transcription_output,
                    show_progress=True
                )

            with gr.Tab("🗣️ Text-to-Speech (Standard)"):
                gr.Markdown("### Convert text to speech using available voices")
                
                with gr.Row():
                    with gr.Column():
                        text_input = gr.Textbox(
                            label="Enter text to synthesize", 
                            lines=4, 
                            placeholder="Type your text here...",
                            value="Hello! This is a test of the Chatterbox text-to-speech system.",
                            max_lines=10
                        )
                        
                        # Voice selection dropdown
                        voice_dropdown = gr.Dropdown(
                            choices=get_voice_options(),
                            value="Default (Fallback)",
                            label="Select Voice",
                            info="Choose from available voices"
                        )
                        
                        # Refresh voices button
                        refresh_voices_btn = gr.Button("🔄 Refresh Voices", size="sm")
                        
                        synthesize_btn = gr.Button("🎵 Generate Speech", variant="primary", size="lg")
                    
                    with gr.Column():
                        audio_output = gr.Audio(
                            label="Generated Audio",
                            autoplay=False,
                            show_download_button=True
                        )
                        
                        status_output = gr.Textbox(
                            label="Status",
                            lines=2,
                            placeholder="Status will appear here...",
                            interactive=False
                        )
                
                # Add text examples
                gr.Examples(
                    examples=[
                        ["Hello, welcome to the Chatterbox TTS demo!"],
                        ["The quick brown fox jumps over the lazy dog."],
                        ["Artificial intelligence is transforming how we communicate."],
                        ["Good morning! How are you doing today?"]
                    ],
                    inputs=text_input,
                    label="Example Texts"
                )
                
                def refresh_voices():
                    return gr.Dropdown(choices=get_voice_options())
                
                def synthesize_with_status(text, voice):
                    try:
                        if not text or not text.strip():
                            return None, "❌ Please enter some text to synthesize."
                        
                        # Limit text length to prevent crashes
                        if len(text) > 5000:
                            text = text[:5000] + "..."
                            status_msg = "⚠️ Text truncated to 5000 characters.\n"
                        else:
                            status_msg = ""
                        
                        audio_file = synthesize_tts(text, voice)
                        if audio_file and os.path.exists(audio_file):
                            return audio_file, status_msg + f"✅ Successfully generated speech using {voice}"
                        else:
                            return None, status_msg + "❌ Failed to generate speech. Using fallback."
                    except Exception as e:
                        logger.error(f"TTS synthesis error: {e}")
                        return None, f"❌ Error: {str(e)}"
                
                refresh_voices_btn.click(
                    fn=refresh_voices,
                    outputs=voice_dropdown
                )
                
                synthesize_btn.click(
                    fn=synthesize_with_status,
                    inputs=[text_input, voice_dropdown],
                    outputs=[audio_output, status_output],
                    show_progress=True
                )

            with gr.Tab("🎭 Voice Cloning"):
                gr.Markdown("### Clone a voice from reference audio")
                gr.Markdown("*Upload a clear audio sample (5-30 seconds) to clone the speaker's voice*")
                
                with gr.Row():
                    with gr.Column():
                        clone_text_input = gr.Textbox(
                            label="Text to synthesize with cloned voice",
                            lines=3,
                            placeholder="Enter the text you want the cloned voice to say...",
                            value="Hello, this is a demonstration of voice cloning technology."
                        )
                        
                        reference_audio = gr.Audio(
                            type="filepath",
                            label="Reference Audio (for voice cloning)",
                            sources=["upload", "microphone"],
                            info="Upload clear audio of the target speaker (5-30 seconds recommended)"
                        )
                        
                        clone_voice_name = gr.Textbox(
                            label="Voice Name",
                            placeholder="e.g., John's Voice",
                            value="Custom Cloned Voice"
                        )
                        
                        clone_btn = gr.Button("🎭 Clone Voice & Generate", variant="primary", size="lg")
                    
                    with gr.Column():
                        cloned_audio_output = gr.Audio(
                            label="Cloned Voice Audio",
                            autoplay=False,
                            show_download_button=True
                        )
                        
                        clone_status_output = gr.Textbox(
                            label="Cloning Status",
                            lines=4,
                            placeholder="Cloning status will appear here...",
                            interactive=False
                        )
                
                def clone_with_status(text, reference_path, voice_name):
                    try:
                        if not text or not text.strip():
                            return None, "❌ Please enter text to synthesize."
                        
                        # Limit text length
                        if len(text) > 2000:
                            text = text[:2000] + "..."
                            
                        if not reference_path:
                            return None, "❌ Please upload reference audio for voice cloning."
                        
                        # Validate file exists and has reasonable size
                        if not os.path.exists(reference_path):
                            return None, "❌ Reference audio file not found."
                            
                        file_size = os.path.getsize(reference_path)
                        if file_size > 50 * 1024 * 1024:  # 50MB limit
                            return None, "❌ Reference audio file too large (max 50MB)."
                        
                        status_msg = f"🎭 Attempting to clone voice: {voice_name}\n"
                        status_msg += f"📁 Reference audio: {os.path.basename(reference_path)}\n"
                        status_msg += f"📏 File size: {file_size / 1024 / 1024:.1f} MB\n"
                        
                        audio_file = clone_voice_from_audio(text, reference_path, voice_name)
                        
                        if audio_file and os.path.exists(audio_file):
                            status_msg += "✅ Voice cloning completed successfully!"
                            return audio_file, status_msg
                        else:
                            status_msg += "⚠️ Voice cloning not supported, using standard TTS."
                            return audio_file, status_msg
                            
                    except Exception as e:
                        logger.error(f"Voice cloning error: {e}")
                        return None, f"❌ Voice cloning error: {str(e)}"
                
                clone_btn.click(
                    fn=clone_with_status,
                    inputs=[clone_text_input, reference_audio, clone_voice_name],
                    outputs=[cloned_audio_output, clone_status_output],
                    show_progress=True
                )

            with gr.Tab("⚙️ Settings & Info"):
                gr.Markdown("### System Information")
                
                def get_system_info():
                    from chatterbox_demo import initialize_tts
                    
                    info = "## 🔧 TTS System Status\n\n"
                    
                    try:
                        tts, voices = initialize_tts()
                        if tts:
                            info += f"✅ **Chatterbox TTS**: Available\n"
                            info += f"📢 **Available Voices**: {len(voices)}\n\n"
                            
                            if voices:
                                info += "### Voice Details:\n"
                                for i, voice in enumerate(voices[:10]):  # Show first 10 voices
                                    if isinstance(voice, dict):
                                        name = voice.get('name', f'Voice {i+1}')
                                        lang = voice.get('language', voice.get('lang', 'Unknown'))
                                        gender = voice.get('gender', 'Unknown')
                                        info += f"- **{name}** ({lang}) - {gender}\n"
                                    else:
                                        info += f"- {voice}\n"
                            else:
                                info += "⚠️ No voices detected\n"
                        else:
                            info += "❌ **Chatterbox TTS**: Not available (using fallback)\n"
                    except Exception as e:
                        info += f"❌ **Error**: {str(e)}\n"
                    
                    # Whisper info
                    info += "\n## 🎧 Whisper System Status\n\n"
                    try:
                        import torch
                        if torch.cuda.is_available():
                            info += "✅ **CUDA**: Available\n"
                            info += f"🎮 **GPU**: {torch.cuda.get_device_name()}\n"
                        else:
                            info += "💻 **CUDA**: Not available (using CPU)\n"
                    except:
                        info += "❓ **CUDA**: Status unknown\n"
                    
                    return info
                
                system_info = gr.Markdown(get_system_info())
                refresh_info_btn = gr.Button("🔄 Refresh System Info", size="sm")
                
                refresh_info_btn.click(
                    fn=lambda: get_system_info(),
                    outputs=system_info
                )

        logger.info("Starting Gradio interface on port 7861")
        demo.launch(
            server_name="0.0.0.0", 
            server_port=7861, 
            share=False,
            show_error=True,
            quiet=False
        )
    
    except Exception as e:
        logger.error(f"Gradio launch error: {e}")
        # Fallback to simple interface
        launch_simple_gradio()

def launch_simple_gradio():
    """Fallback simple Gradio interface if enhanced version fails"""
    try:
        with gr.Blocks(title="Chatterbox TTS and Faster-Whisper Demo") as demo:
            gr.Markdown("## 🗣️ Chatterbox TTS and Faster-Whisper Demo (Simple Mode)")

            with gr.Tab("Transcribe Audio"):
                audio_input = gr.Audio(type="filepath", label="Upload Audio File")
                transcribe_btn = gr.Button("Transcribe", variant="primary")
                transcription_output = gr.Textbox(label="Transcription", lines=5)
                transcribe_btn.click(transcribe_audio, inputs=audio_input, outputs=transcription_output)

            with gr.Tab("Text-to-Speech"):
                text_input = gr.Textbox(label="Enter text", lines=3, value="Hello, this is a test.")
                synthesize_btn = gr.Button("Synthesize", variant="primary")
                audio_output = gr.Audio(label="Generated Audio")
                
                def simple_tts(text):
                    try:
                        from chatterbox_demo import synthesize_tts
                        return synthesize_tts(text)
                    except Exception as e:
                        logger.error(f"Simple TTS error: {e}")
                        from chatterbox_demo import create_fallback_audio
                        return create_fallback_audio(text)
                
                synthesize_btn.click(simple_tts, inputs=text_input, outputs=audio_output)

        logger.info("Starting simple Gradio interface on port 7861")
        demo.launch(server_name="0.0.0.0", server_port=7861, share=False)
    
    except Exception as e:
        logger.error(f"Simple Gradio launch error: {e}")

# Start Gradio in a separate thread with better error handling
def start_gradio_safely():
    """Safely start Gradio with retry logic"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            launch_gradio()
            break
        except Exception as e:
            logger.error(f"Gradio start attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                logger.error("All Gradio start attempts failed, continuing without Gradio")
            else:
                import time
                time.sleep(2)  # Wait before retry

gradio_thread = threading.Thread(target=start_gradio_safely, daemon=True)
gradio_thread.start()

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 7860))
    logger.info(f"Starting FastAPI server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
