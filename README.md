# 🤖 AI Local Agent - Intelligent Desktop Assistant

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![LM Studio](https://img.shields.io/badge/LM%20Studio-Required-green.svg)](https://lmstudio.ai/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://github.com)

> **A powerful local AI assistant powered by LM Studio that helps you manage your computer through natural language commands.**

![AI Agent Demo](https://via.placeholder.com/800x400/1a1a2e/eaeaea?text=AI+Local+Agent)

---

## 📋 Table of Contents

- [Features](#-features)
- [Demo](#-demo)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage Examples](#-usage-examples)
- [Architecture](#-architecture)
- [Configuration](#-configuration)
- [Advanced Features](#-advanced-features)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [Roadmap](#-roadmap)
- [License](#-license)

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

## 🎬 Demo

```bash
> Привіт! Як справи?
🤖 AI Agent: Вітаю! Чудово, готовий допомогти. Що потрібно зробити?

> Знайди всі Python файли на робочому столі
🤖 AI Agent: Шукаю Python файли...
✅ Знайдено 5 файлів:
   - ai_agent.py (102 KB)
   - setup.py (8 KB)
   - extended_features.py (28 KB)

> Покажи інформацію про систему
🤖 AI Agent: 
💻 Система: Windows 11
🖥️ CPU: Intel Core i7-9700K @ 3.60GHz (8 cores)
💾 RAM: 16.0 GB (використано 62%)
💿 Диск C:\: 512 GB (вільно 128 GB)
```

---

## 🚀 Installation

### Prerequisites

1. **Python 3.8 or higher**
   ```bash
   python --version  # Should be 3.8+
   ```

2. **LM Studio**
   - Download from [lmstudio.ai](https://lmstudio.ai/)
   - Install and run the server on `http://localhost:1234`

### Step-by-Step Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/gtausa197-svg/ai_local_agent.git
   cd ai_local_agent
   ```

2. **Install dependencies**
   ```bash
   # Basic dependencies
   pip install -r requirements.txt
   
   # Extended features (optional)
   pip install -r requirements_extended.txt
   ```

3. **Run the setup script**
   ```bash
   python setup_extended.py
   ```
   This will:
   - ✅ Verify Python version
   - ✅ Create necessary directories
   - ✅ Install dependencies
   - ✅ Test module imports

---

## 🎯 Quick Start

### 1. Start LM Studio Server

1. Open LM Studio
2. Load your preferred model (e.g., GPT-4, Llama, Mistral)
3. Start the server on port `1234`

### 2. Configure the Agent

Edit `ai_agent.py` to set your preferences:

```python
class Config:
    LMSTUDIO_API_URL = "http://localhost:1234/v1/chat/completions"
    MODEL_NAME = "your-model-name"
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
```

### 3. Run the Agent

```bash
python ai_agent.py
```

or use the launcher:

```bash
python start_agent.py
```

---

## 📖 Usage Examples

### File Management

```python
# Search for files
> search_files C:\Users\*.txt

# Read a file
> read_file C:\document.txt

# Get file information
> file_info C:\image.jpg

# Find large files (over 100 MB)
> find_large_files C:\Downloads 100

# Find duplicate files
> find_duplicates C:\Photos
```

### System Monitoring

```python
# System information
> system_info

# Monitor performance for 2 minutes
> monitor_performance 120

# Check memory usage
> memory_info

# List top CPU-consuming processes
> list_processes cpu 10
```

### Network Operations

```python
# Check internet connection
> check_internet

# Download a file
> download_file https://example.com/file.zip C:\Downloads\file.zip

# Ping a host
> ping google.com 5

# Test internet speed
> speedtest
```

### Automation

```python
# Create a backup
> backup_files C:\Important C:\Backups

# Schedule a task
> schedule_task "Daily Backup" "backup_files C:\Data C:\Backup" "10:00" "daily"

# Auto cleanup
> auto_cleanup

# Find old files (older than 1 year)
> find_old_files C:\Temp 365
```

### Security

```python
# Encrypt a file
> encrypt_file C:\secrets.txt MySecurePassword123

# Decrypt a file
> decrypt_file C:\secrets.txt.encrypted MySecurePassword123

# Secure delete
> secure_delete C:\sensitive.doc

# Generate a secure password
> generate_password 20
```

### Archives

```python
# Create a ZIP archive
> compress_archive C:\Project C:\Archives\project.zip

# Extract an archive
> extract_archive C:\file.zip C:\Extracted
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│           User Interface (CLI)              │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│         LM Studio Client                    │
│  ┌──────────────────────────────────────┐   │
│  │  Natural Language Processing         │   │
│  │  Command Parsing & Execution         │   │
│  └──────────────────────────────────────┘   │
└──────────────────┬──────────────────────────┘
                   │
     ┌─────────────┼─────────────┐
     │             │             │
┌────▼────┐  ┌────▼────┐  ┌────▼────┐
│ File    │  │ System  │  │ Network │
│ Manager │  │ Monitor │  │ Manager │
└─────────┘  └─────────┘  └─────────┘
     │             │             │
┌────▼─────────────▼─────────────▼────┐
│    SQLite Database (Memory)         │
└─────────────────────────────────────┘
```

### Key Components

- **`ai_agent.py`**: Main agent core with basic functionality
- **`extended_features.py`**: Advanced features module
- **`start_agent.py`**: Agent launcher with GUI support
- **`setup_extended.py`**: Automated setup and installation
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
    
    # Monitoring thresholds
    CPU_ALERT_THRESHOLD = 90       # %
    MEMORY_ALERT_THRESHOLD = 85    # %
    DISK_ALERT_THRESHOLD = 90      # %
```

---

## 🔥 Advanced Features

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

### Database Queries

```python
# Access the agent's database
from ai_agent import AgentDatabase

db = AgentDatabase()

# Get command history
history = db.get_command_history(limit=20)

# Search file index
files = db.search_file_index("document")

# Save preferences
db.save_preference("theme", "dark")
```

---

## 🐛 Troubleshooting

### Common Issues

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

**Issue: "Permission denied" errors**
```bash
# Solution: Run with appropriate permissions
# On Windows: Run as Administrator
# On Linux/Mac: Use sudo if necessary
```

**Issue: "PIL/Pillow not working"**
```bash
# Solution: Reinstall Pillow
pip uninstall Pillow PIL
pip install Pillow
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

### Development Setup

```bash
# Clone your fork
git clone https://github.com/gtausa197-svg/ai_local_agent.git

# Install development dependencies
pip install -r requirements_dev.txt

# Run tests
python -m pytest tests/
```

---

## 🗺️ Roadmap

- [ ] **Telegram Bot Integration** - Control agent via Telegram
- [ ] **Web Dashboard** - Browser-based GUI
- [ ] **Voice Commands** - Speech-to-text integration
- [ ] **OCR Support** - Text recognition from images
- [ ] **Machine Learning** - Pattern recognition and predictions
- [ ] **Git Integration** - Repository management
- [ ] **Email Functions** - Send and receive emails
- [ ] **Docker Support** - Containerized deployment
- [ ] **Multi-language Support** - i18n implementation
- [ ] **Plugin System** - Extensible architecture

---

## 📊 Project Statistics

- **Total Functions**: 50+
- **Lines of Code**: ~2,500+
- **Classes**: 8
- **Modules**: 3
- **Supported OS**: Windows (primary), Linux, macOS (partial)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

- **Original Version**: AI Agent v2.0
- **Extended Version**: AI Agent Pro v3.0
- **Developer**: [gtausa197-svg](https://github.com/gtausa197-svg)
- **Contributors**: [See Contributors](https://github.com/gtausa197-svg/ai_local_agent/graphs/contributors)

---

## 🙏 Acknowledgments

- [LM Studio](https://lmstudio.ai/) - For the amazing local LLM platform
- OpenAI - For GPT architecture inspiration
- Python Community - For excellent libraries and tools

---

## 📞 Support

- **Documentation**: [Wiki](https://github.com/gtausa197-svg/ai_local_agent/wiki)
- **Issues**: [GitHub Issues](https://github.com/gtausa197-svg/ai_local_agent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/gtausa197-svg/ai_local_agent/discussions)

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

**🎉 Enjoy your intelligent desktop assistant!**

Made with ❤️ by **[gtausa197-svg](https://github.com/gtausa197-svg)**

[⬆ Back to Top](#-ai-local-agent---intelligent-desktop-assistant)

</div>
