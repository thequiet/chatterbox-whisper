#!/usr/bin/env python3

"""
Quick test script for TTS enhancements
"""

import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_tts_imports():
    """Test if the TTS libraries can be imported"""
    results = {}
    
    # Test gTTS
    try:
        from gtts import gTTS
        results['gTTS'] = "✅ Available"
        logger.info("gTTS imported successfully")
    except ImportError as e:
        results['gTTS'] = f"❌ Not available: {e}"
    
    # Test Coqui TTS  
    try:
        from TTS.api import TTS
        results['Coqui TTS'] = "✅ Available"
        logger.info("Coqui TTS imported successfully")
    except ImportError as e:
        results['Coqui TTS'] = f"❌ Not available: {e}"
    
    # Test pyttsx3
    try:
        import pyttsx3
        results['pyttsx3'] = "✅ Available"
        logger.info("pyttsx3 imported successfully")
    except ImportError as e:
        results['pyttsx3'] = f"❌ Not available: {e}"
    
    return results

def test_chatterbox_demo():
    """Test the chatterbox_demo module"""
    try:
        from chatterbox_demo import initialize_tts, get_voice_options
        
        print("🔄 Testing TTS initialization...")
        tts, voices = initialize_tts()
        
        if tts:
            print(f"✅ TTS System initialized: {type(tts).__name__}")
            print(f"📢 Available voices: {len(voices)}")
            
            voice_options = get_voice_options()
            print(f"🎵 Voice options: {voice_options}")
            
            return True
        else:
            print("❌ TTS initialization failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing chatterbox_demo: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing TTS System Enhancements")
    print("=" * 40)
    
    # Test imports
    print("\n📦 Testing TTS Library Imports:")
    import_results = test_tts_imports()
    for lib, status in import_results.items():
        print(f"  {lib}: {status}")
    
    # Test chatterbox_demo
    print("\n🔧 Testing Chatterbox Demo Module:")
    demo_success = test_chatterbox_demo()
    
    # Summary
    print("\n📊 Test Summary:")
    available_libs = [lib for lib, status in import_results.items() if "✅" in status]
    print(f"  Available TTS libraries: {len(available_libs)}")
    print(f"  TTS system functional: {'✅ Yes' if demo_success else '❌ No'}")
    
    if available_libs:
        print(f"\n🎉 Recommended for production: {available_libs[0]}")
    else:
        print("\n⚠️  No TTS libraries available - install with:")
        print("     pip install gTTS TTS pyttsx3")
