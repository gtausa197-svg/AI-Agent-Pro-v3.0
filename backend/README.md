# 🚀 AI Local Agent - Backend API

## Quick Start

### Installation

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements_api.txt
```

### Running the Server

```bash
# From ai_local_agent directory
cd backend
python -m uvicorn api.main:app --reload --port 8000
```

Server will start on: http://localhost:8000

## API Documentation

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## Endpoints

### System
- `GET /api/system/info` - Full system information
- `GET /api/system/stats` - Quick stats (CPU, RAM, Disk)
- `GET /api/system/processes` - Running processes

### Commands
- `POST /api/commands/execute` - Execute AI agent command
- `GET /api/commands/history` - Command history

### Files
- `GET /api/files/search?pattern=*.py` - Search files

### WebSocket
- `WS /ws` - Real-time system stats (updates every 2s)

## Testing

### Using curl

```bash
# System info
curl http://localhost:8000/api/system/stats

# Execute command
curl -X POST "http://localhost:8000/api/commands/execute?command=system_info"

# Search files
curl "http://localhost:8000/api/files/search?pattern=*.py&limit=10"
```

### Using Browser

Visit http://localhost:8000/api/docs for interactive API testing

## WebSocket Client Example

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('System stats:', data);
};
```

## Notes

- CORS enabled for http://localhost:5173 (Vite) and http://localhost:3000 (React)
- All endpoints return JSON
- WebSocket provides real-time system monitoring
