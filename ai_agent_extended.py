"""
Локальний AI-агент для керування ПК через LM Studio
Версія: 3.0 - МАКСИМАЛЬНО РОЗШИРЕНА
Автор: AI Assistant
"""

import os
import sys
import json
import subprocess
import psutil
import requests
import webbrowser
import platform
import logging
import shutil
import threading
import time
import re
import hashlib
import sqlite3
import mimetypes
import socket
import urllib.parse
import shlex
import zipfile
import tarfile
import base64
import secrets
import string
import smtplib
import winreg
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
from collections import defaultdict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Додаткові бібліотеки (встановіть при потребі)
try:
    from PIL import ImageGrab, Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except ImportError:
    PYPERCLIP_AVAILABLE = False

try:
    from plyer import notification as plyer_notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False

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
    RECORDINGS_DIR = BASE_DIR / "recordings"
    ARCHIVES_DIR = BASE_DIR / "archives"
    TEMP_DIR = BASE_DIR / "temp"
    
    # База даних
    DB_PATH = KNOWLEDGE_BASE_DIR / "agent_memory.db"
    
    # Налаштування логування
    LOG_FILE = LOGS_DIR / f"agent_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Безпека
    ALLOWED_EXTENSIONS = ['.txt', '.json', '.py', '.md', '.csv', '.log', '.xml', '.html', '.css', '.js']
    FORBIDDEN_PATHS = [
        'C:\\Windows\\System32',
        'C:\\Windows\\SysWOW64',
        '/system',
        '/sys',
        '/proc',
        'C:\\Program Files\\WindowsApps'
    ]
    
    # Обмеження
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 МБ
    MAX_SEARCH_RESULTS = 100
    MAX_HISTORY_MESSAGES = 50
    
    # Автоматизація
    SCHEDULE_CHECK_INTERVAL = 60  # секунд
    AUTO_CLEANUP_DAYS = 30
    
    # Моніторинг
    CPU_ALERT_THRESHOLD = 90  # %
    MEMORY_ALERT_THRESHOLD = 85  # %
    DISK_ALERT_THRESHOLD = 90  # %

# ============================================================================
# НАЛАШТУВАННЯ ЛОГУВАННЯ
# ============================================================================

def cleanup_old_logs(directory: Path, days: int):
    """Видалення старих логів"""
    try:
        cutoff = datetime.now() - timedelta(days=days)
        for log_file in directory.glob("*.log"):
            if datetime.fromtimestamp(log_file.stat().st_mtime) < cutoff:
                log_file.unlink()
                logging.info(f"Видалено старий лог: {log_file}")
    except Exception as e:
        logging.error(f"Помилка очищення логів: {str(e)}")


