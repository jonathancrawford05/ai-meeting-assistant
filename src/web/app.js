/**
 * AI Meeting Assistant - Phase 4 JavaScript
 * Clean, reliable implementation with proper file handling
 */

// Global state
let systemStatus = null;
let modelsInfo = null;
let selectedWhisperModel = 'tiny';
let selectedLLMModel = null;
let selectedProcessingType = 'summary';

// App initialization
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 AI Meeting Assistant Phase 4 - Starting...');
    initializeApp();
});

/**
 * Initialize the application
 */
async function initializeApp() {
    try {
        updateStatus('Loading system information...', 'info');
        
        // Load system status and models
        await loadSystemData();
        
        // Setup file input listeners
        setupFileListeners();
        
        // Setup other UI listeners
        setupUIListeners();
        
        console.log('✅ App initialization complete');
    } catch (error) {
        console.error('❌ App initialization failed:', error);
        updateStatus('Failed to initialize: ' + error.message, 'error');
    }
}

/**
 * Load system status and model information
 */
async function loadSystemData() {
    try {
        // Load system status
        const statusResponse = await fetch('/api/status');
        if (!statusResponse.ok) {
            throw new Error(`Status API failed: ${statusResponse.status}`);
        }
        systemStatus = await statusResponse.json();
        console.log('📊 System status loaded:', systemStatus);
        
        // Load models information
        const modelsResponse = await fetch('/api/models');
        if (!modelsResponse.ok) {
            throw new Error(`Models API failed: ${modelsResponse.status}`);
        }
        modelsInfo = await modelsResponse.json();
        console.log('🤖 Models info loaded:', modelsInfo);
        
        // Update UI
        updateStatusDisplay();
        renderModels();
        
    } catch (error) {
        console.error('❌ Failed to load system data:', error);
        throw error;
    }
}

/**
 * Update status display
 */
function updateStatus(message, type = 'info') {
    const statusBar = document.getElementById('status');
    const statusText = document.getElementById('status-text');
    
    if (statusText) {
        statusText.textContent = message;
    }
    
    if (statusBar) {
        statusBar.className = 'status-bar';
        if (type === 'error') {
            statusBar.classList.add('error');
        } else if (type === 'warning') {
            statusBar.classList.add('warning');
        }
    }
    
    console.log(`📢 Status: ${message} (${type})`);
}

/**
 * Update status display based on system data
 */
function updateStatusDisplay() {
    if (!systemStatus) {
        updateStatus('No system data available', 'error');
        return;
    }
    
    const whisperOk = systemStatus.whisper && systemStatus.whisper.available_models && systemStatus.whisper.available_models.length > 0;
    const llmOk = systemStatus.llm && systemStatus.llm.connected;
    
    if (whisperOk && llmOk) {
        updateStatus('🎯 All systems ready - Whisper + LLM available');
    } else if (whisperOk) {
        updateStatus('🎤 Whisper ready, LLM unavailable - Transcription only', 'warning');
    } else {
        updateStatus('❌ System not ready - Check configuration', 'error');
    }
}

/**
 * Render model selection grids
 */
function renderModels() {
    if (!modelsInfo) {
        console.log('No models info to render');
        return;
    }
    
    console.log('🎨 Rendering models...');
    
    // Render Whisper models for all tabs
    renderWhisperModels('whisper-models', 'transcribe');
    renderWhisperModels('workflow-whisper-models', 'workflow');
    
    // Render LLM models for all tabs
    renderLLMModels('llm-models', 'llm');
    renderLLMModels('workflow-llm-models', 'workflow');
    
    // Render processing types
    renderProcessingTypes();
}

/**
 * Render Whisper models in a container
 */
function renderWhisperModels(containerId, context) {
    const container = document.getElementById(containerId);
    if (!container || !modelsInfo.whisper_models) return;
    
    container.innerHTML = '';
    
    Object.entries(modelsInfo.whisper_models).forEach(([key, model]) => {
        const card = document.createElement('div');
        card.className = `model-card ${model.is_current ? 'selected' : ''}`;
        card.dataset.key = key;  // 👈 Add data-key for reliable selection
        card.onclick = () => selectWhisperModel(key, context);
        card.innerHTML = `
            <strong>${model.description}</strong>
            <small>${model.size} - ${model.speed}</small>
        `;
        container.appendChild(card);
    });
}

