from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import sys
import os

# Add the parent directory to Python path to import ShortGPT modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shortGPT.config.api_db import ApiKeyManager
from shortGPT.api_utils.eleven_api import ElevenLabsAPI

app = FastAPI(title="ShortGPT API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_progress(self, progress: float, message: str):
        data = {"progress": progress, "message": message}
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(data))
            except:
                # Remove broken connections
                self.disconnect(connection)

manager = ConnectionManager()

@app.get("/")
async def root():
    return {"message": "ShortGPT API is running"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

@app.websocket("/ws/progress")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Assets endpoints
@app.get("/api/assets")
async def get_assets():
    return {"assets": [], "message": "Asset API coming soon"}

@app.post("/api/assets")
async def create_asset():
    return {"message": "Upload endpoint coming soon"}

# Content automation endpoints
@app.post("/api/shorts")
async def create_short():
    return {"message": "Short creation endpoint coming soon"}

@app.post("/api/video")
async def create_video():
    return {"message": "Video creation endpoint coming soon"}

@app.post("/api/translate")
async def translate_video():
    return {"message": "Translation endpoint coming soon"}

# Pydantic models for API requests
class ApiKeys(BaseModel):
    OPENAI_API_KEY: str = ""
    ELEVENLABS_API_KEY: str = ""
    PEXELS_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""

class ElevenLabsVerify(BaseModel):
    api_key: str

# Config endpoints
@app.get("/api/config/keys")
async def get_api_keys():
    """Get all API keys"""
    try:
        api_manager = ApiKeyManager()
        return {
            "OPENAI_API_KEY": api_manager.get_api_key("OPENAI_API_KEY"),
            "ELEVENLABS_API_KEY": api_manager.get_api_key("ELEVENLABS_API_KEY"),
            "PEXELS_API_KEY": api_manager.get_api_key("PEXELS_API_KEY"),
            "GEMINI_API_KEY": api_manager.get_api_key("GEMINI_API_KEY"),
            "GROQ_API_KEY": api_manager.get_api_key("GROQ_API_KEY")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/config/keys")
async def save_api_keys(api_keys: ApiKeys):
    """Save API keys"""
    try:
        api_manager = ApiKeyManager()
        
        if api_keys.OPENAI_API_KEY:
            api_manager.set_api_key("OPENAI_API_KEY", api_keys.OPENAI_API_KEY)
        if api_keys.ELEVENLABS_API_KEY:
            api_manager.set_api_key("ELEVENLABS_API_KEY", api_keys.ELEVENLABS_API_KEY)
        if api_keys.PEXELS_API_KEY:
            api_manager.set_api_key("PEXELS_API_KEY", api_keys.PEXELS_API_KEY)
        if api_keys.GEMINI_API_KEY:
            api_manager.set_api_key("GEMINI_API_KEY", api_keys.GEMINI_API_KEY)
        if api_keys.GROQ_API_KEY:
            api_manager.set_api_key("GROQ_API_KEY", api_keys.GROQ_API_KEY)
            
        return {"message": "API keys saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/config/elevenlabs/verify")
async def verify_elevenlabs_key(request: ElevenLabsVerify):
    """Verify ElevenLabs API key and get remaining characters"""
    try:
        if not request.api_key:
            raise HTTPException(status_code=400, detail="API key is required")
            
        eleven_api = ElevenLabsAPI(request.api_key)
        characters_remaining = eleven_api.get_remaining_characters()
        
        return {
            "valid": True,
            "characters_remaining": str(characters_remaining)
        }
    except Exception as e:
        return {
            "valid": False,
            "characters_remaining": f"Error: {str(e)}"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)