def setup_logging():
    """Розширене налаштування логування"""
    Config.LOGS_DIR.mkdir(exist_ok=True)
    Config.CACHE_DIR.mkdir(exist_ok=True)
    Config.BACKUP_DIR.mkdir(exist_ok=True)
    Config.SCREENSHOTS_DIR.mkdir(exist_ok=True)
    Config.RECORDINGS_DIR.mkdir(exist_ok=True)
    Config.ARCHIVES_DIR.mkdir(exist_ok=True)
    Config.TEMP_DIR.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(Config.LOG_FILE, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Ротація логів (видалення старих)
    cleanup_old_logs(Config.LOGS_DIR, days=30)

# ============================================================================
# БАЗА ДАНИХ ДЛЯ ПАМ'ЯТІ АГЕНТА
# ============================================================================

class AgentDatabase:
    """База даних для збереження пам'яті та контексту агента"""
    
    def __init__(self):
        Config.KNOWLEDGE_BASE_DIR.mkdir(exist_ok=True)
        self.conn = sqlite3.connect(Config.DB_PATH, check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        """Створення таблиць бази даних"""
        cursor = self.conn.cursor()
        
        # Таблиця історії команд
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS command_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                command TEXT NOT NULL,
                result TEXT,
                success BOOLEAN,
                execution_time REAL
            )
        ''')
        
        # Таблиця файлового індексу
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_index (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filepath TEXT UNIQUE NOT NULL,
                filename TEXT NOT NULL,
                extension TEXT,
                size INTEGER,
                modified_date DATETIME,
                hash TEXT,
                tags TEXT,
                indexed_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблиця налаштувань користувача (пам'ять)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблиця запланованих завдань
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scheduled_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_name TEXT NOT NULL,
                command TEXT NOT NULL,
                schedule_time TEXT,
                schedule_type TEXT,
                enabled BOOLEAN DEFAULT 1,
                last_run DATETIME,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблиця контекстної пам'яті
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS context_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                context_type TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                importance INTEGER DEFAULT 5
            )
        ''')
        
        # Таблиця моніторингу
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_monitoring (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                cpu_percent REAL,
                memory_percent REAL,
                disk_percent REAL,
                network_sent INTEGER,
                network_received INTEGER
            )
        ''')
        
        self.conn.commit()
    
    def log_command(self, command: str, result: str, success: bool, execution_time: float):
        """Логування виконаної команди"""
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO command_history (command, result, success, execution_time) VALUES (?, ?, ?, ?)',
            (command, result, success, execution_time)
        )
        self.conn.commit()
    
    def get_command_history(self, limit: int = 20) -> List[Dict]:
        """Отримання історії команд"""
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT timestamp, command, success FROM command_history ORDER BY timestamp DESC LIMIT ?',
            (limit,)
        )
        return [{"timestamp": row[0], "command": row[1], "success": bool(row[2])} for row in cursor.fetchall()]
    
    def add_to_file_index(self, filepath: str, metadata: Dict):
        """Додавання файлу до індексу"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO file_index (filepath, filename, extension, size, modified_date, hash, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            filepath,
            metadata.get('filename'),
            metadata.get('extension'),
            metadata.get('size'),
            metadata.get('modified_date'),
            metadata.get('hash'),
            metadata.get('tags')
        ))
        self.conn.commit()
    
    def search_file_index(self, query: str) -> List[Dict]:
        """Пошук у файловому індексі"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT filepath, filename, size, modified_date, tags 
            FROM file_index 
            WHERE filename LIKE ? OR tags LIKE ?
            ORDER BY modified_date DESC
            LIMIT 50
        ''', (f'%{query}%', f'%{query}%'))
        
        return [
            {
                "filepath": row[0],
                "filename": row[1],
                "size": row[2],
                "modified_date": row[3],
                "tags": row[4]
            }
            for row in cursor.fetchall()
        ]
    
    def save_preference(self, key: str, value: str):
        """Збереження налаштування користувача (пам'ять)"""
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT OR REPLACE INTO user_preferences (key, value) VALUES (?, ?)',
            (key, value)
        )
        self.conn.commit()
    
    def get_preference(self, key: str) -> Optional[str]:
        """Отримання налаштування"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT value FROM user_preferences WHERE key = ?', (key,))
        result = cursor.fetchone()
        return result[0] if result else None
    
    def delete_preference(self, key: str):
        """Видалення налаштування"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM user_preferences WHERE key = ?', (key,))
        self.conn.commit()
    
    def get_all_preferences(self) -> Dict[str, str]:
        """Отримати всі налаштування (пам'ять)"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT key, value FROM user_preferences')
        return {row[0]: row[1] for row in cursor.fetchall()}
    
    def add_context_memory(self, context_type: str, content: str, metadata: Dict = None, importance: int = 5):
        """Додавання до контекстної пам'яті"""
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO context_memory (context_type, content, metadata, importance) VALUES (?, ?, ?, ?)',
            (context_type, content, json.dumps(metadata) if metadata else None, importance)
        )
        self.conn.commit()
    
    def get_relevant_context(self, context_type: str = None, limit: int = 10) -> List[Dict]:
        """Отримання релевантного контексту"""
        cursor = self.conn.cursor()
        if context_type:
            cursor.execute('''
                SELECT context_type, content, metadata, created_date 
                FROM context_memory 
                WHERE context_type = ?
                ORDER BY importance DESC, created_date DESC 
                LIMIT ?
            ''', (context_type, limit))
        else:
            cursor.execute('''
                SELECT context_type, content, metadata, created_date 
                FROM context_memory 
                ORDER BY importance DESC, created_date DESC 
                LIMIT ?
            ''', (limit,))
        
        return [
            {
                "type": row[0],
                "content": row[1],
                "metadata": json.loads(row[2]) if row[2] else {},
                "date": row[3]
            }
            for row in cursor.fetchall()
        ]
    
    def add_scheduled_task(self, task_name: str, command: str, schedule_time: str, schedule_type: str):
        """Додавання запланованого завдання"""
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO scheduled_tasks (task_name, command, schedule_time, schedule_type) VALUES (?, ?, ?, ?)',
            (task_name, command, schedule_time, schedule_type)
        )
        self.conn.commit()
    
    def get_scheduled_tasks(self) -> List[Dict]:
        """Отримання всіх запланованих завдань"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, task_name, command, schedule_time, schedule_type, enabled FROM scheduled_tasks WHERE enabled = 1')
        return [
            {
                "id": row[0],
                "task_name": row[1],
                "command": row[2],
                "schedule_time": row[3],
                "schedule_type": row[4],
                "enabled": bool(row[5])
            }
            for row in cursor.fetchall()
        ]
    
    def log_system_monitoring(self, cpu: float, memory: float, disk: float, net_sent: int, net_recv: int):
        """Логування системного моніторингу"""
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO system_monitoring (cpu_percent, memory_percent, disk_percent, network_sent, network_received) VALUES (?, ?, ?, ?, ?)',
            (cpu, memory, disk, net_sent, net_recv)
        )
        self.conn.commit()

# ============================================================================
# РОЗШИРЕНИЙ КЛІЄНТ LM STUDIO
# ============================================================================

class LMStudioClient:
    """Розширений клієнт для роботи з LM Studio"""
    
    def __init__(self, api_url: str = Config.LMSTUDIO_API_URL, db: AgentDatabase = None):
        self.api_url = api_url
        self.conversation_history: List[Dict[str, str]] = []
        self.db = db
        self.system_context = self.build_system_context()
    
    def build_system_context(self) -> str:
        """Побудова розширеного системного контексту"""
        context = f"""Ти — розумний локальний AI-асистент для керування комп'ютером під назвою "AIAgent Pro v3.0".
