#!/usr/bin/env python3
"""
Test script for ChatterboxTTS installation and functionality
"""
import sys
import logging
import torch
import tempfile
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_chatterbox_tts():
    """Test ChatterboxTTS import and basic functionality"""
    try:
        logger.info("Testing ChatterboxTTS import...")
        from chatterbox.tts import ChatterboxTTS
        
        logger.info("✅ ChatterboxTTS imported successfully")
        
        # Test device selection
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {device}")
        
        # Test model loading
        logger.info("Loading ChatterboxTTS model...")
        model = ChatterboxTTS.from_pretrained(device)
        logger.info("✅ ChatterboxTTS model loaded successfully")
        
        # Test basic generation
        logger.info("Testing text generation...")
        test_text = "Hello, this is a test of ChatterboxTTS."
        
        wav = model.generate(
            test_text,
            temperature=0.8,
            exaggeration=0.5,
            cfg_weight=0.5,
            min_p=0.05,
            top_p=1.0,
            repetition_penalty=1.2,
        )
        
        logger.info("✅ Text generation successful")
        logger.info(f"Generated audio shape: {wav.shape}")
        logger.info(f"Sample rate: {model.sr}")
        
        # Test saving audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            import soundfile as sf
            sf.write(f.name, wav.squeeze(0).numpy(), model.sr)
            logger.info(f"✅ Audio saved to: {f.name}")
            
            # Check file size
            file_size = os.path.getsize(f.name)
            logger.info(f"Audio file size: {file_size} bytes")
            
            # Clean up
            os.unlink(f.name)
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ ChatterboxTTS import failed: {e}")
        logger.info("Install with: pip install chatterbox-tts")
        return False
    except Exception as e:
        logger.error(f"❌ ChatterboxTTS test failed: {e}")
        return False

def test_chatterbox_vc():
    """Test ChatterboxVC import and basic functionality"""
    try:
        logger.info("Testing ChatterboxVC import...")
        from chatterbox.vc import ChatterboxVC
        
        logger.info("✅ ChatterboxVC imported successfully")
        
        # Test device selection
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {device}")
        
        # Test model loading
        logger.info("Loading ChatterboxVC model...")
        model = ChatterboxVC.from_pretrained(device)
        logger.info("✅ ChatterboxVC model loaded successfully")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ ChatterboxVC import failed: {e}")
        logger.info("Install with: pip install chatterbox-tts")
        return False
    except Exception as e:
        logger.error(f"❌ ChatterboxVC test failed: {e}")
        return False

def test_dependencies():
    """Test all required dependencies"""
    dependencies = {
        'torch': 'PyTorch',
        'torchaudio': 'TorchAudio',
        'gradio': 'Gradio',
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
        'librosa': 'Librosa',
        'soundfile': 'SoundFile',
        'numpy': 'NumPy',
        'transformers': 'Transformers',
        'diffusers': 'Diffusers',
    }
    
    results = {}
    
    for module, name in dependencies.items():
        try:
            __import__(module)
            results[name] = "✅ Available"
            logger.info(f"✅ {name}: Available")
        except ImportError:
            results[name] = "❌ Missing"
            logger.warning(f"❌ {name}: Missing")
    
    return results

def test_cuda():
    """Test CUDA availability"""
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        
        if cuda_available:
            device_count = torch.cuda.device_count()
            device_name = torch.cuda.get_device_name(0)
            memory = torch.cuda.get_device_properties(0).total_memory / 1e9
            
            logger.info(f"✅ CUDA Available: {device_count} device(s)")
            logger.info(f"   Device 0: {device_name}")
            logger.info(f"   Memory: {memory:.1f} GB")
            return True
        else:
            logger.info("💻 CUDA not available, will use CPU")
            return False
            
    except Exception as e:
        logger.error(f"❌ CUDA test failed: {e}")
        return False

def main():
    """Main test function"""
    logger.info("🧪 ChatterboxTTS Installation Test")
    logger.info("=" * 50)
    
    # Test dependencies
    logger.info("\n📦 Testing Dependencies:")
    dep_results = test_dependencies()
    
    # Test CUDA
    logger.info("\n🎮 Testing CUDA:")
    cuda_available = test_cuda()
    
    # Test ChatterboxTTS
    logger.info("\n🗣️ Testing ChatterboxTTS:")
    tts_success = test_chatterbox_tts()
    
    # Test ChatterboxVC
    logger.info("\n🔄 Testing ChatterboxVC:")
    vc_success = test_chatterbox_vc()
    
    # Summary
    logger.info("\n📊 Test Summary:")
    logger.info("=" * 50)
    
    missing_deps = [name for name, status in dep_results.items() if "❌" in status]
    if missing_deps:
        logger.warning(f"Missing dependencies: {', '.join(missing_deps)}")
    else:
        logger.info("✅ All dependencies available")
    
    logger.info(f"🎮 CUDA: {'Available' if cuda_available else 'Not available (CPU mode)'}")
    logger.info(f"🗣️ ChatterboxTTS: {'Working' if tts_success else 'Failed'}")
    logger.info(f"🔄 ChatterboxVC: {'Working' if vc_success else 'Failed'}")
    
    if tts_success and not missing_deps:
        logger.info("\n🎉 Installation test PASSED! ChatterboxTTS is ready to use.")
        logger.info("You can now run: python app.py")
    else:
        logger.error("\n❌ Installation test FAILED!")
        if missing_deps:
            logger.error("Install missing dependencies with:")
            logger.error("pip install -r requirements.txt")
        if not tts_success:
            logger.error("ChatterboxTTS installation issue - check the error messages above")
    
    return tts_success and not missing_deps

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