function renderLLMModels(containerId, context) {
    const container = document.getElementById(containerId);
    if (!container || !modelsInfo.llm_models) return;
    
    container.innerHTML = '';
    
    Object.entries(modelsInfo.llm_models).forEach(([key, model]) => {
        const card = document.createElement('div');
        card.className = `model-card ${model.default ? 'selected' : ''}`;
        card.dataset.key = key;  // 👈 Add data-key
        card.onclick = () => selectLLMModel(key, context);
        card.innerHTML = `
            <strong>${model.display_name}</strong>
            <small>${model.size} - ${model.speed}</small>
        `;
        container.appendChild(card);
        if (model.default && !selectedLLMModel) {
            selectedLLMModel = key;
        }
    });

    // Fallback: if no model was selected, pick the first one
    if (!selectedLLMModel && Object.keys(modelsInfo.llm_models).length > 0) {
        selectedLLMModel = Object.keys(modelsInfo.llm_models)[0];
        console.warn('⚠️ No LLM model selected. Using first model:', selectedLLMModel);
    }

    // 🔍 Debug: Confirm selection
    console.log('🤖 renderLLMModels: selectedLLMModel =', selectedLLMModel);
}

function renderProcessingTypes() {
    const container = document.getElementById('processing-types');
    if (!container || !modelsInfo.processing_types) return;
    
    container.innerHTML = '';
    
    Object.entries(modelsInfo.processing_types).forEach(([key, type]) => {
        const card = document.createElement('div');
        card.className = `model-card ${key === 'summary' ? 'selected' : ''}`;
        card.dataset.key = key;  // 👈 Add data-key
        card.onclick = () => selectProcessingType(key);
        card.innerHTML = `
            <strong>${type.icon} ${type.name}</strong>
            <small>${type.description}</small>
        `;
        container.appendChild(card);
    });
}

/**
 * Select Whisper model
 */
function selectWhisperModel(key, context) {
    selectedWhisperModel = key;
    console.log(`🎤 Selected Whisper model: ${key} (context: ${context})`);
    
    // Update all Whisper model displays
    updateModelSelection('whisper-models', key);
    updateModelSelection('workflow-whisper-models', key);
    
    updateButtonStates();
}

/**
 * Select LLM model
 */
function selectLLMModel(key, context) {
    selectedLLMModel = key;
    console.log(`🤖 Selected LLM model: ${key} (context: ${context})`);
    
    // Update all LLM model displays
    updateModelSelection('llm-models', key);
    updateModelSelection('workflow-llm-models', key);
    
    updateButtonStates();
}

/**
 * Select processing type
 */
function selectProcessingType(key) {
    selectedProcessingType = key;
    console.log(`⚙️ Selected processing type: ${key}`);
    
    updateModelSelection('processing-types', key);
    updateButtonStates();
}

/**
 * Update model selection display
 */
function updateModelSelection(containerId, selectedKey) {
    const container = document.getElementById(containerId);
    if (!container) return;

    // Remove 'selected' from all cards
    const cards = container.querySelectorAll('.model-card');
    cards.forEach(card => {
        card.classList.remove('selected');
    });

    // Add 'selected' to the correct card using data-key
    const selectedCard = container.querySelector(`.model-card[data-key="${selectedKey}"]`);
    if (selectedCard) {
        selectedCard.classList.add('selected');
    }
}

/**
 * Setup file input listeners
 */
function setupFileListeners() {
    console.log('📁 Setting up file listeners...');
    
    // Transcribe file input
    const transcribeFile = document.getElementById('transcribe-file');
    if (transcribeFile) {
        transcribeFile.addEventListener('change', function() {
            handleFileSelection(this, 'transcribe-file-info', 'transcribe-upload', 'transcribe-btn');
        });
    }
    
    // Workflow file input
    const workflowFile = document.getElementById('workflow-file');
    if (workflowFile) {
        workflowFile.addEventListener('change', function() {
            handleFileSelection(this, 'workflow-file-info', 'workflow-upload', 'workflow-btn');
        });
    }
}

/**
 * Setup other UI listeners
 */