Поточна дата та час: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Операційна система: {platform.system()} {platform.release()}

🎯 ТВОЇ МОЖЛИВОСТІ:

📁 ФАЙЛОВА СИСТЕМА:
- read_file, search_files, open_file, copy_file, move_file, delete_file
- create_folder, list_directory, file_info, search_in_files
- get_file_hash, find_large_files, find_duplicates, analyze_folder, index_directory
- find_old_files <шлях> <дні> - знайти старі файли

💻 ПРОГРАМИ ТА ПРОЦЕСИ:
- list_programs, launch_program, close_program, list_processes
- process_info, kill_process, kill_frozen_apps

🖥️ СИСТЕМНИЙ МОНІТОРИНГ:
- system_info, cpu_info, memory_info, disk_info, network_info, battery_info
- monitor_performance, optimize_memory, system_report

🌐 ІНТЕРНЕТ ТА МЕРЕЖА:
- check_internet, download_file, open_webpage, ping, get_ip_info
- list_network_connections, speedtest, check_website_status <url>
- monitor_url <url> - моніторинг змін на сайті

💾 ПАМ'ЯТЬ ТА КОНТЕКСТ:
- remember, recall, forget, show_memory, command_history

🔧 УТИЛІТИ:
- calculator, generate_password, hash_text, current_time
- encrypt_file <шлях> <пароль>, decrypt_file <шлях> <пароль>
- secure_delete <шлях> - безпечне видалення

