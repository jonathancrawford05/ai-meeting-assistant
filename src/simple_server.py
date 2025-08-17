#!/usr/bin/env python3
"""
Ultra-Simple Web Interface using basic HTTP server
No Gradio dependencies - just works!
"""
import os
import time
import json
import html
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
import cgi
from pathlib import Path

# Import our working Whisper functionality
import sys
sys.path.append(str(Path(__file__).parent))

from transformers import pipeline

# Global pipeline
_pipeline = None

def get_pipeline():
    """Get or create the transcription pipeline"""
    global _pipeline
    if _pipeline is None:
        print("Loading Whisper model...")
        _pipeline = pipeline(
            "automatic-speech-recognition",
            model="openai/whisper-tiny.en",
            chunk_length_s=30,
        )
        print("Model loaded successfully")
    return _pipeline

def transcribe_file(file_path):
    """Transcribe an audio file"""
    try:
        pipe = get_pipeline()
        start_time = time.time()
        result = pipe(file_path, batch_size=8)["text"]
        end_time = time.time()
        processing_time = end_time - start_time
        
        return {
            "success": True,
            "text": result.strip(),
            "time": f"{processing_time:.1f}s"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

class SimpleTranscriptionHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler for transcription requests"""
    
    def do_GET(self):
        """Serve the main HTML page"""
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>🎤 AI Meeting Assistant</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .container { background: #f5f5f5; padding: 20px; border-radius: 10px; margin: 20px 0; }
        .result { background: white; padding: 15px; border-radius: 5px; margin: 10px 0; min-height: 100px; }
        .status { padding: 10px; border-radius: 5px; margin: 10px 0; }
        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .loading { background: #fff3cd; color: #856404; border: 1px solid #ffeeba; }
        button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background: #0056b3; }
        button:disabled { background: #6c757d; cursor: not-allowed; }
        input[type="file"] { margin: 10px 0; padding: 10px; border: 2px dashed #ddd; border-radius: 5px; width: 100%; }
    </style>
</head>
<body>
    <h1>🎤 AI Meeting Assistant</h1>
    <p>Upload an audio file to get a text transcription using Whisper AI</p>
    
    <div class="container">
        <form id="transcriptionForm" enctype="multipart/form-data">
            <input type="file" id="audioFile" name="audio" accept="audio/*" required>
            <br>
            <button type="submit" id="submitBtn">🚀 Transcribe Audio</button>
        </form>
    </div>
    
    <div id="status"></div>
    <div id="result" class="result" style="display: none;">
        <h3>📝 Transcription Result:</h3>
        <div id="transcriptionText"></div>
    </div>

    <script>
        document.getElementById('transcriptionForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const fileInput = document.getElementById('audioFile');
            const submitBtn = document.getElementById('submitBtn');
            const statusDiv = document.getElementById('status');
            const resultDiv = document.getElementById('result');
            const transcriptionText = document.getElementById('transcriptionText');
            
            if (!fileInput.files[0]) {
                statusDiv.innerHTML = '<div class="error">Please select an audio file</div>';
                return;
            }
            
            // Show loading state
            submitBtn.disabled = true;
            submitBtn.textContent = '⏳ Processing...';
            statusDiv.innerHTML = '<div class="loading">🔄 Transcribing audio... This may take a few moments</div>';
            resultDiv.style.display = 'none';
            
            // Prepare form data
            const formData = new FormData();
            formData.append('audio', fileInput.files[0]);
            
            try {
                const response = await fetch('/transcribe', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.success) {
                    statusDiv.innerHTML = `<div class="success">✅ Transcription completed in ${result.time}</div>`;
                    transcriptionText.textContent = result.text;
                    resultDiv.style.display = 'block';
                } else {
                    statusDiv.innerHTML = `<div class="error">❌ Error: ${result.error}</div>`;
                }
                
            } catch (error) {
                statusDiv.innerHTML = `<div class="error">❌ Connection error: ${error.message}</div>`;
            }
            
            // Reset button
            submitBtn.disabled = false;
            submitBtn.textContent = '🚀 Transcribe Audio';
        });
    </script>
</body>
</html>
            """
            
            self.wfile.write(html_content.encode())
        else:
            self.send_error(404)
    
    def do_POST(self):
        """Handle transcription requests"""
        if self.path == "/transcribe":
            try:
                # Parse multipart form data
                content_type = self.headers['content-type']
                if not content_type.startswith('multipart/form-data'):
                    self.send_error(400, "Bad Request")
                    return
                
                # Parse the form data
                form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={'REQUEST_METHOD': 'POST'}
                )
                
                # Get the uploaded file
                audio_field = form['audio']
                if not audio_field.filename:
                    self.send_error(400, "No file uploaded")
                    return
                
                # Save the uploaded file temporarily
                temp_path = f"/tmp/uploaded_audio_{int(time.time())}.wav"
                with open(temp_path, 'wb') as f:
                    f.write(audio_field.file.read())
                
                # Transcribe the file
                result = transcribe_file(temp_path)
                
                # Clean up temporary file
                try:
                    os.remove(temp_path)
                except:
                    pass
                
                # Send JSON response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json') 
                self.end_headers()
                error_response = {"success": False, "error": str(e)}
                self.wfile.write(json.dumps(error_response).encode())
        else:
            self.send_error(404)

def main():
    """Run the simple web server"""
    port = 8080
    
    print("🚀 Starting AI Meeting Assistant Simple Server...")
    print(f"🌐 Server will run at: http://localhost:{port}")
    print("💡 This bypasses all Gradio compatibility issues!")
    print("\nPress Ctrl+C to stop the server")
    
    try:
        server = HTTPServer(('localhost', port), SimpleTranscriptionHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")

if __name__ == "__main__":
    main()