function setupUIListeners() {
    console.log('🎛️ Setting up UI listeners...');
    
    // Transcript input
    const transcriptInput = document.getElementById('transcript-input');
    if (transcriptInput) {
        transcriptInput.addEventListener('input', updateButtonStates);
    }
    
    // Processing type checkboxes (for workflow)
    const checkboxes = document.querySelectorAll('.checkbox-item input[type=\"checkbox\"]');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateButtonStates);
    });
}

/**
 * Handle file selection
 */
function handleFileSelection(fileInput, infoId, uploadAreaId, buttonId) {
    const fileInfo = document.getElementById(infoId);
    const uploadArea = document.getElementById(uploadAreaId);
    const button = document.getElementById(buttonId);
    
    if (!fileInput.files || fileInput.files.length === 0) {
        // No file selected
        if (fileInfo) {
            fileInfo.style.display = 'none';
        }
        if (uploadArea) {
            uploadArea.classList.remove('has-file');
        }
        console.log('📁 No file selected');
    } else {
        // File selected
        const file = fileInput.files[0];
        console.log(`📁 File selected: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`);
        
        if (fileInfo) {
            fileInfo.innerHTML = `
                <strong>📄 Selected:</strong> ${file.name}<br>
                <strong>📊 Size:</strong> ${(file.size / 1024 / 1024).toFixed(2)} MB<br>
                <strong>🎵 Type:</strong> ${file.type || 'Unknown'}
            `;
            fileInfo.style.display = 'block';
        }
        
        if (uploadArea) {
            uploadArea.classList.add('has-file');
        }
    }
    
    updateButtonStates();
}

/**
 * Update button states based on current selections
 */
function updateButtonStates() {
    // Transcribe button
    const transcribeFile = document.getElementById('transcribe-file');
    const transcribeBtn = document.getElementById('transcribe-btn');
    if (transcribeBtn) {
        transcribeBtn.disabled = !transcribeFile || !transcribeFile.files || transcribeFile.files.length === 0;
    }
    
    // LLM button
    const transcriptInput = document.getElementById('transcript-input');
    const llmBtn = document.getElementById('llm-btn');
    if (llmBtn) {
        const hasTranscript = transcriptInput && transcriptInput.value.trim().length > 0;
        const hasLLMModel = selectedLLMModel && systemStatus && systemStatus.llm && systemStatus.llm.connected;
        llmBtn.disabled = !hasTranscript || !hasLLMModel;
    }
    
    // Workflow button
    const workflowFile = document.getElementById('workflow-file');
    const workflowBtn = document.getElementById('workflow-btn');
    if (workflowBtn) {
        const hasFile = workflowFile && workflowFile.files && workflowFile.files.length > 0;
        const hasLLMModel = selectedLLMModel && systemStatus && systemStatus.llm && systemStatus.llm.connected;
        workflowBtn.disabled = !hasFile || !hasLLMModel;
    }
}

/**
 * Show a specific tab
 */
function showTab(tabName) {
    console.log(`🔄 Switching to tab: ${tabName}`);
    
    // Update tab buttons
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => tab.classList.remove('active'));
    event.target.classList.add('active');
    
    // Update tab content
    const contents = document.querySelectorAll('.tab-content');
    contents.forEach(content => content.classList.remove('active'));
    const targetContent = document.getElementById(`tab-${tabName}`);
    if (targetContent) {
        targetContent.classList.add('active');
    }
}

/**
 * Show progress
 */
function showProgress(sectionId, progressId, textId, text, percentage = 0) {
    const section = document.getElementById(sectionId);
    const progress = document.getElementById(progressId);
    const progressText = document.getElementById(textId);
    
    if (section) section.style.display = 'block';
    if (progress) progress.style.width = percentage + '%';
    if (progressText) progressText.textContent = text;
}

/**
 * Hide progress
 */
function hideProgress(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        setTimeout(() => {
            section.style.display = 'none';
        }, 1000);
    }
}

/**
 * Display result
 */
