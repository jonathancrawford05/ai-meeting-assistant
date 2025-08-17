"""
Phase 4 Server - Clean and Modular
Simple HTTP server for AI Meeting Assistant with LLM integration
"""

import os
import json
import time
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

from llm_enhanced_app import get_app
import config


class Phase4Handler(SimpleHTTPRequestHandler):
    """Clean, simple web handler for Phase 4"""
    
    def __init__(self, *args, **kwargs):
        self.app = get_app()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/' or path == '/index.html':
            self.serve_main_page()
        elif path == '/api/status':
            self.serve_status()
        elif path == '/api/models':
            self.serve_models_info()
        else:
            self.send_error(404, "Page not found")
    
    def do_POST(self):
        """Handle POST requests"""
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
            self.send_error_response(f"Request failed: {str(e)}")
    
    def serve_main_page(self):
        """Serve the main application page"""
        html_content = self.get_simple_html()
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Content-length', len(html_content))
        self.end_headers()
        self.wfile.write(html_content.encode())
    
    def serve_status(self):
        """Serve system status"""
        try:
            status = self.app.get_system_status()
            self.send_json_response(status)
        except Exception as e:
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
            self.send_json_response(models_info)
        except Exception as e:
            self.send_error_response(f"Failed to get models info: {str(e)}")
    
    def handle_transcription(self):
        """Handle audio transcription requests"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        # Simple multipart form parsing
        try:
            boundary = self.headers['Content-Type'].split('boundary=')[1].encode()
            parts = post_data.split(b'--' + boundary)
            
            audio_data = None
            model_key = 'tiny'  # default
            
            for part in parts:
                if b'Content-Disposition: form-data; name="audio"' in part:
                    data_start = part.find(b'\\r\\n\\r\\n') + 4
                    audio_data = part[data_start:]
                elif b'Content-Disposition: form-data; name="model"' in part:
                    data_start = part.find(b'\\r\\n\\r\\n') + 4
                    model_key = part[data_start:].decode().strip()
            
            if not audio_data:
                self.send_error_response("No audio file provided")
                return
            
            # Save temporary file
            temp_filename = f"uploaded_audio_{int(time.time())}.wav"
            with open(temp_filename, 'wb') as f:
                f.write(audio_data)
            
            try:
                # Perform transcription
                result = self.app.transcribe_audio(temp_filename, model_key)
                self.send_json_response(result)
            finally:
                # Clean up temporary file
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
                    
        except Exception as e:
            self.send_error_response(f"Transcription parsing failed: {str(e)}")
    
    def handle_llm_processing(self):
        """Handle LLM processing requests"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        data = json.loads(post_data)
        
        transcript = data.get('transcript', '')
        processing_type = data.get('processing_type', 'summary')
        llm_model = data.get('llm_model')
        
        if not transcript.strip():
            self.send_error_response("No transcript provided")
            return
        
        result = self.app.process_with_llm(transcript, processing_type, llm_model)
        self.send_json_response(result)
    
    def handle_complete_workflow(self):
        """Handle complete workflow requests"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        # Parse form data
        try:
            boundary = self.headers['Content-Type'].split('boundary=')[1].encode()
            parts = post_data.split(b'--' + boundary)
            
            audio_data = None
            whisper_model = 'tiny'
            llm_model = None
            processing_types = ['summary', 'key_points', 'action_items']
            
            for part in parts:
                if b'Content-Disposition: form-data; name="audio"' in part:
                    data_start = part.find(b'\\r\\n\\r\\n') + 4
                    audio_data = part[data_start:]
                elif b'Content-Disposition: form-data; name="whisper_model"' in part:
                    data_start = part.find(b'\\r\\n\\r\\n') + 4
                    whisper_model = part[data_start:].decode().strip()
                elif b'Content-Disposition: form-data; name="llm_model"' in part:
                    data_start = part.find(b'\\r\\n\\r\\n') + 4
                    llm_model = part[data_start:].decode().strip()
                elif b'Content-Disposition: form-data; name="processing_types"' in part:
                    data_start = part.find(b'\\r\\n\\r\\n') + 4
                    types_str = part[data_start:].decode().strip()
                    if types_str:
                        processing_types = types_str.split(',')
            
            if not audio_data:
                self.send_error_response("No audio file provided")
                return
            
            # Save temporary file
            temp_filename = f"uploaded_audio_{int(time.time())}.wav"
            with open(temp_filename, 'wb') as f:
                f.write(audio_data)
            
            try:
                # Perform complete workflow
                result = self.app.process_complete_workflow(
                    temp_filename, 
                    whisper_model, 
                    llm_model, 
                    processing_types
                )
                self.send_json_response(result)
            finally:
                # Clean up
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
                    
        except Exception as e:
            self.send_error_response(f"Workflow parsing failed: {str(e)}")
    
    def send_json_response(self, data):
        """Send JSON response"""
        json_data = json.dumps(data, indent=2).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(json_data))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json_data)
    
    def send_error_response(self, error_message):
        """Send error response"""
        error_data = {
            'success': False,
            'error': error_message,
            'timestamp': datetime.now().isoformat()
        }
        self.send_json_response(error_data)
    
    def get_simple_html(self):
        """Generate a clean, simple HTML interface"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Meeting Assistant - Phase 4</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            line-height: 1.6; color: #333; background: #f5f7fa; padding: 20px;
        }
        .container { max-width: 1000px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { color: #2c3e50; margin-bottom: 10px; }
        .card { 
            background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .tabs { display: flex; border-bottom: 2px solid #ecf0f1; margin-bottom: 20px; }
        .tab { 
            padding: 10px 20px; cursor: pointer; border-bottom: 3px solid transparent;
            transition: all 0.3s ease;
        }
        .tab.active { border-bottom-color: #3498db; color: #3498db; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .upload-area {
            border: 2px dashed #bdc3c7; border-radius: 8px; padding: 40px;
            text-align: center; cursor: pointer; transition: all 0.3s ease;
        }
        .upload-area:hover { border-color: #3498db; background-color: #ecf0f1; }
        .btn {
            background: #3498db; color: white; border: none; padding: 10px 20px;
            border-radius: 5px; cursor: pointer; margin: 10px 5px;
        }
        .btn:hover { background: #2980b9; }
        .btn:disabled { background: #95a5a6; cursor: not-allowed; }
        .model-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin: 10px 0; }
        .model-card { 
            border: 2px solid #ecf0f1; border-radius: 5px; padding: 10px; cursor: pointer;
            transition: all 0.3s ease;
        }
        .model-card:hover { border-color: #3498db; }
        .model-card.selected { border-color: #3498db; background-color: #ebf3fd; }
        .status-bar { background: #d5f4e6; border-left: 4px solid #27ae60; padding: 10px; margin-bottom: 20px; }
        .status-bar.error { background: #fdf2f2; border-left-color: #e74c3c; }
        .result { background: #f8f9fa; border-radius: 5px; padding: 15px; margin: 15px 0; }
        .progress { background: #ecf0f1; height: 8px; border-radius: 4px; overflow: hidden; margin: 10px 0; }
        .progress-bar { background: #3498db; height: 100%; transition: width 0.3s ease; width: 0%; }
        textarea { width: 100%; min-height: 120px; padding: 10px; border: 2px solid #ecf0f1; border-radius: 5px; }
        input[type="file"] { display: none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 AI Meeting Assistant</h1>
            <p>Phase 4: Speech-to-Text + LLM Processing</p>
        </div>
        
        <div id="status" class="status-bar">
            <strong>Status:</strong> <span id="status-text">Loading...</span>
        </div>
        
        <div class="card">
            <div class="tabs">
                <div class="tab active" onclick="showTab('transcribe')">🎤 Transcribe</div>
                <div class="tab" onclick="showTab('llm')">🤖 LLM Process</div>
                <div class="tab" onclick="showTab('workflow')">⚡ Complete</div>
            </div>
            
            <!-- Transcribe Tab -->
            <div id="tab-transcribe" class="tab-content active">
                <h3>Audio Transcription</h3>
                <div class="model-grid" id="whisper-models"></div>
                <div class="upload-area" onclick="document.getElementById('audio-file').click()">
                    📁 Click to upload audio file<br>
                    <small>Supported: WAV, MP3, M4A, FLAC, OGG</small>
                </div>
                <input type="file" id="audio-file" accept="audio/*">
                <button class="btn" onclick="transcribe()" id="transcribe-btn" disabled>Start Transcription</button>
                <div class="progress" id="transcribe-progress" style="display: none;">
                    <div class="progress-bar" id="transcribe-bar"></div>
                </div>
                <div id="transcribe-result"></div>
            </div>
            
            <!-- LLM Tab -->
            <div id="tab-llm" class="tab-content">
                <h3>LLM Text Processing</h3>
                <div class="model-grid" id="llm-models"></div>
                <div class="model-grid" id="processing-types"></div>
                <textarea id="transcript-input" placeholder="Paste meeting transcript here..."></textarea>
                <button class="btn" onclick="processLLM()" id="llm-btn" disabled>Process with LLM</button>
                <div class="progress" id="llm-progress" style="display: none;">
                    <div class="progress-bar" id="llm-bar"></div>
                </div>
                <div id="llm-result"></div>
            </div>
            
            <!-- Complete Workflow Tab -->
            <div id="tab-workflow" class="tab-content">
                <h3>Complete Workflow</h3>
                <p>Audio → Transcript → LLM Analysis</p>
                <div class="upload-area" onclick="document.getElementById('workflow-file').click()">
                    📁 Upload audio for complete processing<br>
                    <small>Will transcribe and analyze automatically</small>
                </div>
                <input type="file" id="workflow-file" accept="audio/*">
                <button class="btn" onclick="completeWorkflow()" id="workflow-btn" disabled>Start Complete Workflow</button>
                <div class="progress" id="workflow-progress" style="display: none;">
                    <div class="progress-bar" id="workflow-bar"></div>
                </div>
                <div id="workflow-result"></div>
            </div>
        </div>
    </div>
    
    <script>
        let systemStatus = null;
        let modelsInfo = null;
        let selectedWhisperModel = 'tiny';
        let selectedLLMModel = null;
        let selectedProcessingType = 'summary';
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            loadStatus();
            setupFileInputs();
        });
        
        async function loadStatus() {
            try {
                const response = await fetch('/api/status');
                systemStatus = await response.json();
                
                const modelsResponse = await fetch('/api/models');
                modelsInfo = await modelsResponse.json();
                
                updateStatus();
                renderModels();
            } catch (error) {
                updateStatus(false, 'Failed to load system status');
            }
        }
        
        function updateStatus(success = null, message = null) {
            const statusBar = document.getElementById('status');
            const statusText = document.getElementById('status-text');
            
            if (success === false) {
                statusBar.className = 'status-bar error';
                statusText.textContent = message;
                return;
            }
            
            if (systemStatus) {
                const whisperOk = systemStatus.whisper?.available_models?.length > 0;
                const llmOk = systemStatus.llm?.connected;
                
                if (whisperOk && llmOk) {
                    statusBar.className = 'status-bar';
                    statusText.textContent = 'All systems ready - Whisper + LLM available';
                } else if (whisperOk) {
                    statusBar.className = 'status-bar';
                    statusText.textContent = 'Whisper ready, LLM unavailable - Transcription only';
                } else {
                    statusBar.className = 'status-bar error';
                    statusText.textContent = 'System not ready';
                }
            }
        }
        
        function renderModels() {
            if (!modelsInfo) return;
            
            // Render Whisper models
            const whisperContainer = document.getElementById('whisper-models');
            whisperContainer.innerHTML = '';
            Object.entries(modelsInfo.whisper_models).forEach(([key, model]) => {
                const card = document.createElement('div');
                card.className = `model-card ${model.is_current ? 'selected' : ''}`;
                card.onclick = () => selectWhisperModel(key);
                card.innerHTML = `<strong>${model.description}</strong><br><small>${model.size} - ${model.speed}</small>`;
                whisperContainer.appendChild(card);
            });
            
            // Render LLM models
            const llmContainer = document.getElementById('llm-models');
            llmContainer.innerHTML = '';
            Object.entries(modelsInfo.llm_models).forEach(([key, model]) => {
                const card = document.createElement('div');
                card.className = `model-card ${model.default ? 'selected' : ''}`;
                card.onclick = () => selectLLMModel(key);
                card.innerHTML = `<strong>${model.display_name}</strong><br><small>${model.size} - ${model.speed}</small>`;
                llmContainer.appendChild(card);
                if (model.default) selectedLLMModel = key;
            });
            
            // Render processing types
            const typesContainer = document.getElementById('processing-types');
            typesContainer.innerHTML = '';
            Object.entries(modelsInfo.processing_types).forEach(([key, type]) => {
                const card = document.createElement('div');
                card.className = `model-card ${key === 'summary' ? 'selected' : ''}`;
                card.onclick = () => selectProcessingType(key);
                card.innerHTML = `<strong>${type.icon} ${type.name}</strong><br><small>${type.description}</small>`;
                typesContainer.appendChild(card);
            });
        }
        
        function selectWhisperModel(key) {
            selectedWhisperModel = key;
            document.querySelectorAll('#whisper-models .model-card').forEach(card => card.classList.remove('selected'));
            event.target.closest('.model-card').classList.add('selected');
        }
        
        function selectLLMModel(key) {
            selectedLLMModel = key;
            document.querySelectorAll('#llm-models .model-card').forEach(card => card.classList.remove('selected'));
            event.target.closest('.model-card').classList.add('selected');
            updateButtons();
        }
        
        function selectProcessingType(key) {
            selectedProcessingType = key;
            document.querySelectorAll('#processing-types .model-card').forEach(card => card.classList.remove('selected'));
            event.target.closest('.model-card').classList.add('selected');
        }
        
        function showTab(tabName) {
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById(`tab-${tabName}`).classList.add('active');
        }
        
        function setupFileInputs() {
            document.getElementById('audio-file').addEventListener('change', updateButtons);
            document.getElementById('workflow-file').addEventListener('change', updateButtons);
            document.getElementById('transcript-input').addEventListener('input', updateButtons);
        }
        
        function updateButtons() {
            const audioFile = document.getElementById('audio-file').files.length > 0;
            const workflowFile = document.getElementById('workflow-file').files.length > 0;
            const transcriptText = document.getElementById('transcript-input').value.trim();
            const llmConnected = systemStatus?.llm?.connected;
            
            document.getElementById('transcribe-btn').disabled = !audioFile;
            document.getElementById('llm-btn').disabled = !transcriptText || !selectedLLMModel || !llmConnected;
            document.getElementById('workflow-btn').disabled = !workflowFile || !selectedLLMModel || !llmConnected;
        }
        
        async function transcribe() {
            const fileInput = document.getElementById('audio-file');
            const btn = document.getElementById('transcribe-btn');
            const progress = document.getElementById('transcribe-progress');
            const progressBar = document.getElementById('transcribe-bar');
            const result = document.getElementById('transcribe-result');
            
            btn.disabled = true;
            progress.style.display = 'block';
            progressBar.style.width = '30%';
            result.innerHTML = '<p>🎤 Transcribing audio...</p>';
            
            try {
                const formData = new FormData();
                formData.append('audio', fileInput.files[0]);
                formData.append('model', selectedWhisperModel);
                
                progressBar.style.width = '70%';
                
                const response = await fetch('/api/transcribe', { method: 'POST', body: formData });
                const data = await response.json();
                
                progressBar.style.width = '100%';
                setTimeout(() => progress.style.display = 'none', 1000);
                
                if (data.success) {
                    result.innerHTML = `
                        <div class="result">
                            <h4>✅ Transcription Complete</h4>
                            <p><strong>Model:</strong> ${data.model_used} | <strong>Time:</strong> ${data.processing_time.toFixed(2)}s</p>
                            <div style="background: white; padding: 10px; border-radius: 5px; margin: 10px 0; max-height: 200px; overflow-y: auto;">
                                ${data.transcript}
                            </div>
                            <button class="btn" onclick="downloadText('${data.transcript.replace(/'/g, "\\\\'")}')">📥 Download</button>
                        </div>
                    `;
                } else {
                    result.innerHTML = `<div class="result"><h4>❌ Failed</h4><p>${data.error}</p></div>`;
                }
            } catch (error) {
                result.innerHTML = `<div class="result"><h4>❌ Error</h4><p>${error.message}</p></div>`;
            } finally {
                btn.disabled = false;
            }
        }
        
        async function processLLM() {
            const textInput = document.getElementById('transcript-input');
            const btn = document.getElementById('llm-btn');
            const progress = document.getElementById('llm-progress');
            const progressBar = document.getElementById('llm-bar');
            const result = document.getElementById('llm-result');
            
            btn.disabled = true;
            progress.style.display = 'block';
            progressBar.style.width = '30%';
            result.innerHTML = '<p>🤖 Processing with LLM...</p>';
            
            try {
                const data = {
                    transcript: textInput.value,
                    processing_type: selectedProcessingType,
                    llm_model: selectedLLMModel
                };
                
                progressBar.style.width = '70%';
                
                const response = await fetch('/api/process-llm', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                const responseData = await response.json();
                
                progressBar.style.width = '100%';
                setTimeout(() => progress.style.display = 'none', 1000);
                
                if (responseData.success) {
                    result.innerHTML = `
                        <div class="result">
                            <h4>✅ LLM Processing Complete</h4>
                            <p><strong>Model:</strong> ${responseData.model_used} | <strong>Time:</strong> ${responseData.processing_time.toFixed(2)}s</p>
                            <div style="background: white; padding: 10px; border-radius: 5px; margin: 10px 0;">
                                ${responseData.content}
                            </div>
                            <button class="btn" onclick="downloadText('${responseData.content.replace(/'/g, "\\\\'")}')">📥 Download</button>
                        </div>
                    `;
                } else {
                    result.innerHTML = `<div class="result"><h4>❌ Failed</h4><p>${responseData.error}</p></div>`;
                }
            } catch (error) {
                result.innerHTML = `<div class="result"><h4>❌ Error</h4><p>${error.message}</p></div>`;
            } finally {
                btn.disabled = false;
            }
        }
        
        async function completeWorkflow() {
            const fileInput = document.getElementById('workflow-file');
            const btn = document.getElementById('workflow-btn');
            const progress = document.getElementById('workflow-progress');
            const progressBar = document.getElementById('workflow-bar');
            const result = document.getElementById('workflow-result');
            
            btn.disabled = true;
            progress.style.display = 'block';
            progressBar.style.width = '20%';
            result.innerHTML = '<p>⚡ Starting complete workflow...</p>';
            
            try {
                const formData = new FormData();
                formData.append('audio', fileInput.files[0]);
                formData.append('whisper_model', selectedWhisperModel);
                formData.append('llm_model', selectedLLMModel);
                formData.append('processing_types', 'summary,key_points,action_items');
                
                progressBar.style.width = '50%';
                result.innerHTML = '<p>🎤 Transcribing and processing...</p>';
                
                const response = await fetch('/api/complete-workflow', { method: 'POST', body: formData });
                const data = await response.json();
                
                progressBar.style.width = '100%';
                setTimeout(() => progress.style.display = 'none', 1000);
                
                if (data.success) {
                    let html = `<div class="result"><h4>✅ Complete Workflow Finished</h4>`;
                    
                    if (data.transcription && data.transcription.success) {
                        html += `
                            <h5>🎤 Transcription</h5>
                            <div style="background: white; padding: 10px; border-radius: 5px; margin: 10px 0; max-height: 150px; overflow-y: auto;">
                                ${data.transcription.transcript}
                            </div>
                        `;
                    }
                    
                    if (data.llm_processing) {
                        Object.entries(data.llm_processing).forEach(([type, llmResult]) => {
                            if (llmResult.success) {
                                const typeInfo = modelsInfo.processing_types[type];
                                html += `
                                    <h5>${typeInfo.icon} ${typeInfo.name}</h5>
                                    <div style="background: white; padding: 10px; border-radius: 5px; margin: 10px 0;">
                                        ${llmResult.content}
                                    </div>
                                `;
                            }
                        });
                    }
                    
                    html += `<button class="btn" onclick="downloadJSON(${JSON.stringify(data).replace(/"/g, '&quot;')})">📥 Download Report</button></div>`;
                    result.innerHTML = html;
                } else {
                    result.innerHTML = `<div class="result"><h4>❌ Failed</h4><p>${data.error}</p></div>`;
                }
            } catch (error) {
                result.innerHTML = `<div class="result"><h4>❌ Error</h4><p>${error.message}</p></div>`;
            } finally {
                btn.disabled = false;
            }
        }
        
        function downloadText(text) {
            const blob = new Blob([text], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `meeting-result-${new Date().toISOString().split('T')[0]}.txt`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
        
        function downloadJSON(data) {
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `meeting-report-${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
    </script>
</body>
</html>"""


def run_phase4_server(host="localhost", port=8080):
    """Run the clean Phase 4 server"""
    
    print(f"\n🚀 AI Meeting Assistant - Phase 4 (Clean & Modular)")
    print(f"🌐 Server: http://{host}:{port}")
    print(f"📱 Features: Speech-to-Text + LLM Processing")
    
    # Test system status
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
    
    print(f"\n🎯 Clean, maintainable Phase 4 server ready!")
    print(f"📝 Visit http://{host}:{port} to start")
    
    # Start server
    server = HTTPServer((host, port), Phase4Handler)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n👋 Shutting down server...")
        server.server_close()


if __name__ == "__main__":
    run_phase4_server()
