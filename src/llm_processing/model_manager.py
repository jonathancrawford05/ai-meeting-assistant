"""
Model Manager for AI Meeting Assistant
Manages the three selected Ollama models: llama3.1, llama3.2, and gpt-oss:20b
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from .ollama_client import get_ollama_client, OllamaClient

logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Available model types for the meeting assistant"""
    LLAMA32 = "llama3.2:latest"      # Default - Fast and efficient
    LLAMA31 = "llama3.1:latest"      # Balanced performance
    GPT_OSS = "gpt-oss:20b"          # Most capable, largest


@dataclass
class ModelSpec:
    """Specification for a model"""
    name: str
    display_name: str
    size: str
    speed: str
    capabilities: str
    description: str
    recommended_for: List[str]


class ModelManager:
    """Manages available LLM models for meeting processing"""
    
    # Model specifications based on user's available models
    MODEL_SPECS = {
        ModelType.LLAMA32: ModelSpec(
            name="llama3.2:latest",
            display_name="Llama 3.2",
            size="2.0 GB",
            speed="Fast",
            capabilities="General text processing, summaries",
            description="Latest Llama model - fast and efficient for most tasks",
            recommended_for=["Quick summaries", "Action items", "General processing"]
        ),
        ModelType.LLAMA31: ModelSpec(
            name="llama3.1:latest", 
            display_name="Llama 3.1",
            size="4.9 GB",
            speed="Medium",
            capabilities="Advanced reasoning, detailed analysis",
            description="Balanced performance with strong reasoning capabilities",
            recommended_for=["Detailed analysis", "Complex summaries", "Meeting insights"]
        ),
        ModelType.GPT_OSS: ModelSpec(
            name="gpt-oss:20b",
            display_name="GPT-OSS 20B",
            size="13 GB", 
            speed="Slower",
            capabilities="Advanced reasoning, complex analysis, detailed outputs",
            description="Most capable model for complex analysis and detailed processing",
            recommended_for=["Complex analysis", "Detailed reports", "Professional summaries"]
        )
    }
    
    DEFAULT_MODEL = ModelType.LLAMA32  # User's preferred default
    
    def __init__(self):
        """Initialize model manager"""
        self.ollama_client = get_ollama_client()
        self._available_models = {}
        self._check_model_availability()
    
    def _check_model_availability(self) -> None:
        """Check which of our target models are available"""
        if not self.ollama_client.is_connected():
            logger.warning("Ollama server not connected - models unavailable")
            return
        
        available_ollama_models = self.ollama_client.get_available_models()
        
        for model_type, spec in self.MODEL_SPECS.items():
            if spec.name in available_ollama_models:
                self._available_models[model_type] = spec
                logger.info(f"Model available: {spec.display_name}")
            else:
                logger.warning(f"Model not found: {spec.name}")
    
    def get_available_models(self) -> Dict[ModelType, ModelSpec]:
        """Get dictionary of available models"""
        return self._available_models.copy()
    
    def get_model_list(self) -> List[Dict[str, Any]]:
        """Get list of available models for UI display"""
        return [
            {
                'key': model_type.value,
                'name': spec.display_name,
                'size': spec.size,
                'speed': spec.speed,
                'description': spec.description,
                'recommended_for': spec.recommended_for,
                'is_default': model_type == self.DEFAULT_MODEL
            }
            for model_type, spec in self._available_models.items()
        ]
    
    def get_default_model(self) -> Optional[ModelType]:
        """Get default model if available"""
        if self.DEFAULT_MODEL in self._available_models:
            return self.DEFAULT_MODEL
        
        # Fallback to first available model
        if self._available_models:
            return next(iter(self._available_models.keys()))
        
        return None
    
    def get_model_by_name(self, model_name: str) -> Optional[ModelType]:
        """Get model type by name string"""
        for model_type, spec in self._available_models.items():
            if spec.name == model_name or model_type.value == model_name:
                return model_type
        return None
    
    def is_model_available(self, model_type: ModelType) -> bool:
        """Check if specific model is available"""
        return model_type in self._available_models
    
    def get_model_spec(self, model_type: ModelType) -> Optional[ModelSpec]:
        """Get specification for a model"""
        return self._available_models.get(model_type)
    
    def create_model_instance(self, model_type: ModelType, **kwargs):
        """Create LangChain model instance"""
        if model_type not in self._available_models:
            raise ValueError(f"Model {model_type.value} not available")
        
        spec = self._available_models[model_type]
        return self.ollama_client.create_langchain_model(spec.name, **kwargs)
    
    def test_model(self, model_type: ModelType) -> bool:
        """Test if model is working correctly"""
        if model_type not in self._available_models:
            return False
        
        spec = self._available_models[model_type]
        return self.ollama_client.test_model(spec.name)
    
    def get_recommended_model(self, task_type: str) -> Optional[ModelType]:
        """
        Get recommended model for specific task type
        
        Args:
            task_type: Type of task (e.g., 'summary', 'analysis', 'action_items')
            
        Returns:
            Recommended model type
        """
        task_lower = task_type.lower()
        
        # Task-specific recommendations
        if any(word in task_lower for word in ['quick', 'simple', 'action']):
            # For quick tasks, prefer fastest available
            for model_type in [ModelType.LLAMA32, ModelType.LLAMA31, ModelType.GPT_OSS]:
                if model_type in self._available_models:
                    return model_type
        
        elif any(word in task_lower for word in ['detailed', 'complex', 'analysis']):
            # For complex tasks, prefer most capable
            for model_type in [ModelType.GPT_OSS, ModelType.LLAMA31, ModelType.LLAMA32]:
                if model_type in self._available_models:
                    return model_type
        
        # Default fallback
        return self.get_default_model()


# Global instance
_model_manager: Optional[ModelManager] = None


def get_model_manager() -> ModelManager:
    """Get global model manager instance"""
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager()
    return _model_manager


def get_status_info() -> Dict[str, Any]:
    """Get comprehensive status information"""
    try:
        manager = get_model_manager()
        
        return {
            'connected': manager.ollama_client.is_connected(),
            'available_models': len(manager.get_available_models()),
            'default_model': manager.get_default_model().value if manager.get_default_model() else None,
            'models': manager.get_model_list()
        }
    except Exception as e:
        return {
            'connected': False,
            'error': str(e),
            'available_models': 0,
            'models': []
        }


if __name__ == "__main__":
    # Test the model manager
    import json
    
    print("Testing Model Manager...")
    status = get_status_info()
    print(json.dumps(status, indent=2))
    
    # Test individual models
    manager = get_model_manager()
    for model_type in [ModelType.LLAMA32, ModelType.LLAMA31, ModelType.GPT_OSS]:
        if manager.is_model_available(model_type):
            spec = manager.get_model_spec(model_type)
            working = manager.test_model(model_type)
            print(f"\n{spec.display_name}: {'✅ Working' if working else '❌ Error'}")
