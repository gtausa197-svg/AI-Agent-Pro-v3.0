import sys

# Read the current file
with open(r'c:\Users\elev-n\Desktop\ai_local_agent\ai_agent.py', 'r', encoding='utf-8') as f:
    current_content = f.read()

#Header to prepend
header = '''# Стандартні бібліотеки Python
import os
import sys
import json
import time
import shlex
import shutil
import socket
import sqlite3
import hashlib
import logging
import mimetypes
import platform
import webbrowser
import subprocess
import re
import requests
import psutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional,Tuple
from collections import defaultdict

# ============================================================================
# РОЗШИРЕНА КОНФІГУРАЦІЯ
# ============================================================================

class Config:
    """Розширена конфігурація агента"""
    # LM Studio API
    LMSTUDIO_API_URL = "http://localhost:1234/v1/chat/completions"
    MODEL_NAME = "openai/gpt-oss-20b"
    
    # Шляхи
    BASE_DIR = Path(__file__).parent
    LOGS_DIR = BASE_DIR / "logs"
    KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"
    CACHE_DIR = BASE_DIR / "cache"
    BACKUP_DIR = BASE_DIR / "backups"
    SCREENSHOTS_DIR = BASE_DIR / "screenshots"
    
    # База даних
    DB_PATH = KNOWLEDGE_BASE_DIR / "agent_memory.db"
    
    # Налаштування логування
    LOG_FILE = LOGS_DIR / f"agent_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Безпека
    ALLOWED_EXTENSIONS = ['.txt', '.json', '.py', '.md', '.csv', '.log', '.xml', '.html', '.css', '.js']
    FORBIDDEN_PATHS = [
        'C:\\\\Windows\\\\System32',
        'C:\\\\Windows\\\\SysWOW64',
        '/system',
        '/sys',
        '/proc',
        'C:\\\\Program Files\\\\WindowsApps'
    ]
    
    # Обмеження
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 МБ
    MAX_SEARCH_RESULTS = 100
    MAX_HISTORY_MESSAGES = 50
    
    # Автоматизація
    SCHEDULE_CHECK_INTERVAL = 60  # секунд
    AUTO_CLEANUP_DAYS = 30

# ============================================================================
# НАЛАШТУВАННЯ ЛОГУВАННЯ
# ============================================================================

'''

# Write the fixed file
with open(r'c:\Users\elev-n\Desktop\ai_local_agent\ai_agent.py', 'w', encoding='utf-8') as f:
    f.write(header + current_content)

print("✅ File header fixed successfully!")
