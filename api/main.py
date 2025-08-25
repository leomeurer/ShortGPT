from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI(title="ShortGPT API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)