📦 АРХІВИ:
- compress_archive <джерела...> <архів.zip>
- extract_archive <архів> <призначення>

🎨 МУЛЬТИМЕДІА:
- take_screenshot [назва], record_screen <тривалість_сек>
- compress_image <шлях> [якість]

🔔 ПОВІДОМЛЕННЯ:
- send_notification <заголовок> <текст>
- send_email <кому> <тема> <текст>

🤖 АВТОМАТИЗАЦІЯ:
- schedule_task <назва> <команда> <час> <тип>
- auto_cleanup - очищення системи
- backup_files <джерело> <призначення>
- watch_directory <шлях> - моніторинг папки

📋 БУФЕР ОБМІНУ:
- clipboard_get, clipboard_set <текст>

🔍 АНАЛІТИКА:
- log_analyzer [шлях_до_логу]
- usage_statistics, error_report

📚 ДОВІДКА:
- help [команда], about, exit

🎯 ПРАВИЛА РОБОТИ:
1. Завжди відповідай українською мовою.
2. Будь ввічливим, корисним та зрозумілим.
3. Якщо команда небезпечна - попереджай користувача.
4. Пояснюй результати виконання команд зрозумілою мовою.
5. Використовуй контекст з попередніх команд.
6. Запам'ятовуй важливі деталі про користувача та його систему.

⚡ ВАЖЛИВО: ВИКОНАННЯ КОМАНД
Щоб виконати команду, використовуй спеціальний формат:
to=browser.<команда> <|message|>{{JSON_аргументи}}
або
to=functions.<команда> <|message|>{{JSON_аргументи}}

Приклади:
- Відкрити сайт: to=browser.open_webpage <|message|>{{"url": "https://google.com"}}
- Запустити калькулятор: to=functions.calculator <|message|>{{"expression": "2 + 2 * 2"}}
- Пошук файлів: to=functions.search_files <|message|>{{"directory": "C:/Users", "pattern": "*.txt"}}

