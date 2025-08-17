#!/usr/bin/env python3
"""
Quick Phase 4 Import Test
Tests if all Phase 4 components can be imported without errors
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

def test_imports():
    """Test all imports"""
    print("🧪 Testing Phase 4 Imports...")
    
    try:
        # Test core config
        import config
        print("✅ Config imported")
        
        # Test LLM processing package
        import llm_processing
        print("✅ LLM processing package imported")
        
        # Test individual components
        from llm_processing import get_ollama_client, get_model_manager, get_meeting_processor
        print("✅ LLM processing components imported")
        
        # Test enhanced app
        import llm_enhanced_app
        print("✅ LLM enhanced app imported")
        
        # Test Phase 4 server
        import phase4_server
        print("✅ Phase 4 server imported")
        
        # Test main entry point
        import main
        print("✅ Main entry point imported")
        
        print("\n🎉 All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_configuration():
    """Test configuration values"""
    print("\n🧪 Testing Configuration...")
    
    try:
        import config
        
        # Test LLM config
        assert hasattr(config, 'LLM_MODELS'), "LLM_MODELS not found"
        assert hasattr(config, 'PROCESSING_TYPES'), "PROCESSING_TYPES not found"
        assert hasattr(config, 'OLLAMA_BASE_URL'), "OLLAMA_BASE_URL not found"
        
        print(f"✅ LLM Models configured: {len(config.LLM_MODELS)}")
        print(f"✅ Processing types: {len(config.PROCESSING_TYPES)}")
        print(f"✅ Ollama URL: {config.OLLAMA_BASE_URL}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Quick Phase 4 Import Test")
    print("=" * 40)
    
    success = test_imports() and test_configuration()
    
    if success:
        print("\n✅ Phase 4 implementation looks good!")
        print("📋 Next steps:")
        print("   1. python test_setup.py      # Full system test")
        print("   2. python test_phase4.py     # Comprehensive Phase 4 test") 
        print("   3. cd src && python -m main --version phase4")
    else:
        print("\n❌ Issues found. Check the errors above.")
    
    sys.exit(0 if success else 1)
