"""
Main entry point for the AI Meeting Assistant
Streamlined for working versions only: simple + enhanced-simple
"""
import sys
import argparse
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent))

def main():
    parser = argparse.ArgumentParser(description="AI Meeting Assistant - Speech to Text")
    parser.add_argument(
        "--version", 
        choices=["simple", "enhanced-simple"],
        default="enhanced-simple",
        help="Choose app version to run"
    )
    parser.add_argument(
        "--port",
        type=int, 
        default=8080,
        help="Port to run the server on (default: 8080)"
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host to bind the server to (default: localhost)"
    )
    
    args = parser.parse_args()
    
    print(f"🎤 AI Meeting Assistant - Starting {args.version} version...")
    print(f"🌐 Server will be available at: http://{args.host}:{args.port}")
    print("🔄 Press Ctrl+C to stop the server\n")
    
    if args.version == "simple":
        print("🚀 Launching Simple Server...")
        print("✨ Features: Basic transcription, file upload, clean interface")
        import simple_server
        simple_server.main()
        
    elif args.version == "enhanced-simple":
        print("🚀 Launching Enhanced Simple Server (Phase 3)...")
        print("✨ Features: Multiple models, progress indicators, export options, enhanced UI")
        import enhanced_simple_server
        enhanced_simple_server.main()
    
    else:
        # This should never happen due to choices constraint, but just in case
        print(f"❌ Unknown version: {args.version}")
        print("Available versions: simple, enhanced-simple")
        sys.exit(1)

def show_help():
    """Show helpful information about available versions"""
    print("""
🎤 AI Meeting Assistant - Version Guide

📱 Available Versions:

┌─────────────────┬──────────────────────────────────────────┐
│ Version         │ Features                                 │
├─────────────────┼──────────────────────────────────────────┤
│ simple          │ • Basic Whisper transcription            │
│                 │ • File upload interface                  │
│                 │ • Clean, reliable web UI                 │
│                 │ • Model caching (30x faster repeats)     │
│                 │ • Runs on http://localhost:8080          │
├─────────────────┼──────────────────────────────────────────┤
│ enhanced-simple │ • All simple features +                  │
│ (recommended)   │ • Multiple Whisper models                │
│                 │ • Progress indicators                    │
│                 │ • Processing statistics                  │
│                 │ • Export options (TXT, JSON)             │
│                 │ • Enhanced responsive UI                 │
│                 │ • Multi-format support                   │
│                 │ • Batch size control                     │
└─────────────────┴──────────────────────────────────────────┘

🚀 Quick Start:
    python -m main                        # Enhanced version (default)
    python -m main --version simple       # Basic version
    python -m main --help                 # Show this help

🧪 Testing:
    python test_setup.py                  # Validate installation
    python test_whisper_direct.py         # Test core Whisper functionality

📚 More Info:
    • README.md - Project overview
    • ROADMAP.md - Development phases
    • docs/ - Technical documentation
""")

if __name__ == "__main__":
    # Show help if requested
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help", "help"]:
        show_help()
    else:
        main()
