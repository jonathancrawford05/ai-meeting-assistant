"""
LLM Processing Package for AI Meeting Assistant
Phase 4: Ollama LLM Integration
"""

# Core components
from .ollama_client import (
    OllamaClient,
    get_ollama_client,
    test_ollama_connection
)

from .model_manager import (
    ModelManager,
    ModelType,
    ModelSpec,
    get_model_manager,
    get_status_info
)

from .text_processor import (
    MeetingProcessor,
    ProcessingResult,
    get_meeting_processor,
    process_transcript
)

# Convenience functions
__all__ = [
    # Client
    'OllamaClient',
    'get_ollama_client', 
    'test_ollama_connection',
    
    # Model Management
    'ModelManager',
    'ModelType',
    'ModelSpec', 
    'get_model_manager',
    'get_status_info',
    
    # Processing
    'MeetingProcessor',
    'ProcessingResult',
    'get_meeting_processor',
    'process_transcript'
]
