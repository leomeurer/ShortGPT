#!/usr/bin/env python3
"""
ShortGPT Dual Frontend Server
Serves both React frontend and Gradio legacy interface
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        print("✅ FastAPI dependencies found")
    except ImportError:
        print("❌ FastAPI dependencies missing. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "api/requirements.txt"], check=True)

def build_react_app():
    """Build React app for production"""
    web_dir = Path("web")
    if not web_dir.exists():
        print("❌ React app directory not found")
        return False
    
    print("📦 Building React app...")
    try:
        subprocess.run(["npm", "run", "build"], cwd=web_dir, check=True, cwd=str(web_dir))
        print("✅ React app built successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to build React app")
        return False

def start_server(mode="hybrid"):
    """Start the server in specified mode"""
    if mode == "react":
        # Serve only React frontend
        from api.main import app
        from fastapi.staticfiles import StaticFiles
        
        # Mount React build
        app.mount("/", StaticFiles(directory="web/dist", html=True), name="react")
        
        import uvicorn
        print("🚀 Starting React-only server on http://localhost:8000")
        uvicorn.run(app, host="0.0.0.0", port=8000)
        
    elif mode == "gradio":
        # Start legacy Gradio interface
        from gui.gui_gradio import ShortGptUI
        print("🚀 Starting Gradio server on http://localhost:31415")
        app = ShortGptUI()
        app.launch()
        
    elif mode == "hybrid":
        # Hybrid mode - FastAPI serves React, Gradio runs on different port
        print("🚀 Starting Hybrid mode:")
        print("   📱 React Frontend: http://localhost:8000")
        print("   🎛️  Gradio Legacy: http://localhost:31415")
        
        # Start Gradio in background
        gradio_process = subprocess.Popen([sys.executable, "-c", """
from gui.gui_gradio import ShortGptUI
app = ShortGptUI()
app.launch()
        """])
        
        # Start FastAPI with React
        from api.main import app
        from fastapi.staticfiles import StaticFiles
        
        # Mount React build or dev server
        if Path("web/dist").exists():
            app.mount("/", StaticFiles(directory="web/dist", html=True), name="react")
        else:
            # Development mode - proxy to Vite dev server
            print("ℹ️  Development mode: Make sure to run 'npm run dev' in web/ directory")
        
        import uvicorn
        try:
            uvicorn.run(app, host="0.0.0.0", port=8000)
        finally:
            gradio_process.terminate()

def main():
    """Main entry point"""
    import argparse
    parser = argparse.ArgumentParser(description="ShortGPT Server")
    parser.add_argument("--mode", choices=["react", "gradio", "hybrid"], default="hybrid",
                       help="Server mode (default: hybrid)")
    parser.add_argument("--build", action="store_true", help="Build React app before starting")
    
    args = parser.parse_args()
    
    print("🎬 ShortGPT - Dual Frontend System")
    print("=" * 40)
    
    check_dependencies()
    
    if args.build:
        build_react_app()
    
    start_server(args.mode)

if __name__ == "__main__":
    main()