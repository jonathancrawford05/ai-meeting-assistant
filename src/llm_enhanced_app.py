"""
Enhanced LLM Application for AI Meeting Assistant - Phase 4
Clean, properly formatted core application logic
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

from transformers import pipeline
import torch

# Import LLM processing components
from llm_processing import (
    get_ollama_client,
    get_model_manager,
    get_meeting_processor,
    process_transcript,
    get_status_info
)

import config


class LLMEnhancedTranscriptionApp:
    """Complete meeting assistant with speech-to-text and LLM processing"""
    
    def __init__(self):
        """Initialize the enhanced app"""
        self.setup_logging()
        self.models = {}
        self.current_whisper_model = "tiny"
        self.current_llm_model = None
        
        # Initialize LLM components
        self.setup_llm_components()
        
        # Load default Whisper model
        self.load_whisper_model(self.current_whisper_model)
    
    def setup_logging(self):
        """Configure logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_llm_components(self):
        """Initialize LLM processing components"""
        try:
            # Test Ollama connection
            self.ollama_client = get_ollama_client()
            self.model_manager = get_model_manager()
            self.meeting_processor = get_meeting_processor()
            
            # Get LLM status
            self.llm_status = get_status_info()
            
            if self.llm_status.get('connected', False):
                self.current_llm_model = self.llm_status.get('default_model')
                self.logger.info(f"LLM integration ready. Default model: {self.current_llm_model}")
            else:
                self.logger.warning("LLM integration not available - Ollama server not connected")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize LLM components: {e}")
            self.llm_status = {'connected': False, 'error': str(e)}
    
    def load_whisper_model(self, model_key: str) -> str:
        """Load specified Whisper model"""
        try:
            if model_key not in config.WHISPER_MODELS:
                return f"❌ Unknown model: {model_key}"
            
            model_config = config.WHISPER_MODELS[model_key]
            model_name = model_config["name"]
            
            self.logger.info(f"Loading Whisper model: {model_name}")
            start_time = time.time()
            
            # Load model with GPU support if available
            device = 0 if torch.cuda.is_available() and config.ENABLE_GPU else -1
            
            self.models[model_key] = pipeline(
                "automatic-speech-recognition",
                model=model_name,
                chunk_length_s=config.DEFAULT_CHUNK_LENGTH,
                device=device
            )
            
            load_time = time.time() - start_time
            self.current_whisper_model = model_key
            
            description = model_config['description']
            return f"✅ Loaded {description} in {load_time:.1f}s"
            
        except Exception as e:
            self.logger.error(f"Failed to load model {model_key}: {e}")
            return f"❌ Failed to load model: {str(e)}"
    
    def transcribe_audio(self, audio_file_path: str, model_key: str = None) -> Dict[str, Any]:
        """Transcribe audio file using Whisper"""
        try:
            # Use current model if none specified
            if model_key is None:
                model_key = self.current_whisper_model
            
            # Load model if not already loaded
            if model_key not in self.models:
                load_result = self.load_whisper_model(model_key)
                if "❌" in load_result:
                    return {
                        'success': False,
                        'error': load_result,
                        'transcript': '',
                        'processing_time': 0,
                        'model_used': model_key
                    }
            
            self.logger.info(f"Starting transcription with {model_key}")
            start_time = time.time()
            
            # Perform transcription
            result = self.models[model_key](
                audio_file_path,
                batch_size=config.DEFAULT_BATCH_SIZE
            )
            
            transcript = result["text"].strip()
            processing_time = time.time() - start_time
            
            # Get file info
            file_size = os.path.getsize(audio_file_path) if os.path.exists(audio_file_path) else 0
            
            return {
                'success': True,
                'transcript': transcript,
                'processing_time': processing_time,
                'model_used': model_key,
                'word_count': len(transcript.split()),
                'file_size': file_size,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Transcription failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'transcript': '',
                'processing_time': 0,
                'model_used': model_key or 'unknown'
            }
    
    def process_with_llm(
        self, 
        transcript: str, 
        processing_type: str, 
        llm_model: str = None
    ) -> Dict[str, Any]:
        """Process transcript using LLM"""
        try:
            if not self.llm_status.get('connected', False):
                return {
                    'success': False,
                    'error': 'LLM processing not available - Ollama server not connected',
                    'content': '',
                    'processing_time': 0
                }
            
            # Use default model if none specified
            if llm_model is None:
                llm_model = self.current_llm_model
            
            self.logger.info(f"Processing transcript with {llm_model} for {processing_type}")
            
            # Process using text processor
            result = process_transcript(transcript, processing_type, llm_model)
            
            return {
                'success': result.success,
                'content': result.content,
                'processing_time': result.processing_time,
                'model_used': result.model_used,
                'word_count': result.word_count,
                'error': result.error,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"LLM processing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'content': '',
                'processing_time': 0
            }
    
    def process_complete_workflow(
        self, 
        audio_file_path: str,
        whisper_model: str = None,
        llm_model: str = None,
        processing_types: List[str] = None
    ) -> Dict[str, Any]:
        """Complete workflow: transcribe + LLM processing"""
        try:
            workflow_start = time.time()
            
            # Step 1: Transcribe audio
            self.logger.info("Starting complete workflow: transcription + LLM processing")
            transcription_result = self.transcribe_audio(audio_file_path, whisper_model)
            
            if not transcription_result['success']:
                error_msg = transcription_result.get('error', 'Unknown error')
                return {
                    'success': False,
                    'error': f"Transcription failed: {error_msg}",
                    'workflow_time': time.time() - workflow_start
                }
            
            transcript = transcription_result['transcript']
            
            # Step 2: LLM processing (if available and requested)
            llm_results = {}
            
            if self.llm_status.get('connected', False) and processing_types:
                for proc_type in processing_types:
                    llm_result = self.process_with_llm(transcript, proc_type, llm_model)
                    llm_results[proc_type] = llm_result
            
            total_time = time.time() - workflow_start
            
            return {
                'success': True,
                'transcription': transcription_result,
                'llm_processing': llm_results,
                'workflow_time': total_time,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Complete workflow failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'workflow_time': time.time() - workflow_start
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            'whisper': {
                'available_models': list(config.WHISPER_MODELS.keys()),
                'current_model': self.current_whisper_model,
                'loaded_models': list(self.models.keys()),
                'gpu_available': torch.cuda.is_available()
            },
            'llm': self.llm_status,
            'current_llm_model': self.current_llm_model,
            'processing_types': list(config.PROCESSING_TYPES.keys()),
            'features': {
                'transcription': True,
                'llm_processing': self.llm_status.get('connected', False),
                'complete_workflow': self.llm_status.get('connected', False)
            },
            'timestamp': datetime.now().isoformat()
        }


