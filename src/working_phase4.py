"""
Phase 4 Server - Working Version
Built using the proven working patterns from incremental test
"""

import os
import json
import time
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

from llm_enhanced_app import get_app
import config


class WorkingPhase4Handler(SimpleHTTPRequestHandler):
    """Phase 4 handler using proven working JavaScript patterns"""
    
    def __init__(self, *args, **kwargs):
        self.app = get_app()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/' or path == '/index.html':
            self.serve_working_page()
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
    
    def serve_working_page(self):
        """Serve working Phase 4 interface"""
        html = '''<!DOCTYPE html>
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
        .status-bar.warning { background: #fff3cd; border-left-color: #ffc107; }
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
            <h1>AI Meeting Assistant</h1>
            <p>Phase 4: Speech-to-Text + LLM Processing</p>
        </div>
        
        <div id="status" class="status-bar">
            <strong>Status:</strong> <span id="status-text">Loading...</span>
        </div>
        
        <div class="card">
            <div class="tabs">
                <div class="tab active" onclick="showTab('transcribe')">Transcribe</div>
                <div class="tab" onclick="showTab('llm')">LLM Process</div>
                <div class="tab" onclick="showTab('workflow')">Complete</div>
            </div>
            
            <!-- Transcribe Tab -->
            <div id="tab-transcribe" class="tab-content active">
                <h3>Audio Transcription</h3>
                <div id="whisper-models" class="model-grid">
                    <div>Loading models...</div>
                </div>
                <div class="upload-area" onclick="document.getElementById('audio-file').click()">
                    Click to upload audio file<br>
                    <small>Supported: WAV, MP3, M4A, FLAC, OGG</small>
                </div>
                <input type="file" id="audio-file" accept="audio/*">
                <button class="btn" onclick="startTranscription()" id="transcribe-btn" disabled>Start Transcription</button>
                <div class="progress" id="transcribe-progress" style="display: none;">
                    <div class="progress-bar" id="transcribe-bar"></div>
                </div>
                <div id="transcribe-result"></div>
            </div>
            
            <!-- LLM Tab -->
            <div id="tab-llm" class="tab-content">
                <h3>LLM Text Processing</h3>
                <div id="llm-models" class="model-grid">
                    <div>Loading models...</div>
                </div>
                <div id="processing-types" class="model-grid">
                    <div>Loading types...</div>
                </div>
                <textarea id="transcript-input" placeholder="Paste meeting transcript here..."></textarea>
                <button class="btn" onclick="startLLMProcessing()" id="llm-btn" disabled>Process with LLM</button>
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
                    Upload audio for complete processing<br>
                    <small>Will transcribe and analyze automatically</small>
                </div>
                <input type="file" id="workflow-file" accept="audio/*">
                <button class="btn" onclick="startCompleteWorkflow()" id="workflow-btn" disabled>Start Complete Workflow</button>
                <div class="progress" id="workflow-progress" style="display: none;">
                    <div class="progress-bar" id="workflow-bar"></div>
                </div>
                <div id="workflow-result"></div>
            </div>
        </div>
    </div>
    
    <script>
        // Global state - using simple variables
        var systemStatus = null;
        var modelsInfo = null;
        var selectedWhisperModel = 'tiny';
        var selectedLLMModel = null;
        var selectedProcessingType = 'summary';
        
        console.log('Script loaded');
        
        // Update status using working pattern
        function updateStatus(message, type) {
            console.log('Status update:', message);
            var statusEl = document.getElementById('status');
            var statusTextEl = document.getElementById('status-text');
            
            if (statusTextEl) {
                statusTextEl.textContent = message;
            }
            
            if (statusEl) {
                statusEl.className = 'status-bar';
                if (type === 'error') {
                    statusEl.className += ' error';
                } else if (type === 'warning') {
                    statusEl.className += ' warning';
                }
            }
        }
        
        // Load system data using working pattern
        function loadSystemData() {
            console.log('Loading system data...');
            updateStatus('Loading system information...');
            
            // Load status first
            fetch('/api/status')
                .then(function(response) {
                    console.log('Status response:', response.status);
                    if (!response.ok) {
                        throw new Error('Status API failed: ' + response.status);
                    }
                    return response.json();
                })
                .then(function(data) {
                    console.log('Status data loaded:', data);
                    systemStatus = data;
                    
                    // Then load models
                    return fetch('/api/models');
                })
                .then(function(response) {
                    console.log('Models response:', response.status);
                    if (!response.ok) {
                        throw new Error('Models API failed: ' + response.status);
                    }
                    return response.json();
                })
                .then(function(data) {
                    console.log('Models data loaded:', data);
                    modelsInfo = data;
                    
                    // Update the interface
                    updateStatusDisplay();
                    renderModels();
                    setupEventListeners();
                    updateButtons();
                    
                    console.log('Initialization complete!');
                })
                .catch(function(error) {
                    console.error('Failed to load system data:', error);
                    updateStatus('Failed to load: ' + error.message, 'error');
                });
        }
        
        function updateStatusDisplay() {
            if (!systemStatus) {
                updateStatus('No status data available', 'error');
                return;
            }
            
            var whisperOk = systemStatus.whisper && systemStatus.whisper.available_models && systemStatus.whisper.available_models.length > 0;
            var llmOk = systemStatus.llm && systemStatus.llm.connected;
            
            if (whisperOk && llmOk) {
                updateStatus('All systems ready - Whisper + LLM available');
            } else if (whisperOk) {
                updateStatus('Whisper ready, LLM unavailable - Transcription only', 'warning');
            } else {
                updateStatus('System not ready - Check configuration', 'error');
            }
        }
        
        function renderModels() {
            if (!modelsInfo) {
                console.log('No models info to render');
                return;
            }
            
            console.log('Rendering models...');
            
            // Render Whisper models
            var whisperContainer = document.getElementById('whisper-models');
            if (whisperContainer && modelsInfo.whisper_models) {
                whisperContainer.innerHTML = '';
                
                Object.keys(modelsInfo.whisper_models).forEach(function(key) {
                    var model = modelsInfo.whisper_models[key];
                    var card = document.createElement('div');
                    card.className = 'model-card' + (model.is_current ? ' selected' : '');
                    card.onclick = function() { selectWhisperModel(key); };
                    card.innerHTML = '<strong>' + model.description + '</strong><br><small>' + model.size + ' - ' + model.speed + '</small>';
                    whisperContainer.appendChild(card);
                });
                
                console.log('Whisper models rendered');
            }
            
            // Render LLM models
            var llmContainer = document.getElementById('llm-models');
            if (llmContainer && modelsInfo.llm_models) {
                llmContainer.innerHTML = '';
                
                Object.keys(modelsInfo.llm_models).forEach(function(key) {
                    var model = modelsInfo.llm_models[key];
                    var card = document.createElement('div');
                    card.className = 'model-card' + (model.default ? ' selected' : '');
                    card.onclick = function() { selectLLMModel(key); };
                    card.innerHTML = '<strong>' + model.display_name + '</strong><br><small>' + model.size + ' - ' + model.speed + '</small>';
                    llmContainer.appendChild(card);
                    
                    if (model.default && !selectedLLMModel) {
                        selectedLLMModel = key;
                    }
                });
                
                console.log('LLM models rendered');
            }
            
            // Render processing types
            var typesContainer = document.getElementById('processing-types');
            if (typesContainer && modelsInfo.processing_types) {
                typesContainer.innerHTML = '';
                
                Object.keys(modelsInfo.processing_types).forEach(function(key) {
                    var type = modelsInfo.processing_types[key];
                    var card = document.createElement('div');
                    card.className = 'model-card' + (key === 'summary' ? ' selected' : '');
                    card.onclick = function() { selectProcessingType(key); };
                    card.innerHTML = '<strong>' + type.icon + ' ' + type.name + '</strong><br><small>' + type.description + '</small>';
                    typesContainer.appendChild(card);
                });
                
                console.log('Processing types rendered');
            }
        }
        
        function selectWhisperModel(key) {
            selectedWhisperModel = key;
            console.log('Selected Whisper model:', key);
            
            // Update visual selection
            var cards = document.querySelectorAll('#whisper-models .model-card');
            for (var i = 0; i < cards.length; i++) {
                cards[i].classList.remove('selected');
            }
            event.target.closest('.model-card').classList.add('selected');
        }
        
        function selectLLMModel(key) {
            selectedLLMModel = key;
            console.log('Selected LLM model:', key);
            
            // Update visual selection
            var cards = document.querySelectorAll('#llm-models .model-card');
            for (var i = 0; i < cards.length; i++) {
                cards[i].classList.remove('selected');
            }
            event.target.closest('.model-card').classList.add('selected');
            
            updateButtons();
        }
        
        function selectProcessingType(key) {
            selectedProcessingType = key;
            console.log('Selected processing type:', key);
            
            // Update visual selection
            var cards = document.querySelectorAll('#processing-types .model-card');
            for (var i = 0; i < cards.length; i++) {
                cards[i].classList.remove('selected');
            }
            event.target.closest('.model-card').classList.add('selected');
        }
        
        function showTab(tabName) {
            console.log('Showing tab:', tabName);
            
            // Update tab buttons
            var tabs = document.querySelectorAll('.tab');
            for (var i = 0; i < tabs.length; i++) {
                tabs[i].classList.remove('active');
            }
            event.target.classList.add('active');
            
            // Update tab content
            var contents = document.querySelectorAll('.tab-content');
            for (var i = 0; i < contents.length; i++) {
                contents[i].classList.remove('active');
            }
            document.getElementById('tab-' + tabName).classList.add('active');
        }
        
        function setupEventListeners() {
            // File input listeners
            var audioFile = document.getElementById('audio-file');
            var workflowFile = document.getElementById('workflow-file');
            var transcriptInput = document.getElementById('transcript-input');
            
            if (audioFile) {
                audioFile.addEventListener('change', updateButtons);
            }
            if (workflowFile) {
                workflowFile.addEventListener('change', updateButtons);
            }
            if (transcriptInput) {
                transcriptInput.addEventListener('input', updateButtons);
            }
        }
        
        function updateButtons() {
            var audioFile = document.getElementById('audio-file');
            var workflowFile = document.getElementById('workflow-file');
            var transcriptInput = document.getElementById('transcript-input');
            
            var hasAudioFile = audioFile && audioFile.files.length > 0;
            var hasWorkflowFile = workflowFile && workflowFile.files.length > 0;
            var hasTranscriptText = transcriptInput && transcriptInput.value.trim();
            var llmConnected = systemStatus && systemStatus.llm && systemStatus.llm.connected;
            
            var transcribeBtn = document.getElementById('transcribe-btn');
            var llmBtn = document.getElementById('llm-btn');
            var workflowBtn = document.getElementById('workflow-btn');
            
            if (transcribeBtn) {
                transcribeBtn.disabled = !hasAudioFile;
            }
            if (llmBtn) {
                llmBtn.disabled = !hasTranscriptText || !selectedLLMModel || !llmConnected;
            }
            if (workflowBtn) {
                workflowBtn.disabled = !hasWorkflowFile || !selectedLLMModel || !llmConnected;
            }
        }
        
        // Processing functions (will implement these next)
        function startTranscription() {
            console.log('Starting transcription...');
            alert('Transcription functionality ready to implement!\\nSelected model: ' + selectedWhisperModel);
        }
        
        function startLLMProcessing() {
            console.log('Starting LLM processing...');
            alert('LLM processing functionality ready to implement!\\nSelected model: ' + selectedLLMModel + '\\nProcessing type: ' + selectedProcessingType);
        }
        
        function startCompleteWorkflow() {
            console.log('Starting complete workflow...');
            alert('Complete workflow functionality ready to implement!\\nWhisper: ' + selectedWhisperModel + '\\nLLM: ' + selectedLLMModel);
        }
        
        // Initialize when page loads
        document.addEventListener('DOMContentLoaded', function() {
            console.log('Page loaded, starting initialization...');
            updateStatus('Page loaded, initializing...');
            
            // Start loading after a short delay
            setTimeout(loadSystemData, 100);
        });
        
        console.log('Script setup complete');
    </script>
</body>
</html>'''
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Content-length', len(html))
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_status(self):
        """Serve system status"""
        try:
            status = self.app.get_system_status()
            self.send_json_response(status)
        except Exception as e:
            self.send_json_response({'error': str(e), 'success': False})
    
    def serve_models_info(self):
        """Serve model information"""
        try:
            models_info = {
                'whisper_models': {
                    key: {**value, 'is_current': key == self.app.current_whisper_model}
                    for key, value in config.WHISPER_MODELS.items()
                },
                'llm_models': config.LLM_MODELS,
                'processing_types': config.PROCESSING_TYPES
            }
            self.send_json_response(models_info)
        except Exception as e:
            self.send_json_response({'error': str(e), 'success': False})
    
    def handle_transcription(self):
        """Handle audio transcription requests - placeholder for now"""
        self.send_json_response({'message': 'Transcription endpoint ready', 'success': True})
    
    def handle_llm_processing(self):
        """Handle LLM processing requests - placeholder for now"""
        self.send_json_response({'message': 'LLM processing endpoint ready', 'success': True})
    
    def handle_complete_workflow(self):
        """Handle complete workflow requests - placeholder for now"""
        self.send_json_response({'message': 'Complete workflow endpoint ready', 'success': True})
    
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


def run_working_phase4_server(host="localhost", port=8080):
    """Run the working Phase 4 server"""
    
    print(f"\n🎉 AI Meeting Assistant - Phase 4 (Working Version)")
    print(f"🌐 Server: http://{host}:{port}")
    print(f"✅ Built using proven working patterns")
    
    # Test system status
    app = get_app()
    status = app.get_system_status()
    
    print(f"\n=== System Status ===")
    print(f"🎤 Whisper: {len(status['whisper']['available_models'])} models available")
    print(f"🤖 LLM: {'✅ Connected' if status['llm']['connected'] else '❌ Disconnected'}")
    
    if status['llm']['connected']:
        print(f"   Available LLM models: {status['llm']['available_models']}")
        print(f"   Default model: {status['current_llm_model']}")
    
    print(f"\n🎯 Working Phase 4 interface ready!")
    print(f"📝 Visit http://{host}:{port} to start")
    
    # Start server
    server = HTTPServer((host, port), WorkingPhase4Handler)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n👋 Shutting down server...")
        server.server_close()


if __name__ == "__main__":
    run_working_phase4_server()
