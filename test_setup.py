#!/usr/bin/env python3
"""
Test script to validate working AI Meeting Assistant components
Updated for streamlined project structure (simple + enhanced-simple servers)
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_core_imports():
    """Test that core working components can be imported"""
    print("🧪 Testing core imports...")
    
    try:
        import config
        print("✅ Config module imported")
    except Exception as e:
        print(f"❌ Failed to import config: {e}")
        return False
    
    try:
        import simple_server
        print("✅ Simple server module imported")
    except Exception as e:
        print(f"❌ Failed to import simple server: {e}")
        return False
    
    try:
        import enhanced_simple_server
        print("✅ Enhanced simple server module imported")
    except Exception as e:
        print(f"❌ Failed to import enhanced simple server: {e}")
        return False
    
    return True

def test_whisper_functionality():
    """Test core Whisper functionality"""
    print("🧪 Testing Whisper functionality...")
    
    try:
        # Test the working Whisper test script
        import test_whisper_direct
        print("✅ Whisper test module imported")
        
        # Test basic Whisper import
        from transformers import pipeline
        print("✅ Transformers pipeline import successful")
        
        return True
    except Exception as e:
        print(f"❌ Failed Whisper test: {e}")
        return False

def test_whisper_model_loading():
    """Test actual Whisper model loading (slower test)"""
    print("🧪 Testing Whisper model loading...")
    
    try:
        from transformers import pipeline
        pipe = pipeline(
            "automatic-speech-recognition",
            model="openai/whisper-tiny.en"
        )
        print("✅ Whisper model loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to load Whisper model: {e}")
        return False

def test_sample_audio_file():
    """Test if sample audio file exists"""
    print("🧪 Testing sample audio file...")
    
    audio_path = Path("data/audio_samples/sample-meeting.wav")
    if audio_path.exists():
        file_size = audio_path.stat().st_size / (1024 * 1024)  # MB
        print(f"✅ Sample audio file found: {audio_path} ({file_size:.1f}MB)")
        return True
    else:
        print(f"❌ Sample audio file not found: {audio_path}")
        print("💡 Run the setup script to download: python setup.py")
        return False

def test_server_creation():
    """Test that servers can be created without launching"""
    print("🧪 Testing server creation...")
    
    try:
        # Test simple server handler creation
        import simple_server
        handler_class = simple_server.SimpleTranscriptionHandler
        print("✅ Simple server handler class accessible")
        
        # Test enhanced server handler creation  
        import enhanced_simple_server
        enhanced_handler_class = enhanced_simple_server.EnhancedTranscriptionHandler
        print("✅ Enhanced server handler class accessible")
        
        return True
    except Exception as e:
        print(f"❌ Failed server creation test: {e}")
        return False

def test_project_structure():
    """Test that project structure is correct"""
    print("🧪 Testing project structure...")
    
    required_paths = [
        "src/main.py",
        "src/simple_server.py", 
        "src/enhanced_simple_server.py",
        "src/config.py",
        "src/test_whisper_direct.py",
        "src/llm_processing/",  # Phase 4 addition
        "src/llm_enhanced_app.py",  # Phase 4 addition
        "src/phase4_server.py",  # Phase 4 addition
        "data/audio_samples/",
        "archive/",
        "pyproject.toml"
    ]
    
    missing_paths = []
    for path in required_paths:
        if not Path(path).exists():
            missing_paths.append(path)
    
    if missing_paths:
        print(f"❌ Missing required paths: {missing_paths}")
        return False
    else:
        print("✅ All required project paths exist")
        return True

def test_phase4_imports():
    """Test Phase 4 LLM components can be imported"""
    print("🧪 Testing Phase 4 imports...")
    
    try:
        import llm_processing
        print("✅ LLM processing package imported")
    except Exception as e:
        print(f"❌ Failed to import LLM processing: {e}")
        return False
    
    try:
        import llm_enhanced_app
        print("✅ LLM enhanced app imported")
    except Exception as e:
        print(f"❌ Failed to import LLM enhanced app: {e}")
        return False
    
    try:
        import phase4_server
        print("✅ Phase 4 server imported")
    except Exception as e:
        print(f"❌ Failed to import Phase 4 server: {e}")
        return False
    
    return True

def test_ollama_integration():
    """Test Ollama integration (optional - may fail if Ollama not running)"""
    print("🧪 Testing Ollama integration...")
    
    try:
        from llm_processing import test_ollama_connection
        
        status = test_ollama_connection()
        
        if status['connected']:
            print(f"✅ Ollama server connected ({status['model_count']} models)")
            return True
        else:
            print(f"⚠️ Ollama server not connected - LLM features will be unavailable")
            print(f"   💡 Start Ollama server to enable: ollama serve")
            return "optional"  # Not a failure, just unavailable
            
    except Exception as e:
        print(f"⚠️ Could not test Ollama integration: {e}")
        print(f"   💡 This is optional - Phase 4 will gracefully degrade")
        return "optional"

def main():
    """Run all tests for streamlined project + Phase 4"""
    print("🚀 Running AI Meeting Assistant Tests (Complete + Phase 4)\n")
    
    tests = [
        ("Project Structure", test_project_structure),
        ("Core Imports", test_core_imports),
        ("Server Creation", test_server_creation),
        ("Sample Audio File", test_sample_audio_file),
        ("Whisper Functionality", test_whisper_functionality),
        ("Whisper Model Loading", test_whisper_model_loading),
        ("Phase 4 Imports", test_phase4_imports),
        ("Ollama Integration", test_ollama_integration),
    ]
    
    results = []
    optional_tests = []
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        result = test_func()
        
        if result == "optional":
            optional_tests.append(test_name)
            results.append((test_name, True))  # Count as passed for summary
        else:
            results.append((test_name, result))
    
    print("\n" + "="*70)
    print("📊 TEST RESULTS")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        if test_name in optional_tests:
            status = "🟡 OPTIONAL"
        else:
            status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:25} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your setup is ready.")
        print("\n🚀 Available versions:")
        print("   • simple          : Basic transcription (Phase 1)")
        print("   • enhanced-simple : Full transcription features (Phase 3)")
        print("   • phase4          : Complete LLM integration (Phase 4)")
        
        print("\n🔥 Quick Start:")
        print("   cd src")
        print("   python -m main --version enhanced-simple  # Recommended")
        print("   python -m main --version phase4          # Latest with LLM")
        
        if optional_tests:
            print("\n💡 Optional Features:")
            for test_name in optional_tests:
                if "Ollama" in test_name:
                    print("   • LLM Processing: Start Ollama server to enable")
                    print("     - ollama serve")
                    print("     - ollama pull llama3.2")
    else:
        print("\n⚠️  Some tests failed. Please resolve issues before proceeding.")
        print("\n🔧 Common solutions:")
        print("   • Run 'python setup.py' to download sample audio")
        print("   • Run 'poetry install' to ensure dependencies")
        print("   • Check that you're in the correct directory")
        
        failed_phase4 = any(not result for test_name, result in results if "Phase 4" in test_name or "Ollama" in test_name)
        if failed_phase4:
            print("\n🚑 Fallback: Phase 3 should still work:")
            print("   python -m main --version enhanced-simple")
    
    print("\n🧪 Advanced Testing:")
    print("   python test_phase4.py                    # Comprehensive Phase 4 tests")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
