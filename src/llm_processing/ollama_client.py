"""
Ollama Client Integration for AI Meeting Assistant
Provides connection to local Ollama server for LLM processing
"""

import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

import ollama
from langchain_ollama import OllamaLLM

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class ModelInfo:
    """Information about available Ollama models"""
    name: str
    size: str
    description: str
    capabilities: List[str]
    speed: str


class OllamaClient:
    """Client for interacting with local Ollama server"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        """
        Initialize Ollama client
        
        Args:
            base_url: Ollama server URL (default: http://localhost:11434)
        """
        self.base_url = base_url
        self.client = ollama.Client(host=base_url)
        self._available_models = {}
        self._langchain_models = {}
        
        # Initialize available models
        self._discover_models()
    
    def _discover_models(self) -> None:
        """Discover available models on Ollama server"""
        try:
            models = self.client.list()
            logger.info(f"Found {len(models['models'])} models on Ollama server")
            
            # Store raw model info
            for model in models['models']:
                model_name = model['name']
                self._available_models[model_name] = model
                
        except Exception as e:
            logger.error(f"Failed to connect to Ollama server: {e}")
            self._available_models = {}
    
    def is_connected(self) -> bool:
        """Check if connected to Ollama server"""
        try:
            self.client.list()
            return True
        except Exception:
            return False
    
    def get_available_models(self) -> List[str]:
        """Get list of available model names"""
        return list(self._available_models.keys())
    
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific model"""
        return self._available_models.get(model_name)
    
    def create_langchain_model(self, model_name: str, **kwargs) -> OllamaLLM:
        """
        Create a LangChain-compatible Ollama model instance
        
        Args:
            model_name: Name of the Ollama model
            **kwargs: Additional parameters for the model
            
        Returns:
            OllamaLLM instance
        """
        if model_name not in self._langchain_models:
            default_params = {
                'base_url': self.base_url,
                'temperature': 0.7,
                'top_p': 0.9,
                'num_predict': 2048,
            }
            default_params.update(kwargs)
            
            self._langchain_models[model_name] = OllamaLLM(
                model=model_name,
                **default_params
            )
        
        return self._langchain_models[model_name]
    
    def generate(self, model_name: str, prompt: str, **kwargs) -> str:
        """
        Generate text using specified model
        
        Args:
            model_name: Name of the model to use
            prompt: Input text prompt
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text response
        """
        try:
            response = self.client.generate(
                model=model_name,
                prompt=prompt,
                **kwargs
            )
            return response['response']
        except Exception as e:
            logger.error(f"Generation failed with model {model_name}: {e}")
            raise
    
    def chat(self, model_name: str, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Chat with model using conversation format
        
        Args:
            model_name: Name of the model to use
            messages: List of conversation messages
            **kwargs: Additional parameters
            
        Returns:
            Model response
        """
        try:
            response = self.client.chat(
                model=model_name,
                messages=messages,
                **kwargs
            )
            return response['message']['content']
        except Exception as e:
            logger.error(f"Chat failed with model {model_name}: {e}")
            raise
    
    def test_model(self, model_name: str) -> bool:
        """
        Test if a specific model is working
        
        Args:
            model_name: Model to test
            
        Returns:
            True if model responds correctly
        """
        try:
            test_prompt = "Hello! Please respond with 'Model working correctly.'"
            response = self.generate(model_name, test_prompt, num_predict=10)
            return "working" in response.lower() or "hello" in response.lower()
        except Exception as e:
            logger.error(f"Model test failed for {model_name}: {e}")
            return False


# Global client instance (lazy initialization)
_ollama_client: Optional[OllamaClient] = None


def get_ollama_client() -> OllamaClient:
    """Get global Ollama client instance (singleton pattern)"""
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = OllamaClient()
    return _ollama_client


def test_ollama_connection() -> Dict[str, Any]:
    """
    Test Ollama connection and return status info
    
    Returns:
        Dictionary with connection status and available models
    """
    try:
        client = get_ollama_client()
        
        if not client.is_connected():
            return {
                'connected': False,
                'error': 'Cannot connect to Ollama server. Is it running?',
                'models': []
            }
        
        models = client.get_available_models()
        
        return {
            'connected': True,
            'server_url': client.base_url,
            'models': models,
            'model_count': len(models)
        }
        
    except Exception as e:
        return {
            'connected': False,
            'error': str(e),
            'models': []
        }


if __name__ == "__main__":
    # Quick test when run directly
    print("Testing Ollama connection...")
    status = test_ollama_connection()
    print(json.dumps(status, indent=2))
