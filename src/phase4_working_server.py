"""
Phase 4 Server - Clean and Working
Complete rewrite with proper file handling and separate HTML/CSS/JS files
"""

import os
import json
import time
import tempfile
import cgi
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from io import BytesIO

from llm_enhanced_app import get_app
import config


class Phase4WorkingHandler(SimpleHTTPRequestHandler):
    """Clean, working Phase 4 handler with proper file upload handling"""
    
    def __init__(self, *args, **kwargs):
        self.app = get_app()
        # Set the directory to serve static files from
        super().__init__(*args, directory=os.path.join(os.path.dirname(__file__), 'web'), **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # API endpoints
        if path == '/api/status':
            self.serve_status()
        elif path == '/api/models':
            self.serve_models_info()
        # Static files (HTML, CSS, JS)
        elif path == '/' or path == '/index.html':
            # Serve index.html from web directory
            self.path = '/index.html'
            super().do_GET()
        elif path.startswith('/') and (path.endswith('.css') or path.endswith('.js') or path.endswith('.html')):
            # Serve static files from web directory
            super().do_GET()
        else:
            self.send_error(404, "Page not found")
    
    def do_POST(self):
        """Handle POST requests with proper multipart parsing"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        try:
            if path == '/api/transcribe':
                self.handle_transcription()
            elif path == '/api/process-llm':
                self.handle_llm_processing()
            elif path == '/api/complete-workflow':
                self.handle_complete_workflow()
            else:
                self.send_error(404, "Endpoint not found")
        except Exception as e:
            print(f"❌ POST request failed: {str(e)}")
            self.send_error_response(f"Request failed: {str(e)}")
    
    def serve_status(self):
        """Serve system status"""
        try:
            status = self.app.get_system_status()
            print(f"📊 Status request: Whisper={len(status.get('whisper', {}).get('available_models', []))} models, LLM={'connected' if status.get('llm', {}).get('connected') else 'disconnected'}")
            self.send_json_response(status)
        except Exception as e:
            print(f"❌ Status error: {str(e)}")
            self.send_error_response(f"Failed to get status: {str(e)}")
    
    def serve_models_info(self):
        """Serve model information"""
        try:
            models_info = {
                'whisper_models': {
                    key: {
                        **value,
                        'is_current': key == self.app.current_whisper_model
                    }
                    for key, value in config.WHISPER_MODELS.items()
                },
                'llm_models': config.LLM_MODELS,
                'processing_types': config.PROCESSING_TYPES
            }
            print(f"🤖 Models info request: {len(models_info['whisper_models'])} Whisper, {len(models_info['llm_models'])} LLM models")
            self.send_json_response(models_info)
        except Exception as e:
            print(f"❌ Models info error: {str(e)}")
            self.send_error_response(f"Failed to get models info: {str(e)}")
    
    def handle_transcription(self):
        """Handle audio transcription with proper file parsing"""
        try:
            # Parse multipart form data using cgi module
            content_type = self.headers.get('Content-Type', '')
            if not content_type.startswith('multipart/form-data'):
                self.send_error_response("Expected multipart/form-data")
                return
            
            # Parse the form data
            form_data = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={
                    'REQUEST_METHOD': 'POST',
                    'CONTENT_TYPE': content_type,
                    'CONTENT_LENGTH': self.headers.get('Content-Length', '0')
                }
            )
            # print(f"📬 Raw form_data: {form_data}")
            # print(f"📬 form_data.keys(): {list(form_data.keys()) if hasattr(form_data, 'keys') else 'No keys method'}")

            # for key in form_data.keys():
            #     field = form_data[key]
            #     print(f"  → Field: {key}")
            #     print(f"    Type: {type(field)}")
            #     print(f"    Has value: {hasattr(field, 'value')}")
            #     if hasattr(field, 'value'):
            #         print(f"    Value: {field.value}")
            #     if hasattr(field, 'filename'):
            #         print(f"    Filename: {field.filename}")
            
            # # 🔍 Debug: Log all form data keys
            # print(f"📬 Form data keys: {list(form_data.keys())}")

            # Extract audio file
            if 'audio' not in form_data:
                self.send_error_response("No audio file provided")
                return
            
            audio_field = form_data['audio']
            if not audio_field.file:
                self.send_error_response("Invalid audio file")
                return
            
            # Extract model parameter
            model_key = 'tiny'  # default
            if 'model' in form_data:
                model_key = form_data['model'].value
            
            print(f"🎤 Transcription request: model={model_key}, filename={getattr(audio_field, 'filename', 'unknown')}")
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                # Read and write audio data
                audio_data = audio_field.file.read()
                temp_file.write(audio_data)
                temp_filename = temp_file.name
            
            try:
                print(f"🎤 Processing audio file: {temp_filename} ({len(audio_data)} bytes)")
                
                # Perform transcription
                result = self.app.transcribe_audio(temp_filename, model_key)
                print(f"✅ Transcription completed: {result.get('success', False)}")
                
                self.send_json_response(result)
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
                    
        except Exception as e:
            print(f"❌ Transcription error: {str(e)}")
            self.send_error_response(f"Transcription failed: {str(e)}")
    
    def handle_llm_processing(self):
        """Handle LLM processing requests"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(post_data)
            
            transcript = data.get('transcript', '')
            processing_type = data.get('processing_type', 'summary')
            llm_model = data.get('llm_model')
            
            print(f"🤖 LLM processing request: type={processing_type}, model={llm_model}")
            
            if not transcript.strip():
                self.send_error_response("No transcript provided")
                return
            
            result = self.app.process_with_llm(transcript, processing_type, llm_model)
            print(f"✅ LLM processing completed: {result.get('success', False)}")
            
            self.send_json_response(result)
            
        except Exception as e:
            print(f"❌ LLM processing error: {str(e)}")
            self.send_error_response(f"LLM processing failed: {str(e)}")

    def handle_complete_workflow(self):
        """Handle complete workflow requests"""
        try:
            # Parse multipart form data
            content_type = self.headers.get('Content-Type', '')
            if not content_type.startswith('multipart/form-data'):
                self.send_error_response("Expected multipart/form-data")
                return
            
            form_data = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={
                    'REQUEST_METHOD': 'POST',
                    'CONTENT_TYPE': content_type,
                    'CONTENT_LENGTH': self.headers.get('Content-Length', '0')
                }
            )
            # print(f"📬 Raw form_data: {form_data}")
            # print(f"📬 form_data.keys(): {list(form_data.keys()) if hasattr(form_data, 'keys') else 'No keys method'}")

            # for key in form_data.keys():
            #     field = form_data[key]
            #     print(f"  → Field: {key}")
            #     print(f"    Type: {type(field)}")
            #     print(f"    Has value: {hasattr(field, 'value')}")
            #     if hasattr(field, 'value'):
            #         print(f"    Value: {field.value}")
            #     if hasattr(field, 'filename'):
            #         print(f"    Filename: {field.filename}")

            # # 🔍 Debug: Log all form data keys
            # print(f"📬 Form data keys: {list(form_data.keys())}")
            
            # Extract parameters
            if 'audio' not in form_data:
                self.send_error_response("No audio file provided")
                return
            
            audio_field = form_data['audio']
            if not audio_field.file:
                self.send_error_response("Invalid audio file")
                return

            def safe_get_field(form, key, default=None):
                """Safely extract value from cgi.FieldStorage"""
                if key not in form:
                    return default
                field = form[key]
                if hasattr(field, 'value'):
                    return field.value
                elif isinstance(field, str):
                    return field
                return default

            # Extract parameters safely
            whisper_model = safe_get_field(form_data, 'whisper_model', 'tiny')
            llm_model = safe_get_field(form_data, 'llm_model')
            processing_types_str = safe_get_field(form_data, 'processing_types', 'summary,key_points,action_items')

            # Clean and validate processing_types
            if processing_types_str:
                processing_types = [pt.strip() for pt in processing_types_str.split(',') if pt.strip()]
            else:
                processing_types = ['summary']

            # # 🔍 Debug: Log actual values
            # print(f"⚡ Complete workflow request: whisper={whisper_model}, llm={llm_model}, types={processing_types}")
            # print(f"  → whisper_model type: {type(whisper_model)}")
            # print(f"  → llm_model type: {type(llm_model)}")
            # print(f"  → processing_types: {processing_types}")
            for i, pt in enumerate(processing_types):
                print(f"    type[{i}]: {pt} ({type(pt)})")
            
            # processing_types = processing_types_str.split(',') if processing_types_str else ['summary']
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                audio_data = audio_field.file.read()
                temp_file.write(audio_data)
                temp_filename = temp_file.name
            
            try:
                print(f"⚡ Processing complete workflow: {temp_filename} ({len(audio_data)} bytes)")
                
                # Perform complete workflow
                result = self.app.process_complete_workflow(
                    temp_filename, 
                    whisper_model, 
                    llm_model, 
                    processing_types
                )
                print(f"✅ Complete workflow completed: {result.get('success', False)}")
                
                self.send_json_response(result)
                
            finally:
                # Clean up
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
                    
        except Exception as e:
            print(f"❌ Complete workflow internal error: {str(e)}")
            print(f"    Exception type: {type(e).__name__}")
            import traceback
            traceback.print_exc()  # ← This shows the full stack trace
            self.send_error_response(f"Complete workflow failed: {str(e)}")
    
    def send_json_response(self, data):
        """Send JSON response with proper headers"""
        json_data = json.dumps(data, indent=2).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(json_data))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(json_data)
    
    def send_error_response(self, error_message):
        """Send error response"""
        error_data = {
            'success': False,
            'error': error_message,
            'timestamp': datetime.now().isoformat()
        }
        print(f"❌ Sending error response: {error_message}")
        self.send_json_response(error_data)
    
    def log_message(self, format, *args):
        """Override to reduce log noise"""
        if not any(x in format % args for x in ['.css', '.js', 'favicon.ico']):
            super().log_message(format, *args)


