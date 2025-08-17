"""
Configuration settings for the Audio Transcription App
"""

# Model configurations
WHISPER_MODELS = {
    "tiny": {
        "name": "openai/whisper-tiny.en",
        "size": "39 MB",
        "speed": "Very Fast",
        "accuracy": "Good",
        "description": "Fastest model, good for quick transcriptions"
    },
    "base": {
        "name": "openai/whisper-base.en", 
        "size": "74 MB",
        "speed": "Fast",
        "accuracy": "Better",
        "description": "Balanced speed and accuracy"
    },
    "small": {
        "name": "openai/whisper-small.en",
        "size": "244 MB", 
        "speed": "Medium",
        "accuracy": "Good",
        "description": "Better accuracy for longer content"
    },
    "medium": {
        "name": "openai/whisper-medium.en",
        "size": "769 MB",
        "speed": "Slow", 
        "accuracy": "Excellent",
        "description": "High accuracy for professional use"
    }
}

# Audio processing settings
MAX_FILE_SIZE_MB = 100
SUPPORTED_FORMATS = {'.wav', '.mp3', '.m4a', '.flac', '.ogg', '.aac'}
DEFAULT_CHUNK_LENGTH = 30
DEFAULT_BATCH_SIZE = 8

# UI settings
DEFAULT_PORT = 7860
DEFAULT_HOST = "127.0.0.1"  # Local only for security

# Performance settings
ENABLE_GPU = True  # Use GPU if available
CACHE_MODELS = True  # Cache loaded models