Завжди використовуй цей формат для виконання дій!
"""
        return context
    
    def send_message(self, user_message: str, include_context: bool = True) -> str:
        """Відправка повідомлення в LM Studio з контекстом"""
        try:
            messages = [{"role": "system", "content": self.system_context}]
            
            # Додаємо релевантний контекст з БД
            if include_context and self.db:
                recent_context = self.db.get_relevant_context(limit=5)
                if recent_context:
                    context_summary = "\\n".join([f"- {ctx['content']}" for ctx in recent_context])
                    messages.append({
                        "role": "system",
                        "content": f"Релевантний контекст:\\n{context_summary}"
                    })
            
            # Історія розмови
            messages.extend(self.conversation_history[-Config.MAX_HISTORY_MESSAGES:])
            messages.append({"role": "user", "content": user_message})
            
            response = requests.post(
                self.api_url,
                json={
                    "model": Config.MODEL_NAME,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 3000,
                    "stream": False
                },
                timeout=90
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content']
                
                # Зберігаємо в історію
                self.conversation_history.append({"role": "user", "content": user_message})
                self.conversation_history.append({"role": "assistant", "content": ai_response})
                
                # Обмежуємо історію
                if len(self.conversation_history) > Config.MAX_HISTORY_MESSAGES * 2:
                    self.conversation_history = self.conversation_history[-Config.MAX_HISTORY_MESSAGES * 2:]
                
                return ai_response
            else:
                return f"❌ Помилка LM Studio API: {response.status_code} - {response.text}"
                
        except requests.exceptions.ConnectionError:
            return "❌ Не вдалося підключитися до LM Studio. Переконайтеся, що сервер запущений на http://localhost:1234"
        except Exception as e:
            logging.error(f"Помилка LM Studio: {str(e)}")
            return f"❌ Помилка: {str(e)}"
    
    def clear_history(self):
        """Очищення історії"""
        self.conversation_history = []

# ============================================================================
# РОЗШИРЕНИЙ МЕНЕДЖЕР ФАЙЛОВОЇ СИСТЕМИ
# ============================================================================

class AdvancedFileSystemManager:
    """Розширене керування файловою системою"""
    
    def __init__(self, db: AgentDatabase):
        self.db = db
    
    @staticmethod
    def is_safe_path(path: str) -> bool:
        """Перевірка безпеки шляху"""
        abs_path = os.path.abspath(path)
        for forbidden in Config.FORBIDDEN_PATHS:
            if abs_path.startswith(os.path.abspath(forbidden)):
                return False
        return True
    
    def read_file(self, filepath: str) -> Dict[str, Any]:
        """Читання файлу"""
        try:
            if not self.is_safe_path(filepath):
                return {"success": False, "error": "❌ Доступ заборонено"}
            
            if not os.path.exists(filepath):
                return {"success": False, "error": "❌ Файл не існує"}
            
            file_size = os.path.getsize(filepath)
            if file_size > Config.MAX_FILE_SIZE:
                return {"success": False, "error": f"❌ Файл занадто великий ({file_size / 1024 / 1024:.2f} МБ)"}
            
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            self.db.add_context_memory("file_access", f"Прочитано: {filepath}", {"size": file_size})
            return {"success": True, "content": content, "size": file_size}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def search_files(self, directory: str, pattern: str = "*", extension: str = None, 
                     recursive: bool = True, max_results: int = None) -> Dict[str, Any]:
        """Розширений пошук файлів"""
        try:
            if not self.is_safe_path(directory):
                return {"success": False, "error": "❌ Доступ заборонено"}
            
            if not os.path.exists(directory):
                return {"success": False, "error": "❌ Директорія не існує"}
            
            found_files = []
            path_obj = Path(directory)
            max_results = max_results or Config.MAX_SEARCH_RESULTS
            
            if extension:
                search_pattern = f"**/*{extension}"
            else:
                search_pattern = f"**/{pattern}"
            
            method = path_obj.rglob if recursive else path_obj.glob
            
            for file in method(search_pattern if extension else pattern):
                if file.is_file() and len(found_files) < max_results:
                    stat = file.stat()
                    found_files.append({
                        "name": file.name,
                        "path": str(file),
                        "size": stat.st_size,
                        "size_mb": f"{stat.st_size / 1024 / 1024:.2f} MB",
                        "modified": datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                        "extension": file.suffix
                    })
            
            return {"success": True, "files": found_files, "count": len(found_files)}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def find_old_files(self, directory: str, days: int = 365) -> Dict[str, Any]:
        """Пошук старих файлів"""
        try:
            if not self.is_safe_path(directory):
                return {"success": False, "error": "❌ Доступ заборонено"}
            if not os.path.isdir(directory):
                return {"success": False, "error": "❌ Директорія не існує"}
            
            cutoff_date = datetime.now() - timedelta(days=days)
            old_files = []
            
            for file in Path(directory).rglob('*'):
                if file.is_file():
                    try:
                        mtime = datetime.fromtimestamp(file.stat().st_mtime)
                        if mtime < cutoff_date:
                            old_files.append({
                                "path": str(file),
                                "modified": mtime.strftime('%Y-%m-%d %H:%M:%S'),
                                "size_mb": f"{file.stat().st_size / 1024 / 1024:.2f} MB"
                            })
                    except Exception:
                        pass
            
            return {"success": True, "files": old_files, "count": len(old_files)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def secure_delete(self, filepath: str, passes: int = 3) -> Dict[str, Any]:
        """Безпечне видалення файлу з перезаписом"""
        try:
            if not self.is_safe_path(filepath):
                return {"success": False, "error": "❌ Доступ заборонено"}
            if not os.path.isfile(filepath):
                return {"success": False, "error": "❌ Файл не існує"}
            
            file_size = os.path.getsize(filepath)
            
            # Перезаписування випадковими даними
            with open(filepath, 'ba+', buffering=0) as f:
                for _ in range(passes):
                    f.seek(0)
                    f.write(os.urandom(file_size))
            
            # Видалення файлу
            os.remove(filepath)
            
            return {"success": True, "message": f"✅ Файл безпечно видалено ({passes} проходів)"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def compress_archive(self, source_paths: List[str], archive_path: str) -> Dict[str, Any]:
        """Створення архіву"""
        try:
            if archive_path.endswith('.zip'):
                with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for source in source_paths:
                        if os.path.isfile(source):
                            zipf.write(source, os.path.basename(source))
                        elif os.path.isdir(source):
                            for root, dirs, files in os.walk(source):
                                for file in files:
                                    file_path = os.path.join(root, file)
                                    arcname = os.path.relpath(file_path, os.path.dirname(source))
                                    zipf.write(file_path, arcname)
            elif archive_path.endswith(('.tar.gz', '.tgz')):
                with tarfile.open(archive_path, 'w:gz') as tar:
                    for source in source_paths:
                        tar.add(source, arcname=os.path.basename(source))
            else:
                return {"success": False, "error": "❌ Підтримуються тільки .zip та .tar.gz архіви"}
            
            return {"success": True, "message": f"✅ Архів створено: {archive_path}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def extract_archive(self, archive_path: str, destination: str) -> Dict[str, Any]:
        """Розпакування архіву"""
        try:
            if not os.path.exists(archive_path):
                return {"success": False, "error": "❌ Архів не існує"}
            
            os.makedirs(destination, exist_ok=True)
            
            if archive_path.endswith('.zip'):
                with zipfile.ZipFile(archive_path, 'r') as zipf:
                    zipf.extractall(destination)
            elif archive_path.endswith(('.tar.gz', '.tgz', '.tar')):
                with tarfile.open(archive_path, 'r:*') as tar:
                    tar.extractall(destination)
            else:
                return {"success": False, "error": "❌ Непідтримуваний формат архіву"}
            
            return {"success": True, "message": f"✅ Архів розпаковано в: {destination}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def encrypt_file(self, filepath: str, password: str) -> Dict[str, Any]:
        """Проста XOR-шифрування файлу"""
        try:
            if not self.is_safe_path(filepath):
                return {"success": False, "error": "❌ Доступ заборонено"}
            if not os.path.isfile(filepath):
                return {"success": False, "error": "❌ Файл не існує"}
            
            with open(filepath, 'rb') as f:
                data = f.read()
            
            # XOR шифрування
            key = hashlib.sha256(password.encode()).digest()
            encrypted = bytes([data[i] ^ key[i % len(key)] for i in range(len(data))])
            
            encrypted_path = filepath + '.encrypted'
            with open(encrypted_path, 'wb') as f:
                f.write(encrypted)
            
            return {"success": True, "message": f"✅ Файл зашифровано: {encrypted_path}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def decrypt_file(self, filepath: str, password: str) -> Dict[str, Any]:
        """Розшифрування файлу"""
        try:
            if not os.path.isfile(filepath):
                return {"success": False, "error": "❌ Файл не існує"}
            
            with open(filepath, 'rb') as f:
                encrypted = f.read()
            
            # XOR розшифрування
            key = hashlib.sha256(password.encode()).digest()
            decrypted = bytes([encrypted[i] ^ key[i % len(key)] for i in range(len(encrypted))])
            
            decrypted_path = filepath.replace('.encrypted', '.decrypted')
            with open(decrypted_path, 'wb') as f:
                f.write(decrypted)
            
            return {"success": True, "message": f"✅ Файл розшифровано: {decrypted_path}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

# Продовження в наступній частині коду...
# (Через обмеження розміру, я створю окремий файл для решти класів)

