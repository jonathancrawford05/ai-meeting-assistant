#!/usr/bin/env python3
"""
Fallback command-line transcription script
Use this if Gradio has compatibility issues
"""
import os
import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

def test_whisper_directly():
    """Test Whisper transcription directly without Gradio"""
    print("🧪 Testing Whisper transcription directly...\n")
    
    try:
        from transformers import pipeline
        
        # Initialize pipeline
        print("📥 Loading Whisper model...")
        pipe = pipeline(
            "automatic-speech-recognition",
            model="openai/whisper-tiny.en",
            chunk_length_s=30,
        )
        print("✅ Model loaded successfully\n")
        
        # Test with sample audio if available
        sample_path = Path("../data/audio_samples/sample-meeting.wav")
        if sample_path.exists():
            print(f"🎵 Transcribing sample audio: {sample_path}")
            start_time = time.time()
            
            result = pipe(str(sample_path.resolve()), batch_size=8)["text"]
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            print(f"\n⏱️  Processing time: {processing_time:.1f} seconds")
            print(f"📄 Transcription result:\n")
            print("-" * 50)
            print(result.strip())
            print("-" * 50)
            
        else:
            print(f"⚠️  Sample audio not found at: {sample_path}")
            print("💡 You can test with your own audio file by modifying this script")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during transcription: {e}")
        return False

def main():
    """Main function"""
    print("🎤 AI Meeting Assistant - Direct Whisper Test")
    print("=" * 50)
    
    success = test_whisper_directly()
    
    if success:
        print("\n🎉 Whisper transcription is working correctly!")
        print("\n💡 If Gradio has issues, you can:")
        print("1. Use this script directly for transcription")
        print("2. Try different Gradio versions")
        print("3. Use a different web framework")
    else:
        print("\n⚠️  Whisper transcription failed")
        print("💡 Check your dependencies and try reinstalling")

if __name__ == "__main__":
    main()
