# AI Meeting Assistant: Instant Notes, Zero Worries

A streamlined AI-powered meeting assistant that converts speech to text and processes transcriptions using advanced language models.

## 🎯 **Current Status: Phase 3 Complete**

✅ **Phase 1**: Whisper Exploration & Mastery  
✅ **Phase 2**: Working Web Interface (Custom Solution)  
✅ **Phase 3**: Complete Speech-to-Text Application  
🎯 **Ready for Phase 4**: Ollama LLM Integration

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.11+ with pyenv
- Poetry for dependency management
- ffmpeg for audio processing: `brew install ffmpeg`

### **Installation**
```bash
# Clone the repository
git clone <your-repo-url>
cd ai-meeting-assistant

# Install dependencies
poetry install
poetry shell

# Download sample audio
python setup.py

# Test installation
python test_setup.py
```

### **Launch the App**
```bash
# Enhanced version (recommended) - http://localhost:8080
cd src && python -m main

# Basic version - http://localhost:8080  
cd src && python -m main --version simple

# See all options
cd src && python -m main --help
```

## ✨ **Features**

### **🎤 Speech-to-Text (Phase 3 Complete)**
- **Multiple Whisper Models**: Choose from tiny (fast) to medium (accurate)
- **Multi-Format Support**: WAV, MP3, M4A, FLAC, OGG, AAC, MP4, WebM
- **Professional Web Interface**: Upload files or record directly
- **Real-Time Processing**: Progress indicators and live status updates
- **Model Caching**: 30x faster subsequent transcriptions
- **Export Options**: Download as TXT or JSON with metadata
- **Mobile-Responsive**: Works on all devices

### **📱 Available Versions**
| Version | Features | Best For |
|---------|----------|----------|
| **Enhanced-Simple** | All features, multiple models, exports | **Recommended** |
| **Simple** | Basic transcription, reliable | Testing, minimal needs |

## 🏗️ **Project Structure**

```
ai-meeting-assistant/
├── src/                          # Core application
│   ├── main.py                   # Entry point
│   ├── enhanced_simple_server.py # Full-featured server
│   ├── simple_server.py          # Basic server
│   ├── config.py                 # Configuration
│   ├── test_whisper_direct.py    # Core testing
│   ├── audio_processing/         # Audio components
│   └── llm_processing/           # Ready for Phase 4
├── data/audio_samples/           # Sample files
├── archive/                      # Non-working attempts (git ignored)
├── docs/                         # Documentation
├── test_setup.py                 # Installation validation
└── setup.py                      # Initial setup utility
```

## 🛠️ **Dependencies**

### **Core AI Stack**
- **Transformers 4.35.2**: Whisper model integration
- **PyTorch 2.1.1**: ML framework
- **NumPy <2.0**: Compatibility layer

### **LLM Integration (Phase 4 Ready)**
- **LangChain 0.3.12**: Workflow orchestration
- **Ollama**: Local LLM server
- **LangChain-Ollama**: Integration layer

### **Utilities**
- **Pydantic**: Data validation
- **Requests**: HTTP client

## 🧪 **Testing & Validation**

```bash
# Comprehensive testing
python test_setup.py

# Core Whisper functionality
python src/test_whisper_direct.py

# Web interface testing
cd src && python -m main --version simple
# Test at http://localhost:8080
```

## 📋 **Development Roadmap**

### **✅ Completed Phases**
- **Phase 1**: Whisper model exploration and optimization
- **Phase 2**: Custom web interface (bypassed Gradio compatibility issues)
- **Phase 3**: Complete speech-to-text application with exports

### **🎯 Phase 4: Ollama LLM Integration** (Next)
- Meeting summary generation
- Key point extraction
- Action item identification
- Speaker analysis
- Content categorization

### **🔮 Future Phases**
- **Phase 5**: Advanced text processing and formatting
- **Phase 6**: LangChain workflow integration
- **Phase 7**: Complete end-to-end meeting assistant

## 🎨 **Design Philosophy**

### **Reliability Over Complexity**
- Custom server solution instead of framework dependencies
- Proven, tested components only
- No compatibility issues or dependency hell

### **Performance Focused**
- Model caching for 30x speed improvements
- Efficient audio processing
- Optimized for repeated use

### **User Experience First**
- Professional, intuitive interface
- Real-time feedback and progress
- Multiple export options
- Mobile-responsive design

## 🤝 **Contributing**

This project demonstrates a practical approach to AI application development:
1. **Start with working solutions** (custom servers vs. broken frameworks)
2. **Focus on core functionality** (excellent transcription)
3. **Build incrementally** (phases 1-3 complete, 4-7 planned)
4. **Maintain clean architecture** (archived non-working attempts)

## 📄 **License**

This project is for educational and development purposes.

## 🆘 **Support**

- **Issues**: See `docs/` for troubleshooting
- **Testing**: Run `python test_setup.py` for diagnostics
- **Archive**: Non-working attempts preserved in `archive/` for reference

---

**Built with ❤️ using Python, Whisper AI, and custom web solutions**
