"""
FastAPI Application - Main Entry Point
AI Local Agent Web API
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import logging
from typing import List

# Import our bridge to AI Agent
from api.utils.agent_bridge import agent_bridge

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Local Agent API",
    description="REST API for AI Local Agent Web Interface",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite and React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connections manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting: {e}")

manager = ConnectionManager()


# ============================================================================
# ROOT ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "AI Local Agent API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/api/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# ============================================================================
# SYSTEM ENDPOINTS
# ============================================================================

@app.get("/api/system/info")
async def get_system_info():
    """Get comprehensive system information"""
    try:
        info = agent_bridge.get_system_info()
        return JSONResponse(content=info)
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.get("/api/system/stats")
async def get_system_stats():
    """Get quick system stats (CPU, RAM, Disk)"""
    try:
        info = agent_bridge.get_system_info()
        return {
            "cpu": info["cpu"]["percent"],
            "memory": info["memory"]["percent"],
            "disk": info["disk"]["percent"],
            "timestamp": info["timestamp"]
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/system/processes")
async def get_processes(limit: int = 20):
    """Get running processes"""
    try:
        processes = agent_bridge.get_processes(limit=limit)
        return {"processes": processes}
    except Exception as e:
        return {"error": str(e)}


# ============================================================================
# COMMAND ENDPOINTS
# ============================================================================

@app.post("/api/commands/execute")
async def execute_command(command: str):
    """Execute a command through AI Agent"""
    try:
        result = agent_bridge.execute_command(command)
        return result
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/commands/history")
async def get_command_history(limit: int = 50):
    """Get command execution history"""
    try:
        history = agent_bridge.get_command_history(limit=limit)
        return {"history": history}
    except Exception as e:
        return {"error": str(e)}


# ============================================================================
# FILE ENDPOINTS
# ============================================================================

@app.get("/api/files/search")
async def search_files(pattern: str, directory: str = None, limit: int = 100):
    """Search for files"""
    try:
        results = agent_bridge.search_files(
            pattern=pattern,
            directory=directory,
            limit=limit
        )
        return {"results": results, "count": len(results) if isinstance(results, list) else 0}
    except Exception as e:
        return {"error": str(e)}


# ============================================================================
# WEBSOCKET ENDPOINT
# ============================================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time system stats"""
    await manager.connect(websocket)
    try:
        # Send stats every 2 seconds
        while True:
            try:
                stats = agent_bridge.get_system_info()
                await websocket.send_json({
                    "type": "system_stats",
                    "data": {
                        "cpu": stats["cpu"]["percent"],
                        "memory": stats["memory"]["percent"],
                        "disk": stats["disk"]["percent"],
                        "timestamp": stats["timestamp"]
                    }
                })
                await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"Error in WebSocket loop: {e}")
                break
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


# ============================================================================
# STARTUP EVENT
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("🚀 AI Local Agent API starting...")
    logger.info("📡 WebSocket endpoint: ws://localhost:8000/ws")
    logger.info("📚 API documentation: http://localhost:8000/api/docs")
    logger.info("✅ API ready!")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
