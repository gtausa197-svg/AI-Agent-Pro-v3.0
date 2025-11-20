# 🤖 AI Local Agent

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://github.com)

> A powerful local AI assistant powered by LM Studio that helps you manage your computer through natural language commands.

---

## Features

- 🗂️ **File Management** - Search, read, copy, move, and organize files
-  **Application Control** - Launch and manage applications
- 🖥️ **System Monitoring** - Track CPU, RAM, disk usage, and processes
- 🌐 **Network Operations** - Download files, check connectivity, ping hosts
- 💾 **Smart Memory** - Remember preferences and command history
- 🛠️ **Utilities** - Calculator, password generator, screenshots, archives
- 📊 **Analytics** - Usage statistics and system reports
- 🔔 **Automation** - Schedule tasks and automated backups

---

## Installation

### Requirements

- Python 3.8+
- LM Studio ([Download](https://lmstudio.ai/))

### Setup

1. Clone the repository:
```bash
git clone https://github.com/gtausa197-svg/ai_local_agent.git
cd ai_local_agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the setup (optional):
```bash
python setup_extended.py
```

---

## Quick Start

1. **Start LM Studio** on `http://localhost:1234`
2. **Load a model** (e.g., Mistral-7B, Llama-2)
3. **Run the agent**:
```bash
python ai_agent.py
```

---

## Usage Examples

### File Operations
```bash
# Search for files
> search_files C:\Projects *.py

# Find large files
> find_large_files C:\Downloads 100

# Create backup
> backup_files C:\Important C:\Backups
```

### System Monitoring
```bash
# System information
> system_info

# Monitor performance
> monitor_performance 120

# List processes
> list_processes
```

### Network
```bash
# Check internet
> check_internet

# Download file
> download_file https://example.com/file.zip C:\Downloads\file.zip

# Speed test
> speedtest
```

### Automation
```bash
# Auto cleanup
> auto_cleanup

# Schedule task
> schedule_task "Daily Backup" "backup_files C:\Data C:\Backup" "02:00" "daily"
```

---

## Configuration

Edit `ai_agent.py` to customize settings:

```python
class Config:
    LMSTUDIO_API_URL = "http://localhost:1234/v1/chat/completions"
    MODEL_NAME = "your-model-name"
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
```

---

## Project Structure

```
ai_local_agent/
├── ai_agent.py              # Main agent
├── extended_features.py     # Additional features
├── start_agent.py           # Launcher
├── logs/                    # Log files
├── knowledge_base/          # Database
├── cache/                   # Cache
└── backups/                 # Backups
```

---

## Troubleshooting

**LM Studio not connecting?**
- Ensure LM Studio is running on `http://localhost:1234`
- Check if a model is loaded

**Module not found?**
```bash
pip install --upgrade -r requirements.txt
```

**Permission errors?**
- Some system paths are protected by design
- Use allowed directories only

---

## Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Author

**gtausa197-svg**
- GitHub: [@gtausa197-svg](https://github.com/gtausa197-svg)

---

## Acknowledgments

- [LM Studio](https://lmstudio.ai/) - Local LLM platform
- [Python](https://www.python.org/) - Programming language
- [psutil](https://github.com/giampaolo/psutil) - System monitoring

---

**Made with ❤️ by gtausa197-svg**