# Global app instance
_app_instance: Optional[LLMEnhancedTranscriptionApp] = None


def get_app() -> LLMEnhancedTranscriptionApp:
    """Get global app instance"""
    global _app_instance
    if _app_instance is None:
        _app_instance = LLMEnhancedTranscriptionApp()
    return _app_instance


if __name__ == "__main__":
    # Test the enhanced app
    print("Testing LLM Enhanced Transcription App...")
    
    app = get_app()
    status = app.get_system_status()
    
    print("\n=== System Status ===")
    print(json.dumps(status, indent=2))
    
    # Test with sample audio if available
    sample_audio = "../data/audio_samples/sample-meeting.wav"
    if os.path.exists(sample_audio):
        print(f"\n=== Testing with {sample_audio} ===")
        
        # Test transcription only
        result = app.transcribe_audio(sample_audio)
        if result['success']:
            print(f"✅ Transcription successful ({result['processing_time']:.2f}s)")
            print(f"Transcript: {result['transcript'][:100]}...")
            
            # Test LLM processing if available
            if status['llm']['connected']:
                print("\n=== Testing LLM Processing ===")
                llm_result = app.process_with_llm(result['transcript'], 'summary')
                if llm_result['success']:
                    print(f"✅ LLM Summary successful ({llm_result['processing_time']:.2f}s)")
                    print(f"Summary: {llm_result['content'][:100]}...")
                else:
                    error_msg = llm_result.get('error', 'Unknown error')
                    print(f"❌ LLM processing failed: {error_msg}")
        else:
            error_msg = result.get('error', 'Unknown error')
            print(f"❌ Transcription failed: {error_msg}")
    else:
        print(f"Sample audio not found: {sample_audio}")
