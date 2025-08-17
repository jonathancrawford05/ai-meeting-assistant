#!/usr/bin/env python3
"""
Phase 4 Test Script - AI Meeting Assistant
Tests LLM integration and complete workflow functionality
"""

import os
import sys
import json
import time
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

def test_ollama_connection():
    """Test Ollama server connection"""
    print("🔌 Testing Ollama Connection...")
    
    try:
        from llm_processing import test_ollama_connection
        
        status = test_ollama_connection()
        
        if status['connected']:
            print(f"✅ Ollama server connected")
            print(f"   📍 Server URL: {status.get('server_url', 'N/A')}")
            print(f"   🤖 Models available: {status['model_count']}")
            
            for model in status['models']:
                print(f"      • {model}")
            
            return True
        else:
            print(f"❌ Ollama server not connected")
            print(f"   Error: {status.get('error', 'Unknown error')}")
            print(f"   💡 Make sure Ollama is running: ollama serve")
            return False
            
    except Exception as e:
        print(f"❌ Failed to test Ollama connection: {e}")
        print(f"   💡 Check if dependencies are installed: poetry install")
        return False

def test_model_manager():
    """Test model manager functionality"""
    print("\n🧠 Testing Model Manager...")
    
    try:
        from llm_processing import get_model_manager, get_status_info
        
        manager = get_model_manager()
        status = get_status_info()
        
        if status['connected']:
            print(f"✅ Model manager initialized")
            print(f"   🎯 Default model: {status.get('default_model', 'None')}")
            print(f"   📊 Available models: {status['available_models']}")
            
            # List available models
            models = manager.get_model_list()
            for model in models:
                print(f"      • {model['name']} ({model['size']}) - {model['speed']}")
                if model.get('is_default'):
                    print(f"        ^ Default model")
            
            return True
        else:
            print(f"❌ Model manager not ready - Ollama not connected")
            return False
            
    except Exception as e:
        print(f"❌ Failed to test model manager: {e}")
        return False

def test_text_processing():
    """Test text processing workflows"""
    print("\n📝 Testing Text Processing...")
    
    try:
        from llm_processing import process_transcript
        
        # Sample meeting transcript for testing
        test_transcript = """
        John: Good morning everyone, thanks for joining today's project review meeting.
        Sarah: Thanks John. I wanted to update everyone on the marketing campaign progress.
        We've completed the initial designs and they're ready for review.
        Mike: That's great Sarah. I can review those by Friday. 
        John: Perfect. Mike, can you also look into the budget allocation we discussed?
        Mike: Yes, I'll have that analysis ready by next Tuesday.
        Sarah: Should we schedule a follow-up meeting for next week?
        John: Good idea. Let's meet again next Wednesday at 2 PM.
        """
        
        # Test different processing types
        processing_types = ['summary', 'key_points', 'action_items']
        
        all_success = True
        
        for proc_type in processing_types:
            print(f"   Testing {proc_type}...")
            
            result = process_transcript(test_transcript, proc_type)
            
            if result.success:
                print(f"   ✅ {proc_type} completed in {result.processing_time:.2f}s")
                print(f"      Model: {result.model_used}")
                print(f"      Words: {result.word_count}")
                print(f"      Preview: {result.content[:100]}...")
            else:
                print(f"   ❌ {proc_type} failed: {result.error}")
                all_success = False
        
        return all_success
        
    except Exception as e:
        print(f"❌ Failed to test text processing: {e}")
        return False

def test_complete_workflow():
    """Test complete workflow with sample audio"""
    print("\n⚡ Testing Complete Workflow...")
    
    try:
        from llm_enhanced_app import get_app
        
        app = get_app()
        
        # Look for sample audio file
        sample_audio_paths = [
            "data/audio_samples/sample-meeting.wav",
            "../data/audio_samples/sample-meeting.wav",
            "sample-meeting.wav"
        ]
        
        sample_audio = None
        for path in sample_audio_paths:
            if os.path.exists(path):
                sample_audio = path
                break
        
        if not sample_audio:
            print("   ⚠️ No sample audio found - testing components individually")
            
            # Test transcription capability
            status = app.get_system_status()
            if status['features']['transcription']:
                print("   ✅ Transcription component ready")
            else:
                print("   ❌ Transcription component not ready")
            
            # Test LLM capability
            if status['features']['llm_processing']:
                print("   ✅ LLM processing component ready")
            else:
                print("   ❌ LLM processing component not ready")
            
            return status['features']['transcription'] and status['features']['llm_processing']
        
        # Test with actual audio file
        print(f"   🎵 Testing with {sample_audio}")
        
        result = app.process_complete_workflow(
            sample_audio,
            whisper_model='tiny',
            processing_types=['summary', 'action_items']
        )
        
        if result['success']:
            print("   ✅ Complete workflow successful")
            print(f"      Total time: {result['workflow_time']:.2f}s")
            
            if result.get('transcription', {}).get('success'):
                transcript = result['transcription']['transcript']
                print(f"      Transcript: {transcript[:100]}...")
            
            if result.get('llm_processing'):
                for proc_type, llm_result in result['llm_processing'].items():
                    if llm_result.get('success'):
                        print(f"      {proc_type}: ✅")
                    else:
                        print(f"      {proc_type}: ❌")
            
            return True
        else:
            print(f"   ❌ Complete workflow failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to test complete workflow: {e}")
        return False

def test_system_status():
    """Test system status reporting"""
    print("\n📊 Testing System Status...")
    
    try:
        from llm_enhanced_app import get_app
        
        app = get_app()
        status = app.get_system_status()
        
        print("   System Status Report:")
        print(f"   🎤 Whisper Models: {len(status['whisper']['available_models'])}")
        print(f"      Available: {', '.join(status['whisper']['available_models'])}")
        print(f"      Current: {status['whisper']['current_model']}")
        print(f"      GPU Available: {status['whisper']['gpu_available']}")
        
        print(f"   🤖 LLM Status: {'Connected' if status['llm']['connected'] else 'Disconnected'}")
        if status['llm']['connected']:
            print(f"      Available models: {status['llm']['available_models']}")
            print(f"      Current model: {status['current_llm_model']}")
        
        print(f"   ⚡ Features:")
        for feature, enabled in status['features'].items():
            print(f"      {feature}: {'✅' if enabled else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to test system status: {e}")
        return False

def main():
    """Run all Phase 4 tests"""
    print("🧪 AI Meeting Assistant - Phase 4 Testing Suite")
    print("=" * 60)
    
    tests = [
        ("Ollama Connection", test_ollama_connection),
        ("Model Manager", test_model_manager),
        ("Text Processing", test_text_processing),
        ("Complete Workflow", test_complete_workflow),
        ("System Status", test_system_status)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        results[test_name] = test_func()
    
    # Summary
    print(f"\n{'='*60}")
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{test_name:<20} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Phase 4 is ready to use.")
        print("🚀 Start the server: python -m main --version phase4")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed.")
        
        if not results.get("Ollama Connection"):
            print("\n💡 To fix Ollama issues:")
            print("   1. Start Ollama server: ollama serve")
            print("   2. Install required models:")
            print("      ollama pull llama3.2")
            print("      ollama pull llama3.1")
            print("      ollama pull gpt-oss:20b")
        
        print("\n🔧 After fixing issues, run this test again:")
        print("   python test_phase4.py")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
