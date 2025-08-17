#!/usr/bin/env python3
"""
Test the Phase 4 Working Implementation
Quick validation of the new clean HTML/CSS/JS approach
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / 'src'))

def test_web_files():
    """Test that all web files exist and have content"""
    print("🔍 Testing web files...")
    
    web_dir = Path(__file__).parent / 'src' / 'web'
    required_files = {
        'index.html': 'AI Meeting Assistant',
        'style.css': 'body {',
        'app.js': 'function'
    }
    
    if not web_dir.exists():
        print(f"❌ Web directory not found: {web_dir}")
        return False
    
    for filename, expected_content in required_files.items():
        file_path = web_dir / filename
        if not file_path.exists():
            print(f"❌ Missing file: {filename}")
            return False
        
        try:
            content = file_path.read_text()
            if expected_content not in content:
                print(f"❌ File {filename} doesn't contain expected content")
                return False
            print(f"✅ {filename} - {len(content)} characters")
        except Exception as e:
            print(f"❌ Error reading {filename}: {e}")
            return False
    
    print("✅ All web files present and valid")
    return True

def test_server_import():
    """Test that the new server can be imported"""
    print("🔍 Testing server import...")
    
    try:
        from src.phase4_working_server import Phase4WorkingHandler
        print("✅ Phase4WorkingHandler imported successfully")
        
        from src.llm_enhanced_app import get_app
        app = get_app()
        print("✅ LLM enhanced app imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_system_components():
    """Test system components"""
    print("🔍 Testing system components...")
    
    try:
        from src.llm_enhanced_app import get_app
        app = get_app()
        
        # Test status
        status = app.get_system_status()
        print(f"✅ System status: Whisper={len(status.get('whisper', {}).get('available_models', []))} models")
        print(f"✅ LLM status: {'Connected' if status.get('llm', {}).get('connected') else 'Disconnected'}")
        
        return True
    except Exception as e:
        print(f"❌ System test failed: {e}")
        return False

def test_config():
    """Test configuration"""
    print("🔍 Testing configuration...")
    
    try:
        from src import config
        
        print(f"✅ Whisper models: {len(config.WHISPER_MODELS)}")
        print(f"✅ LLM models: {len(config.LLM_MODELS)}")
        print(f"✅ Processing types: {len(config.PROCESSING_TYPES)}")
        
        return True
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Phase 4 Working Implementation")
    print("=" * 50)
    
    tests = [
        ("Web Files", test_web_files),
        ("Server Import", test_server_import),
        ("System Components", test_system_components),
        ("Configuration", test_config)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Test: {test_name}")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print(f"\n{'=' * 50}")
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Phase 4 Working is ready to use.")
        print("\n🚀 To start the server:")
        print("   cd src")
        print("   python -m main --version phase4-working")
        print("   Visit http://localhost:8080")
        return True
    else:
        print("❌ Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