function displayResult(containerId, result, isSuccess = true) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const resultClass = isSuccess ? 'success' : 'error';
    const icon = isSuccess ? '✅' : '❌';
    
    let html = `<div class="result ${resultClass}">`;
    
    if (isSuccess && result.success) {
        html += `<h4>${icon} ${result.type || 'Operation'} Complete</h4>`;
        
        if (result.model_used || result.processing_time) {
            html += '<div class="result-meta">';
            if (result.model_used) html += `<strong>Model:</strong> ${result.model_used} `;
            if (result.processing_time) html += `<strong>Time:</strong> ${result.processing_time.toFixed(2)}s`;
            html += '</div>';
        }
        
        if (result.transcript) {
            html += `
                <div class="result-content">
                    ${result.transcript.replace(/\\n/g, '<br>')}
                </div>
            `;
        }
        
        if (result.content) {
            html += `
                <div class="result-content">
                    ${result.content.replace(/\\n/g, '<br>')}
                </div>
            `;
        }
        
        // Add download buttons
        if (result.transcript) {
            html += `<button class="btn" onclick="downloadText('${encodeURIComponent(result.transcript)}', 'transcript')">📥 Download Transcript</button>`;
        }
        if (result.content) {
            html += `<button class="btn" onclick="downloadText('${encodeURIComponent(result.content)}', 'analysis')">📥 Download Analysis</button>`;
        }
        
    } else {
        html += `<h4>${icon} Operation Failed</h4>`;
        html += `<p>${result.error || 'Unknown error occurred'}</p>`;
    }
    
    html += '</div>';
    container.innerHTML = html;
    container.classList.add('slide-up');
}

/**
 * Display workflow results
 */
function displayWorkflowResult(result) {
    const container = document.getElementById('workflow-result');
    if (!container) return;
    
    if (!result.success) {
        displayResult('workflow-result', result, false);
        return;
    }
    
    let html = '<div class="result success"><h4>⚡ Complete Workflow Finished</h4>';
    
    // Show transcription
    if (result.transcription && result.transcription.success) {
        html += `
            <h5>🎤 Transcription</h5>
            <div class="result-content">
                ${result.transcription.transcript.replace(/\\n/g, '<br>')}
            </div>
        `;
    }
    
    // Show LLM processing results
    if (result.llm_processing) {
        Object.entries(result.llm_processing).forEach(([type, llmResult]) => {
            if (llmResult.success && modelsInfo.processing_types[type]) {
                const typeInfo = modelsInfo.processing_types[type];
                html += `
                    <h5>${typeInfo.icon} ${typeInfo.name}</h5>
                    <div class="result-content">
                        ${llmResult.content.replace(/\\n/g, '<br>')}
                    </div>
                `;
            }
        });
    }
    
    // Add download button for complete report
    html += `<button class="btn" onclick="downloadJSON(${JSON.stringify(result).replace(/"/g, '&quot;')})">📥 Download Complete Report</button>`;
    html += '</div>';
    
    container.innerHTML = html;
    container.classList.add('slide-up');
}

/**
 * Transcribe audio
 */
