#!/usr/bin/env python3
"""
Setup script for AI Meeting Assistant
Downloads sample audio file and verifies dependencies
"""

import os
import sys
import subprocess
from pathlib import Path

def check_ffmpeg():
    """Check if ffmpeg is installed"""
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        print("✅ ffmpeg is installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ ffmpeg is not installed")
        print("Please install ffmpeg using: brew install ffmpeg")
        return False

def download_sample_audio():
    """Download the sample audio file"""
    print("📥 Downloading sample audio file...")
    
    # Change to the audio samples directory
    audio_dir = Path(__file__).parent / "data" / "audio_samples"
    os.chdir(audio_dir)
    
    # Run the download script
    subprocess.run([sys.executable, "sample_audio_speech2text.py"], check=True)
    
    # Check if file was downloaded
    if (audio_dir / "sample-meeting.wav").exists():
        print("✅ Sample audio file downloaded successfully")
        return True
    else:
        print("❌ Failed to download sample audio file")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up AI Meeting Assistant...")
    
    # Check ffmpeg
    if not check_ffmpeg():
        sys.exit(1)
    
    # Download sample audio
    if not download_sample_audio():
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Run 'poetry install' to install dependencies")
    print("2. Run 'poetry shell' to activate the virtual environment")
    print("3. Start developing your AI Meeting Assistant!")

if __name__ == "__main__":
    main()
