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

# ===== LLM PROCESSING SETTINGS (Phase 4) =====

# Ollama server configuration
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_TIMEOUT = 300  # 5 minutes for long processing

# Available LLM models (based on user's installed models)
LLM_MODELS = {
    "llama3.2": {
        "name": "llama3.2:latest",
        "display_name": "Llama 3.2",
        "size": "2.0 GB",
        "speed": "Fast",
        "description": "Latest Llama model - fast and efficient for most tasks",
        "recommended_for": ["Quick summaries", "Action items", "General processing"],
        "default": True
    },
    "llama3.1": {
        "name": "llama3.1:latest",
        "display_name": "Llama 3.1", 
        "size": "4.9 GB",
        "speed": "Medium",
        "description": "Balanced performance with strong reasoning capabilities",
        "recommended_for": ["Detailed analysis", "Complex summaries", "Meeting insights"],
        "default": False
    },
    "gpt-oss": {
        "name": "gpt-oss:20b",
        "display_name": "GPT-OSS 20B",
        "size": "13 GB",
        "speed": "Slower", 
        "description": "Most capable model for complex analysis and detailed processing",
        "recommended_for": ["Complex analysis", "Detailed reports", "Professional summaries"],
        "default": False
    }
}

# Default LLM model
DEFAULT_LLM_MODEL = "llama3.2"

# Processing options
PROCESSING_TYPES = {
    "summary": {
        "name": "Meeting Summary",
        "description": "Create a comprehensive summary of the meeting",
        "icon": "📝"
    },
    "key_points": {
        "name": "Key Points", 
        "description": "Extract the most important points discussed",
        "icon": "🔑"
    },
    "action_items": {
        "name": "Action Items",
        "description": "Identify tasks and follow-up items",
        "icon": "✅"
    },
    "insights": {
        "name": "Meeting Insights",
        "description": "Analyze meeting tone, sentiment, and next steps", 
        "icon": "💡"
    }
}

# LLM processing settings
LLM_TEMPERATURE = 0.7  # Creativity vs consistency (0.0 to 1.0)
LLM_MAX_TOKENS = 2048  # Maximum response length
LLM_TOP_P = 0.9       # Nucleus sampling

# Enable/disable features
ENABLE_LLM_PROCESSING = True
ENABLE_BATCH_PROCESSING = True  # Process multiple files
ENABLE_EXPORT_WITH_LLM = True   # Export with LLM results