def run_phase4_working_server(host="localhost", port=8080):
    """Run the working Phase 4 server"""
    
    print(f"\n🚀 AI Meeting Assistant - Phase 4 (Working Version)")
    print(f"🌐 Server: http://{host}:{port}")
    print(f"📁 Serving from: {os.path.join(os.path.dirname(__file__), 'web')}")
    print(f"💪 Features: Reliable file uploads + LLM processing")
    
    # Verify web directory exists
    web_dir = os.path.join(os.path.dirname(__file__), 'web')
    if not os.path.exists(web_dir):
        print(f"❌ Error: Web directory not found: {web_dir}")
        return
    
    required_files = ['index.html', 'style.css', 'app.js']
    missing_files = [f for f in required_files if not os.path.exists(os.path.join(web_dir, f))]
    if missing_files:
        print(f"❌ Error: Missing web files: {missing_files}")
        return
    
    # Test system status
    try:
        app = get_app()
        status = app.get_system_status()
        
        print(f"\n=== System Status ===")
        print(f"🎤 Whisper: {len(status['whisper']['available_models'])} models available")
        print(f"🤖 LLM: {'✅ Connected' if status['llm']['connected'] else '❌ Disconnected'}")
        
        if status['llm']['connected']:
            print(f"   Available LLM models: {status['llm']['available_models']}")
            print(f"   Default model: {status['current_llm_model']}")
        else:
            print(f"   ⚠️ LLM processing unavailable - Transcription only mode")
            print(f"   💡 Start Ollama server to enable LLM features")
        
        print(f"\n✅ All components loaded successfully!")
        
    except Exception as e:
        print(f"⚠️ Warning: Could not initialize app: {e}")
    
    print(f"\n🎯 Clean, reliable Phase 4 server ready!")
    print(f"📱 Visit http://{host}:{port} to start")
    print(f"🔄 Press Ctrl+C to stop the server\n")
    
    # Start server
    try:
        server = HTTPServer((host, port), Phase4WorkingHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n👋 Shutting down server...")
        server.server_close()
    except Exception as e:
        print(f"❌ Server error: {e}")


if __name__ == "__main__":
    run_phase4_working_server()