async function transcribeAudio() {
    const fileInput = document.getElementById('transcribe-file');
    const btn = document.getElementById('transcribe-btn');
    
    if (!fileInput.files || fileInput.files.length === 0) {
        alert('Please select an audio file first');
        return;
    }
    
    const file = fileInput.files[0];
    console.log(`🎤 Starting transcription: ${file.name}`);
    
    btn.disabled = true;
    showProgress('transcribe-progress-section', 'transcribe-progress', 'transcribe-progress-text', 'Uploading and transcribing...', 30);
    
    try {
        // Create form data
        const formData = new FormData();
        formData.append('audio', file);
        formData.append('model', selectedWhisperModel);
        
        showProgress('transcribe-progress-section', 'transcribe-progress', 'transcribe-progress-text', 'Processing audio...', 70);
        
        // Send request
        const response = await fetch('/api/transcribe', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        
        const result = await response.json();
        
        showProgress('transcribe-progress-section', 'transcribe-progress', 'transcribe-progress-text', 'Complete!', 100);
        hideProgress('transcribe-progress-section');
        
        console.log('🎤 Transcription result:', result);
        displayResult('transcribe-result', { ...result, type: 'Transcription' });
        
    } catch (error) {
        console.error('❌ Transcription failed:', error);
        hideProgress('transcribe-progress-section');
        displayResult('transcribe-result', { error: error.message }, false);
    } finally {
        btn.disabled = false;
    }
}

/**
 * Process text with LLM
 */
async function processLLM() {
    const transcriptInput = document.getElementById('transcript-input');
    const btn = document.getElementById('llm-btn');
    
    if (!transcriptInput.value.trim()) {
        alert('Please enter a transcript first');
        return;
    }
    
    console.log(`🤖 Starting LLM processing: ${selectedProcessingType}`);
    
    btn.disabled = true;
    showProgress('llm-progress-section', 'llm-progress', 'llm-progress-text', 'Processing with AI...', 30);
    
    try {
        const data = {
            transcript: transcriptInput.value,
            processing_type: selectedProcessingType,
            llm_model: selectedLLMModel
        };
        
        showProgress('llm-progress-section', 'llm-progress', 'llm-progress-text', 'Analyzing content...', 70);
        
        const response = await fetch('/api/process-llm', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        
        const result = await response.json();
        
        showProgress('llm-progress-section', 'llm-progress', 'llm-progress-text', 'Complete!', 100);
        hideProgress('llm-progress-section');
        
        console.log('🤖 LLM processing result:', result);
        displayResult('llm-result', { ...result, type: 'LLM Processing' });
        
    } catch (error) {
        console.error('❌ LLM processing failed:', error);
        hideProgress('llm-progress-section');
        displayResult('llm-result', { error: error.message }, false);
    } finally {
        btn.disabled = false;
    }
}

/**
 * Complete workflow
 */
async function completeWorkflow() {
    const fileInput = document.getElementById('workflow-file');
    const btn = document.getElementById('workflow-btn');
    
    if (!fileInput.files || fileInput.files.length === 0) {
        alert('Please select an audio file first');
        return;
    }
    
    // Get selected processing types
    const checkboxes = document.querySelectorAll('.checkbox-item input[type=\"checkbox\"]:checked');
    const processingTypes = Array.from(checkboxes).map(cb => cb.value);
    
    if (processingTypes.length === 0) {
        alert('Please select at least one analysis type');
        return;
    }
    
    const file = fileInput.files[0];
    console.log(`⚡ Starting complete workflow: ${file.name}`);
    
    btn.disabled = true;
    showProgress('workflow-progress-section', 'workflow-progress', 'workflow-progress-text', 'Starting workflow...', 10);
    
    try {
        // Create form data
        const formData = new FormData();
        formData.append('audio', file);
        formData.append('whisper_model', selectedWhisperModel);
        formData.append('llm_model', selectedLLMModel);
        formData.append('processing_types', processingTypes.join(','));

        // 🔍 Debug: Log all FormData entries
        console.log('📬 Preparing complete workflow request with FormData:');
        for (let [key, value] of formData.entries()) {
            console.log(`  - ${key}:`, value);
        }
        showProgress('workflow-progress-section', 'workflow-progress', 'workflow-progress-text', 'Transcribing audio...', 30);
        
        // Send request
        const response = await fetch('/api/complete-workflow', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        
        showProgress('workflow-progress-section', 'workflow-progress', 'workflow-progress-text', 'Processing with AI...', 70);
        
        const result = await response.json();
        
        showProgress('workflow-progress-section', 'workflow-progress', 'workflow-progress-text', 'Complete!', 100);
        hideProgress('workflow-progress-section');
        
        console.log('⚡ Complete workflow result:', result);
        displayWorkflowResult(result);
        
    } catch (error) {
        console.error('❌ Complete workflow failed:', error);
        hideProgress('workflow-progress-section');
        displayResult('workflow-result', { error: error.message }, false);
    } finally {
        btn.disabled = false;
    }
}

/**
 * Download text content
 */
function downloadText(encodedContent, type = 'content') {
    try {
        const content = decodeURIComponent(encodedContent);
        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `meeting-${type}-${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        console.log(`📥 Downloaded: ${type}`);
    } catch (error) {
        console.error('❌ Download failed:', error);
        alert('Download failed');
    }
}

/**
 * Download JSON content
 */
function downloadJSON(data) {
    try {
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `meeting-report-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        console.log('📥 Downloaded: complete report');
    } catch (error) {
        console.error('❌ Download failed:', error);
        alert('Download failed');
    }
}

// Export functions for global access
window.showTab = showTab;
window.transcribeAudio = transcribeAudio;
window.processLLM = processLLM;
window.completeWorkflow = completeWorkflow;
window.downloadText = downloadText;
window.downloadJSON = downloadJSON;

console.log('📱 Phase 4 JavaScript loaded and ready!');