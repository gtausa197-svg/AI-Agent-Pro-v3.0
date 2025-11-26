# 🤖 AI Local Agent - Intelligent Desktop Assistant

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![LM Studio](https://img.shields.io/badge/LM%20Studio-Required-green.svg)](https://lmstudio.ai/)
[![React](https://img.shields.io/badge/React-18.2-61DAFB.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://github.com)

> **A powerful local AI assistant powered by LM Studio that helps you manage your computer through natural language commands - now with a beautiful web interface!**

![AI Agent Demo](https://via.placeholder.com/800x400/1a1a2e/eaeaea?text=AI+Local+Agent+Web+Interface)

---

## 📋 Table of Contents

- [Features](#-features)
- [What's New - Web Interface](#-whats-new---web-interface)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
  - [CLI Mode](#1-cli-mode-traditional)
  - [Web Interface Mode](#2-web-interface-mode-new)
- [Usage Examples](#-usage-examples)
- [Architecture](#-architecture)
- [Configuration](#-configuration)
- [Advanced Features](#-advanced-features)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [Roadmap](#-roadmap)
- [License](#-license)

---

## 🆕 What's New - Web Interface!

**AI Local Agent now includes a professional web interface!** 🌐

### Web Dashboard Features:
- 📊 **Real-time System Monitoring** - Live CPU, RAM, Disk usage with auto-refresh
- 📈 **Interactive Charts** - Performance graphs with Recharts
- 💬 **Command Center** - Execute commands through a beautiful UI
- 📜 **Command History** - View all executed commands with results
- 🌓 **Dark/Light Theme** - Toggle between themes
- 📱 **Responsive Design** - Works on desktop and mobile
- 🔌 **WebSocket Support** - Live updates every 2 seconds

### Technology Stack:
- **Backend**: FastAPI + WebSocket
- **Frontend**: React + Vite + Tailwind CSS
- **Charts**: Recharts
- **State Management**: Zustand

---

## ✨ Features

### 🗂️ **File System Management**
- 📄 Read, search, and manage files
- 📁 Create, move, copy, and delete files/folders
- 🔍 Advanced search with pattern matching
- 🔎 Search text within files
- 📊 File indexing and metadata management
- 🔐 File hash computation (MD5, SHA256)
- 📦 Find large files and duplicates
- 📂 Comprehensive folder analysis

### 💻 **Application & Process Management**
- 🚀 Launch and close applications
- 📋 List installed programs
- 🔄 Monitor running processes
- ❌ Kill frozen or unresponsive apps
- 📊 Process information and statistics
- 🧹 System optimization

### 🖥️ **System Monitoring**
- 📈 Real-time CPU, RAM, and disk monitoring
- 🌡️ System temperature tracking
- 🔋 Battery status (laptops)
- 🌐 Network information and connections
- 📊 Performance analytics
- 📝 Comprehensive system reports

### 🌐 **Internet & Network**
- 🔗 Check internet connectivity
- 📥 Download files from URLs
- 🌍 Open webpages
- 🏓 Ping hosts
- 🌐 Get IP information
- 🔌 List active network connections
- ⚡ Internet speed test
- ✅ Website status checker

### 💾 **Memory & Context Management**
- 🧠 Remember and recall information
- 📚 Command history tracking
- 🗃️ SQLite database for persistent storage
- 🔄 Context-aware responses
- 📊 User preferences storage

### 🛠️ **Utilities**
- 🧮 Built-in calculator
- 🔐 Password generator
- 🔒 Text hashing (multiple algorithms)
- ⏰ Time and date functions
- 📋 Clipboard management
- 🖼️ Screenshot capture
- 📦 Archive creation and extraction (ZIP, TAR.GZ)
- 🔐 File encryption/decryption
- 🗑️ Secure file deletion

### 📊 **Analytics & Reporting**
- 📈 Usage statistics
- 🐛 Error reporting
- 📋 Log analysis
- 📊 System performance reports

### 🔔 **Automation**
- ⏰ Task scheduling
- 🔄 Automatic system cleanup
- 💾 Automated backups
- 📁 Directory monitoring
- 🔔 System notifications

---

## 🚀 Installation

### Prerequisites

1. **Python 3.8 or higher**
   ```bash
   python --version  # Should be 3.8+
   ```

2. **Node.js 18+ (for Web Interface)**
   ```bash
   node --version  # Should be 18+
   npm --version
   ```
   Download from [nodejs.org](https://nodejs.org/)

3. **LM Studio**
   - Download from [lmstudio.ai](https://lmstudio.ai/)
   - Install and run the server on `http://localhost:1234`

### Step-by-Step Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/gtausa197-svg/ai_local_agent.git
   cd ai_local_agent
   ```

2. **Install Python dependencies**
   ```bash
   # Basic dependencies
   pip install psutil requests
   
   # Extended features (optional)
   pip install -r requirements_extended.txt
   ```

3. **Install Backend API dependencies (for Web Interface)**
   ```bash
   cd backend
   pip install -r requirements_api.txt
   cd ..
   ```

4. **Install Frontend dependencies (for Web Interface)**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

---

## 🎯 Quick Start

You can run AI Local Agent in **two modes**: CLI (traditional) or Web Interface (new).

### 1. CLI Mode (Traditional)

#### Step 1: Start LM Studio Server

1. Open LM Studio
2. Load your preferred model (e.g., GPT-4, Llama, Mistral)
3. Start the server on port `1234`

#### Step 2: Run the Agent

```bash
python ai_agent.py
```

or use the launcher:

```bash
python start_agent.py
```

#### Step 3: Start Using!

```bash
> Привіт! Як справи?
🤖 AI Agent: Вітаю! Чудово, готовий допомогти. Що потрібно зробити?

> Знайди всі Python файли на робочому столі
🤖 AI Agent: Шукаю Python файли...
✅ Знайдено 5 файлів:
   - ai_agent.py (102 KB)
   - setup.py (8 KB)
   - extended_features.py (28 KB)
```

---

### 2. Web Interface Mode (NEW! 🌐)

#### Step 1: Start LM Studio Server

Same as CLI mode - ensure LM Studio is running on `http://localhost:1234`

#### Step 2: Start Backend API

**Open Terminal 1:**

```bash
cd backend

# Create virtual environment (first time only)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies (first time only)
pip install -r requirements_api.txt

# Start FastAPI server
python -m uvicorn api.main:app --reload
```

**✅ Backend should show:**
```
🚀 AI Local Agent API starting...
📡 WebSocket endpoint: ws://localhost:8000/ws
📚 API documentation: http://localhost:8000/api/docs
✅ API ready!
INFO:     Uvicorn running on http://127.0.0.1:8000
```

#### Step 3: Start Frontend

**Open Terminal 2 (new terminal):**

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

**✅ Frontend should show:**
```
VITE v5.0.8  ready in XXX ms

➜  Local:   http://localhost:5173/
```

#### Step 4: Open Web Interface

**Open your browser and visit:**

```
http://localhost:5173
```

### 🎉 You should see:

1. **Dashboard** page with:
   - 📊 CPU, RAM, Disk usage cards
   - 📈 Live performance chart
   - 🔌 WebSocket connection status
   - 🎯 Quick action buttons

2. **Commands** page (click in navigation):
   - 💬 Command input field
   - 📜 Command history with results
   - ✅ Success/failure indicators

### Quick Actions:

- 🌓 **Toggle Theme**: Click moon/sun icon in navigation
- 🔄 **Real-time Stats**: Updates automatically every 2 seconds
- 💻 **Execute Commands**: Type in natural language and click Execute
- 📊 **View Charts**: Watch live performance graphs

---

## 📖 Usage Examples

### Web Interface Commands

Open the **Commands** page and try these:

```
show system info
```
```
search for *.py files in Desktop
```
```
what is my CPU usage?
```
```
list running processes
```

### CLI Commands

```python
# Search for files
> search_files C:\Users\*.txt

# Read a file
> read_file C:\document.txt

# System information
> system_info

# Monitor performance for 2 minutes
> monitor_performance 120

# Download a file
> download_file https://example.com/file.zip C:\Downloads\file.zip

# Create a backup
> backup_files C:\Important C:\Backups

# Encrypt a file
> encrypt_file C:\secrets.txt MySecurePassword123
```

---

## 🏗️ Architecture

### Overall System Architecture

```
┌─────────────────────────────────────────────────┐
│         Browser (http://localhost:5173)         │
│  ┌──────────────────────────────────────────┐   │
│  │  React Frontend                          │   │
│  │  - Dashboard (Real-time monitoring)      │   │
│  │  - Command Interface                     │   │
│  │  - Live Charts (Recharts)                │   │
│  └──────────────────────────────────────────┘   │
└──────────────┬──────────────┬───────────────────┘
               │              │
        HTTP REST API    WebSocket (Real-time)
               │              │
┌──────────────▼──────────────▼───────────────────┐
│    FastAPI Backend (http://localhost:8000)      │
│  ┌──────────────────────────────────────────┐   │
│  │  API Routes                              │   │
│  │  - /api/system/stats                     │   │
│  │  - /api/commands/execute                 │   │
│  │  - /ws (WebSocket)                       │   │
│  └──────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────┐   │
│  │  Agent Bridge                            │   │
│  │  - Integration with AI Agent Core        │   │
│  └──────────────────────────────────────────┘   │
└──────────────┬──────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────┐
│        AI Local Agent Core                      │
│  ┌──────────────────────────────────────────┐   │
│  │  LMStudioClient + AgentDatabase          │   │
│  │  File Manager, System Monitor, Network   │   │
│  └──────────────────────────────────────────┘   │
│                     │                           │
│  ┌──────────────────▼───────────────────────┐   │
│  │  SQLite Database (Persistent Storage)    │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

### Key Components

**CLI Mode:**
- **`ai_agent.py`**: Main agent core with basic functionality
- **`extended_features.py`**: Advanced features module
- **`start_agent.py`**: Agent launcher with GUI support

**Web Interface Mode:**
- **`backend/api/main.py`**: FastAPI application with REST + WebSocket
- **`backend/api/utils/agent_bridge.py`**: Bridge to AI agent core
- **`frontend/src/App.jsx`**: React application entry point
- **`frontend/src/components/Dashboard/`**: Dashboard components
- **`frontend/src/components/CommandInterface/`**: Command execution UI

**Shared:**
- **`knowledge_base/`**: SQLite database for persistent storage
- **`logs/`**: Application logs and error tracking

---

## ⚙️ Configuration

### Environment Variables

```bash
# Optional: Set custom LM Studio URL
export LMSTUDIO_API_URL="http://localhost:1234/v1/chat/completions"

# Optional: Set custom model name
export MODEL_NAME="llama-2-13b"
```

### Config Class

Edit the `Config` class in `ai_agent.py`:

```python
class Config:
    # LM Studio API
    LMSTUDIO_API_URL = "http://localhost:1234/v1/chat/completions"
    MODEL_NAME = "openai/gpt-oss-20b"
    
    # Security
    FORBIDDEN_PATHS = [
        'C:\\Windows\\System32',
        '/system',
        '/sys'
    ]
    
    # Limits
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    MAX_SEARCH_RESULTS = 100
    MAX_HISTORY_MESSAGES = 50
```

### Web Interface Configuration

**Backend Port** - Edit `backend/api/main.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Frontend Port** - Edit `frontend/vite.config.js`:
```javascript
server: {
  port: 5173
}
```

---

## 🔥 Advanced Features

### Web Interface API

The backend provides REST API endpoints:

```python
# System Information
GET  http://localhost:8000/api/system/info
GET  http://localhost:8000/api/system/stats
GET  http://localhost:8000/api/system/processes

# Commands
POST http://localhost:8000/api/commands/execute?command=system_info
GET  http://localhost:8000/api/commands/history

# Files
GET  http://localhost:8000/api/files/search?pattern=*.py

# WebSocket (Real-time)
WS   ws://localhost:8000/ws
```

**API Documentation:**
Visit `http://localhost:8000/api/docs` for interactive Swagger UI

### Custom Function Integration

```python
from extended_features import (
    MultimediaManager,
    SystemUtilities,
    MonitoringManager
)

# Use multimedia features
multimedia = MultimediaManager(screenshots_dir)
screenshot = multimedia.take_screenshot("desktop")

# System utilities
utils = SystemUtilities()
utils.send_notification("Task Complete", "Backup finished!")

# Monitoring
monitor = MonitoringManager(db)
stats = monitor.get_usage_statistics()
```

---

## 🐛 Troubleshooting

### CLI Issues

**Issue: "Cannot connect to LM Studio"**
```bash
# Solution: Ensure LM Studio is running
# Check if the server is accessible at http://localhost:1234
```

**Issue: "Module not found"**
```bash
# Solution: Reinstall dependencies
pip install --upgrade -r requirements_extended.txt
```

### Web Interface Issues

**Issue: "Backend not starting"**
```bash
# Check if port 8000 is already in use
# Kill the process or use a different port

# Install missing dependencies
cd backend
pip install -r requirements_api.txt
```

**Issue: "Frontend shows blank page"**
```bash
# Solution: Install Node.js dependencies
cd frontend
rm -rf node_modules package-lock.json  # Clean install
npm install
npm run dev
```

**Issue: "WebSocket not connecting"**
```bash
# Solution: Ensure backend is running on port 8000
# Check browser console for errors (F12)
# Verify CORS settings in backend/api/main.py
```

**Issue: "ModuleNotFoundError: No module named 'requests'"**
```bash
# Solution: Install dependencies in backend venv
cd backend
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements_api.txt
```

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit your changes**
   ```bash
   git commit -m 'Add amazing feature'
   ```
4. **Push to the branch**
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open a Pull Request**

---

## 🗺️ Roadmap

### Completed ✅
- [x] **Web Dashboard** - Browser-based GUI with real-time monitoring
- [x] **REST API** - FastAPI backend with WebSocket support
- [x] **Command Interface** - Execute commands through web UI

### In Progress 🚧
- [ ] **File Manager UI** - Web-based file browser
- [ ] **System Monitor Page** - Process list and detailed monitoring

### Planned 📋
- [ ] **Telegram Bot Integration** - Control agent via Telegram
- [ ] **Voice Commands** - Speech-to-text integration
- [ ] **OCR Support** - Text recognition from images
- [ ] **Machine Learning** - Pattern recognition and predictions
- [ ] **Git Integration** - Repository management
- [ ] **Docker Support** - Containerized deployment
- [ ] **Plugin System** - Extensible architecture
- [ ] **Mobile App** - iOS/Android companion app

---

## 📊 Project Statistics

- **Total Functions**: 50+
- **Lines of Code**: ~4,000+
- **Classes**: 12+
- **Modules**: 5
- **API Endpoints**: 10+
- **React Components**: 15+
- **Supported OS**: Windows (primary), Linux, macOS (partial)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

- **Original Version**: AI Agent v2.0
- **Extended Version**: AI Agent Pro v3.0
- **Web Interface**: AI Agent Pro v3.1
- **Developer**: [gtausa197-svg](https://github.com/gtausa197-svg)
- **Contributors**: [See Contributors](https://github.com/gtausa197-svg/ai_local_agent/graphs/contributors)

---

## 🙏 Acknowledgments

- [LM Studio](https://lmstudio.ai/) - For the amazing local LLM platform
- [FastAPI](https://fastapi.tiangolo.com/) - For the modern Python web framework
- [React](https://reactjs.org/) - For the powerful UI library
- [Vite](https://vitejs.dev/) - For the blazing fast build tool
- [Tailwind CSS](https://tailwindcss.com/) - For the utility-first CSS framework
- OpenAI - For GPT architecture inspiration
- Python Community - For excellent libraries and tools

---

## 📞 Support

- **Documentation**: [Wiki](https://github.com/gtausa197-svg/ai_local_agent/wiki)
- **Issues**: [GitHub Issues](https://github.com/gtausa197-svg/ai_local_agent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/gtausa197-svg/ai_local_agent/discussions)
- **Web Interface Guide**: [WEB_INTERFACE_SETUP.md](WEB_INTERFACE_SETUP.md)

---

## 💝 Support the Project

If you find this project useful, please consider:

- ⭐ **Starring the repository**
- 🐛 **Reporting bugs**
- 💡 **Suggesting new features**
- 🤝 **Contributing code**
- 📢 **Sharing with others**

---

<div align="center">

**🎉 Enjoy your intelligent desktop assistant - now with a beautiful web interface!**

Made with ❤️ by **[gtausa197-svg](https://github.com/gtausa197-svg)**

[⬆ Back to Top](#-ai-local-agent---intelligent-desktop-assistant)

</div>