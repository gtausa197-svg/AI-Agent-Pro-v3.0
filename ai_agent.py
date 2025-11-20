# Стандартні бібліотеки Python
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
        context = f"""Ти — розумний локальний AI-асистент для керування комп'ютером під назвою "AIAgent Pro".
Поточна дата та час: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Операційна система: {platform.system()} {platform.release()}

🎯 ТВОЇ МОЖЛИВОСТІ:

📁 ФАЙЛОВА СИСТЕМА:
- read_file <шлях> - прочитати вміст файлу
- search_files <директорія> [розширення] - пошук файлів
- open_file <шлях> - відкрити файл у програмі
- copy_file <джерело> <призначення> - копіювати файл
- move_file <джерело> <призначення> - перемістити файл
- delete_file <шлях> - видалити файл (з підтвердженням)
- create_folder <шлях> - створити папку
- list_directory <шлях> - показати вміст директорії
- file_info <шлях> - детальна інформація про файл
- search_in_files <директорія> <текст> - пошук тексту у файлах
- get_file_hash <шлях> - отримати хеш файлу
- find_large_files <шлях> [розмір_МБ] - знайти великі файли
- find_duplicates <шлях> - знайти дублікати файлів
- analyze_folder <шлях> - аналіз вмісту папки
- index_directory <шлях> - індексація папки

💻 ПРОГРАМИ ТА ПРОЦЕСИ:
- list_programs - список встановлених програм
- launch_program <шлях або назва> - запустити програму
- close_program <назва процесу> - закрити програму
- list_processes [cpu|memory] [limit] - показати процеси
- process_info <pid або назва> - інформація про процес
- kill_process <pid> - примусово завершити процес

🖥️ СИСТЕМНИЙ МОНІТОРИНГ:
- system_info - повна інформація про систему
- cpu_info - детальна інформація про CPU
- memory_info - інформація про RAM
- disk_info - інформація про диски
- network_info - мережева інформація
- battery_info - стан батареї (для ноутбуків)
- list_processes - список процесів

🌐 ІНТЕРНЕТ ТА МЕРЕЖА:
- check_internet - перевірити з'єднання
- download_file <url> <шлях> - завантажити файл
- open_webpage <url> - відкрити сайт
- ping <хост> [count] - перевірити доступність хосту
- get_ip_info - інформація про IP-адресу
- list_network_connections - активні з'єднання

💾 ПАМ'ЯТЬ ТА КОНТЕКСТ:
- remember <ключ> <значення> - запам'ятати інформацію
- recall <ключ> - згадати інформацію
- forget <ключ> - забути інформацію
- show_memory - показати збережену пам'ять
- command_history [кількість] - історія команд
- index_directory <шлях> - проіндексувати директорію

🔧 УТИЛІТИ:
- calculator <вираз> - калькулятор
- generate_password [довжина] - генерація пароля
- hash_text <текст> [алгоритм] - хешування тексту
- current_time - поточний час

🧠 АНАЛІЗ ТА ДОПОМОГА:
- analyze_code <код> - аналіз програмного коду
- explain_error <помилка> - пояснення технічних помилок
- suggest_optimization <код> - пропозиції щодо оптимізації

📚 ДОВІДКА:
- help [команда] - допомога по командах
- about - інформація про агента
- exit - вихід з програми

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
                # Напр. ".txt"
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
    
    def open_file(self, filepath: str) -> Dict[str, Any]:
        """Відкрити файл стандартною програмою"""
        try:
            if not self.is_safe_path(filepath):
                return {"success": False, "error": "❌ Доступ заборонено"}
            if not os.path.exists(filepath):
                return {"success": False, "error": "❌ Файл не існує"}
            
            system = platform.system()
            if system == "Windows":
                os.startfile(filepath)  # type: ignore
            elif system == "Darwin":
                subprocess.Popen(["open", filepath])
            else:
                subprocess.Popen(["xdg-open", filepath])
            
            self.db.add_context_memory("file_open", f"Відкрито файл: {filepath}")
            return {"success": True, "message": f"✅ Файл відкрито: {filepath}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def copy_file(self, source: str, destination: str) -> Dict[str, Any]:
        """Копіювання файлу"""
        try:
            if not self.is_safe_path(source) or not self.is_safe_path(destination):
                return {"success": False, "error": "❌ Доступ заборонено"}
            
            shutil.copy2(source, destination)
            self.db.add_context_memory("file_operation", f"Скопійовано: {source} -> {destination}")
            return {"success": True, "message": f"✅ Файл скопійовано: {destination}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def move_file(self, source: str, destination: str) -> Dict[str, Any]:
        """Переміщення файлу"""
        try:
            if not self.is_safe_path(source) or not self.is_safe_path(destination):
                return {"success": False, "error": "❌ Доступ заборонено"}
            
            shutil.move(source, destination)
            self.db.add_context_memory("file_operation", f"Переміщено: {source} -> {destination}")
            return {"success": True, "message": f"✅ Файл переміщено: {destination}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_file(self, filepath: str) -> Dict[str, Any]:
        """Видалення файлу або папки"""
        try:
            if not self.is_safe_path(filepath):
                return {"success": False, "error": "❌ Доступ заборонено"}
            
            if os.path.isfile(filepath):
                os.remove(filepath)
            elif os.path.isdir(filepath):
                shutil.rmtree(filepath)
            else:
                return {"success": False, "error": "❌ Файл або папка не існує"}
            
            self.db.add_context_memory("file_operation", f"Видалено: {filepath}", importance=7)
            return {"success": True, "message": f"✅ Видалено: {filepath}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_folder(self, path: str) -> Dict[str, Any]:
        """Створення папки"""
        try:
            if not self.is_safe_path(path):
                return {"success": False, "error": "❌ Доступ заборонено"}
            
            Path(path).mkdir(parents=True, exist_ok=True)
            return {"success": True, "message": f"✅ Папку створено: {path}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_directory(self, path: str) -> Dict[str, Any]:
        """Вміст директорії"""
        try:
            if not self.is_safe_path(path):
                return {"success": False, "error": "❌ Доступ заборонено"}
            
            if not os.path.isdir(path):
                return {"success": False, "error": "❌ Директорія не існує"}
            
            items = []
            for item in Path(path).iterdir():
                stat = item.stat()
                items.append({
                    "name": item.name,
                    "type": "folder" if item.is_dir() else "file",
                    "size": stat.st_size if item.is_file() else 0,
                    "modified": datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                })
            
            return {"success": True, "items": items, "count": len(items)}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def file_info(self, filepath: str) -> Dict[str, Any]:
        """Детальна інформація про файл"""
        try:
            if not os.path.exists(filepath):
                return {"success": False, "error": "❌ Файл не існує"}
            
            stat = os.stat(filepath)
            path_obj = Path(filepath)
            
            info = {
                "name": path_obj.name,
                "path": str(path_obj.absolute()),
                "size": stat.st_size,
                "size_formatted": f"{stat.st_size / 1024 / 1024:.2f} MB",
                "created": datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                "modified": datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                "accessed": datetime.fromtimestamp(stat.st_atime).strftime('%Y-%m-%d %H:%M:%S'),
                "extension": path_obj.suffix,
                "mime_type": mimetypes.guess_type(filepath)[0],
                "is_file": path_obj.is_file(),
                "is_directory": path_obj.is_dir()
            }
            
            return {"success": True, "info": info}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def search_in_files(self, directory: str, search_text: str, extensions: List[str] = None) -> Dict[str, Any]:
        """Пошук тексту у файлах"""
        try:
            if not self.is_safe_path(directory):
                return {"success": False, "error": "❌ Доступ заборонено"}
            
            if not os.path.isdir(directory):
                return {"success": False, "error": "❌ Директорія не існує"}
            
            extensions = extensions or ['.txt', '.py', '.md', '.json', '.log', '.csv']
            search_text_lower = search_text.lower()
            results = []
            
            for file in Path(directory).rglob('*'):
                if not file.is_file():
                    continue
                if file.suffix and extensions and file.suffix.lower() not in [e.lower() for e in extensions]:
                    continue
                
                try:
                    with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_num, line in enumerate(f, start=1):
                            if search_text_lower in line.lower():
                                results.append({
                                    "file": str(file),
                                    "line_number": line_num,
                                    "line": line.strip()
                                })
                                if len(results) >= Config.MAX_SEARCH_RESULTS:
                                    break
                except Exception:
                    continue
            
            return {
                "success": True,
                "matches": results,
                "count": len(results),
                "search_text": search_text
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_file_hash(self, filepath: str, algorithm: str = 'sha256') -> Dict[str, Any]:
        """Отримати хеш файлу"""
        try:
            if not self.is_safe_path(filepath):
                return {"success": False, "error": "❌ Доступ заборонено"}
            if not os.path.isfile(filepath):
                return {"success": False, "error": "❌ Файл не існує"}
            
            h = hashlib.new(algorithm)
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    if not chunk:
                        break
                    h.update(chunk)
            
            return {
                "success": True,
                "file": filepath,
                "algorithm": algorithm,
                "hash": h.hexdigest()
            }
        except ValueError:
            return {"success": False, "error": "❌ Непідтримуваний алгоритм хешування"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def find_large_files(self, directory: str, min_size_mb: int = 100) -> Dict[str, Any]:
        """Пошук великих файлів"""
        try:
            if not self.is_safe_path(directory):
                return {"success": False, "error": "❌ Доступ заборонено"}
            if not os.path.isdir(directory):
                return {"success": False, "error": "❌ Директорія не існує"}
            
            min_bytes = min_size_mb * 1024 * 1024
            large_files = []
            
            for file in Path(directory).rglob('*'):
                if file.is_file():
                    try:
                        size = file.stat().st_size
                        if size >= min_bytes:
                            large_files.append({
                                "path": str(file),
                                "size_bytes": size,
                                "size_mb": f"{size / 1024 / 1024:.2f} MB"
                            })
                    except Exception:
                        pass
            
            large_files.sort(key=lambda x: x['size_bytes'], reverse=True)
            return {
                "success": True,
                "files": large_files[:Config.MAX_SEARCH_RESULTS],
                "count": len(large_files),
                "min_size_mb": min_size_mb
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def find_duplicates(self, directory: str) -> Dict[str, Any]:
        """Пошук дублікатів файлів"""
        try:
            if not self.is_safe_path(directory):
                return {"success": False, "error": "❌ Доступ заборонено"}
            if not os.path.isdir(directory):
                return {"success": False, "error": "❌ Директорія не існує"}
            
            hashes: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
            
            for file in Path(directory).rglob('*'):
                if file.is_file():
                    try:
                        hash_md5 = hashlib.md5()
                        with open(file, 'rb') as f:
                            for chunk in iter(lambda: f.read(4096), b""):
                                if not chunk:
                                    break
                                hash_md5.update(chunk)
                        
                        file_hash = hash_md5.hexdigest()
                        size_bytes = file.stat().st_size
                        hashes[file_hash].append({
                            "path": str(file),
                            "name": file.name,
                            "size_mb": f"{size_bytes / 1024 / 1024:.2f} MB",
                            "size_bytes": size_bytes
                        })
                    except Exception:
                        pass
            
            duplicates = {
                hash_val: files
                for hash_val, files in hashes.items()
                if len(files) > 1
            }
            
            total_duplicate_size = 0
            duplicate_count = 0
            for files in duplicates.values():
                duplicate_count += len(files) - 1
                total_duplicate_size += files[0]['size_bytes'] * (len(files) - 1)
            
            return {
                "success": True,
                "duplicates": duplicates,
                "groups": len(duplicates),
                "duplicate_files_count": duplicate_count,
                "wasted_space_mb": f"{total_duplicate_size / 1024 / 1024:.2f} MB"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def analyze_folder(self, directory: str) -> Dict[str, Any]:
        """Аналіз вмісту папки"""
        try:
            if not self.is_safe_path(directory):
                return {"success": False, "error": "❌ Доступ заборонено"}
            if not os.path.isdir(directory):
                return {"success": False, "error": "❌ Директорія не існує"}
            
            stats = {
                "total_files": 0,
                "total_size": 0,
                "file_types": defaultdict(int),
                "largest_files": []
            }
            
            files_list: List[Tuple[str, int]] = []
            
            for file in Path(directory).rglob('*'):
                if file.is_file():
                    try:
                        size = file.stat().st_size
                        stats["total_files"] += 1
                        stats["total_size"] += size
                        stats["file_types"][file.suffix or "no_extension"] += 1
                        files_list.append((str(file), size))
                    except Exception:
                        pass
            
            files_list.sort(key=lambda x: x[1], reverse=True)
            stats["largest_files"] = [
                {"path": f, "size_mb": f"{s / 1024 / 1024:.2f} MB"} 
                for f, s in files_list[:10]
            ]
            
            stats["total_size_gb"] = f"{stats['total_size'] / 1024 / 1024 / 1024:.2f} GB"
            stats["file_types"] = dict(stats["file_types"])
            
            return {"success": True, "analysis": stats}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def index_directory(self, directory: str) -> Dict[str, Any]:
        """Індексація директорії для швидкого пошуку"""
        try:
            if not self.is_safe_path(directory):
                return {"success": False, "error": "❌ Доступ заборонено"}
            if not os.path.isdir(directory):
                return {"success": False, "error": "❌ Директорія не існує"}
            
            indexed_count = 0
            
            for file in Path(directory).rglob('*'):
                if file.is_file():
                    try:
                        stat = file.stat()
                        file_hash = hashlib.md5(str(file).encode()).hexdigest()
                        
                        metadata = {
                            "filename": file.name,
                            "extension": file.suffix,
                            "size": stat.st_size,
                            "modified_date": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            "hash": file_hash,
                            "tags": f"{file.suffix} {file.name}"
                        }
                        
                        self.db.add_to_file_index(str(file), metadata)
                        indexed_count += 1
                    except Exception:
                        pass
            
            return {"success": True, "indexed_files": indexed_count}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

# ============================================================================
# РОЗШИРЕНИЙ МЕНЕДЖЕР ПРОГРАМ
# ============================================================================

class AdvancedApplicationManager:
    """Розширене керування програмами"""
    
    def __init__(self, db: AgentDatabase):
        self.db = db
    
    def list_programs(self) -> Dict[str, Any]:
        """Список встановлених програм (Windows)"""
        try:
            programs = []
            
            if platform.system() == 'Windows':
                import winreg
                paths = [
                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                    r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
                ]
                
                for path in paths:
                    try:
                        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
                        for i in range(winreg.QueryInfoKey(key)[0]):
                            try:
                                subkey_name = winreg.EnumKey(key, i)
                                subkey = winreg.OpenKey(key, subkey_name)
                                try:
                                    name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                    version = None
                                    try:
                                        version = winreg.QueryValueEx(subkey, "DisplayVersion")[0]
                                    except Exception:
                                        pass
                                    programs.append({"name": name, "version": version})
                                except Exception:
                                    pass
                            except Exception:
                                pass
                    except Exception:
                        pass
            
            return {"success": True, "programs": sorted(programs, key=lambda x: x['name'])}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def launch_program(self, program_path: str) -> Dict[str, Any]:
        """Запуск програми"""
        try:
            process = subprocess.Popen(program_path, shell=True)
            self.db.add_context_memory("program_launch", f"Запущено: {program_path}", importance=6)
            return {"success": True, "message": f"✅ Програму запущено: {program_path}", "pid": process.pid}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def close_program(self, process_name: str) -> Dict[str, Any]:
        """Закриття програми за назвою процесу"""
        try:
            terminated = []
            for proc in psutil.process_iter(['name', 'pid']):
                name = proc.info['name'] or ""
                if process_name.lower() in name.lower():
                    try:
                        proc.terminate()
                        terminated.append(f"{name} (PID: {proc.info['pid']})")
                    except Exception:
                        pass
            
            if terminated:
                self.db.add_context_memory("program_close", f"Закрито: {', '.join(terminated)}", importance=7)
                return {"success": True, "terminated": terminated, "count": len(terminated)}
            else:
                return {"success": False, "error": "❌ Процес не знайдено"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def process_info(self, identifier: str) -> Dict[str, Any]:
        """Інформація про процес (за PID або назвою)"""
        try:
            proc = None
            try:
                pid = int(identifier)
                proc = psutil.Process(pid)
            except ValueError:
                for p in psutil.process_iter(['name', 'pid']):
                    name = p.info['name'] or ""
                    if identifier.lower() in name.lower():
                        proc = psutil.Process(p.info['pid'])
                        break
            
            if proc is None:
                return {"success": False, "error": "❌ Процес не знайдено"}
            
            info = {
                "name": proc.name(),
                "pid": proc.pid,
                "status": proc.status(),
                "cpu_percent": f"{proc.cpu_percent(interval=0.1)}%",
                "memory_mb": f"{proc.memory_info().rss / 1024 / 1024:.2f} MB",
                "memory_percent": f"{proc.memory_percent():.2f}%",
                "num_threads": proc.num_threads(),
                "create_time": datetime.fromtimestamp(proc.create_time()).strftime('%Y-%m-%d %H:%M:%S')
            }
            
            try:
                info["exe"] = proc.exe()
                info["cwd"] = proc.cwd()
            except Exception:
                pass
            
            return {"success": True, "info": info}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def kill_process(self, pid: int) -> Dict[str, Any]:
        """Примусове завершення процесу за PID"""
        try:
            proc = psutil.Process(pid)
            name = proc.name()
            proc.kill()
            self.db.add_context_memory("process_kill", f"Вбито процес: {name} (PID: {pid})", importance=8)
            return {"success": True, "message": f"✅ Процес {name} (PID: {pid}) примусово завершено"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

# ============================================================================
# РОЗШИРЕНИЙ СИСТЕМНИЙ МОНІТОР
# ============================================================================

class AdvancedSystemMonitor:
    """Розширений моніторинг системи"""
    
    def get_system_info(self) -> Dict[str, Any]:
        """Повна системна інформація"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            disk = psutil.disk_usage('/')
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            
            info = {
                "system": {
                    "platform": platform.system(),
                    "release": platform.release(),
                    "version": platform.version(),
                    "machine": platform.machine(),
                    "processor": platform.processor(),
                    "boot_time": boot_time.strftime('%Y-%m-%d %H:%M:%S'),
                    "uptime": str(datetime.now() - boot_time).split('.')[0]
                },
                "cpu": {
                    "physical_cores": psutil.cpu_count(logical=False),
                    "total_cores": psutil.cpu_count(logical=True),
                    "max_frequency": f"{psutil.cpu_freq().max:.2f} MHz" if psutil.cpu_freq() else "N/A",
                    "current_frequency": f"{psutil.cpu_freq().current:.2f} MHz" if psutil.cpu_freq() else "N/A",
                    "cpu_usage_per_core": [f"{x}%" for x in cpu_percent],
                    "total_cpu_usage": f"{sum(cpu_percent) / len(cpu_percent):.2f}%"
                },
                "memory": {
                    "total": f"{memory.total / 1024**3:.2f} GB",
                    "available": f"{memory.available / 1024**3:.2f} GB",
                    "used": f"{memory.used / 1024**3:.2f} GB",
                    "percentage": f"{memory.percent}%",
                    "swap_total": f"{swap.total / 1024**3:.2f} GB",
                    "swap_used": f"{swap.used / 1024**3:.2f} GB",
                    "swap_percentage": f"{swap.percent}%"
                },
                "disk": {
                    "total": f"{disk.total / 1024**3:.2f} GB",
                    "used": f"{disk.used / 1024**3:.2f} GB",
                    "free": f"{disk.free / 1024**3:.2f} GB",
                    "percentage": f"{disk.percent}%"
                }
            }
            
            return {"success": True, "info": info}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_battery_info(self) -> Dict[str, Any]:
        """Інформація про батарею"""
        try:
            battery = psutil.sensors_battery()
            if battery:
                info = {
                    "percent": f"{battery.percent}%",
                    "power_plugged": "Підключено" if battery.power_plugged else "Не підключено",
                    "time_left": str(timedelta(seconds=battery.secsleft)) if battery.secsleft not in (psutil.POWER_TIME_UNLIMITED, psutil.POWER_TIME_UNKNOWN) else "Невідомо/∞"
                }
                return {"success": True, "info": info}
            else:
                return {"success": False, "error": "❌ Батарея не виявлена"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_network_info(self) -> Dict[str, Any]:
        """Мережева інформація"""
        try:
            net_io = psutil.net_io_counters()
            addrs = psutil.net_if_addrs()
            
            info = {
                "bytes_sent": f"{net_io.bytes_sent / 1024**2:.2f} MB",
                "bytes_received": f"{net_io.bytes_recv / 1024**2:.2f} MB",
                "packets_sent": net_io.packets_sent,
                "packets_received": net_io.packets_recv,
                "interfaces": {}
            }
            
            for interface, addresses in addrs.items():
                info["interfaces"][interface] = [
                    {"family": str(addr.family), "address": addr.address}
                    for addr in addresses
                ]
            
            return {"success": True, "info": info}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_processes(self, sort_by: str = "cpu", limit: int = 20) -> Dict[str, Any]:
        """Список процесів з сортуванням"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    processes.append({
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "cpu": proc.info['cpu_percent'],
                        "memory": proc.info['memory_percent'],
                        "status": proc.info['status']
                    })
                except Exception:
                    pass
            
            if sort_by == "cpu":
                processes.sort(key=lambda x: x['cpu'], reverse=True)
            elif sort_by == "memory":
                processes.sort(key=lambda x: x['memory'], reverse=True)
            
            return {"success": True, "processes": processes[:limit]}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_disk_info(self) -> Dict[str, Any]:
        """Інформація про всі диски"""
        try:
            disks = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disks.append({
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total": f"{usage.total / 1024**3:.2f} GB",
                        "used": f"{usage.used / 1024**3:.2f} GB",
                        "free": f"{usage.free / 1024**3:.2f} GB",
                        "percentage": f"{usage.percent}%"
                    })
                except Exception:
                    pass
            
            return {"success": True, "disks": disks}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """Скорочена інформація про CPU"""
        base = self.get_system_info()
        if not base.get("success"):
            return base
        return {"success": True, "cpu": base["info"]["cpu"]}
    
    def get_memory_info(self) -> Dict[str, Any]:
        """Скорочена інформація про пам'ять"""
        base = self.get_system_info()
        if not base.get("success"):
            return base
        return {"success": True, "memory": base["info"]["memory"]}

# ============================================================================
# РОЗШИРЕНИЙ МЕРЕЖЕВИЙ МЕНЕДЖЕР
# ============================================================================

class AdvancedNetworkManager:
    """Розширене керування мережею"""
    
    def check_internet(self) -> Dict[str, Any]:
        """Перевірка інтернету"""
        try:
            start_time = time.time()
            response = requests.get("https://www.google.com", timeout=5)
            latency = (time.time() - start_time) * 1000
            
            return {
                "success": True,
                "connected": True,
                "latency_ms": f"{latency:.2f} ms",
                "status_code": response.status_code
            }
        except Exception:
            return {"success": True, "connected": False}
    
    def download_file(self, url: str, save_path: str) -> Dict[str, Any]:
        """Завантаження файлу"""
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if not chunk:
                        continue
                    downloaded += len(chunk)
                    f.write(chunk)
                    if total_size:
                        progress = (downloaded / total_size) * 100
                        print(f"\rЗавантаження: {progress:.1f}%", end='', flush=True)
            
            print()
            return {
                "success": True,
                "message": f"✅ Файл збережено: {save_path}",
                "size": f"{downloaded / 1024 / 1024:.2f} MB"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def ping(self, host: str, count: int = 4) -> Dict[str, Any]:
        """Ping хоста"""
        try:
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            command = ['ping', param, str(count), host]
            result = subprocess.run(command, capture_output=True, text=True, timeout=15)
            
            return {
                "success": True,
                "host": host,
                "output": result.stdout,
                "reachable": result.returncode == 0
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_ip_info(self) -> Dict[str, Any]:
        """Інформація про IP"""
        try:
            hostname = socket.gethostname()
            try:
                local_ip = socket.gethostbyname(hostname)
            except Exception:
                local_ip = "Недоступно"
            
            try:
                external_ip = requests.get('https://api.ipify.org', timeout=5).text
            except Exception:
                external_ip = "Недоступно"
            
            return {
                "success": True,
                "hostname": hostname,
                "local_ip": local_ip,
                "external_ip": external_ip
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_network_connections(self) -> Dict[str, Any]:
        """Список мережевих з'єднань"""
        try:
            connections = []
            for conn in psutil.net_connections(kind='inet'):
                if conn.status == 'ESTABLISHED':
                    connections.append({
                        "local_address": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A",
                        "remote_address": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A",
                        "status": conn.status,
                        "pid": conn.pid
                    })
            
            return {"success": True, "connections": connections[:50], "total": len(connections)}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def open_webpage(self, url: str) -> Dict[str, Any]:
        """Відкрити веб-сторінку"""
        try:
            if not (url.startswith("http://") or url.startswith("https://")):
                url = "http://" + url
            webbrowser.open(url)
            return {"success": True, "message": f"✅ Відкрито сторінку: {url}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

# ============================================================================
# УТИЛІТИ
# ============================================================================

class Utilities:
    """Корисні утиліти"""
    
    @staticmethod
    def calculator(expression: str) -> Dict[str, Any]:
        """Калькулятор"""
        try:
            allowed_chars = set("0123456789+-*/(). ")
            if not all(c in allowed_chars for c in expression):
                return {"success": False, "error": "❌ Недопустимі символи"}
            
            result = eval(expression, {"__builtins__": {}}, {})
            return {"success": True, "result": result}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def generate_password(length: int = 16) -> Dict[str, Any]:
        """Генерація пароля"""
        try:
            import string
            import secrets
            
            if length <= 0:
                return {"success": False, "error": "❌ Довжина має бути > 0"}
            
            alphabet = string.ascii_letters + string.digits + string.punctuation
            password = ''.join(secrets.choice(alphabet) for _ in range(length))
            
            return {"success": True, "password": password}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def hash_text(text: str, algorithm: str = 'sha256') -> Dict[str, Any]:
        """Хешування тексту"""
        try:
            hash_func = hashlib.new(algorithm)
            hash_func.update(text.encode('utf-8'))
            
            return {"success": True, "hash": hash_func.hexdigest(), "algorithm": algorithm}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def current_time() -> Dict[str, Any]:
        """Поточний час"""
        now = datetime.now()
        return {
            "success": True,
            "datetime": now.strftime('%Y-%m-%d %H:%M:%S'),
            "timestamp": int(now.timestamp()),
            "timezone": time.tzname[0] if time.tzname else ""
        }

# ============================================================================
# ГОЛОВНИЙ АГЕНТ
# ============================================================================

class AIAgent:
    """Головний AI-агент"""
    
    def __init__(self):
        self.db = AgentDatabase()
        self.lm_client = LMStudioClient(db=self.db)
        self.fs_manager = AdvancedFileSystemManager(self.db)
        self.app_manager = AdvancedApplicationManager(self.db)
        self.sys_monitor = AdvancedSystemMonitor()
        self.net_manager = AdvancedNetworkManager()
        self.utilities = Utilities()
    
    @staticmethod
    def _json(data: Any) -> str:
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    def handle_direct_command(self, user_input: str) -> Optional[str]:
        """
        Обробка явних команд (read_file, system_info, search_files тощо).
        Повертає:
          - рядок з результатом, якщо команда розпізнана
          - None, якщо команда не розпізнана (тоді йдемо в LLM)
        """
        try:
            parts = shlex.split(user_input, posix=False)
        except ValueError as e:
            return f"❌ Помилка розбору команди: {str(e)}"
        
        if not parts:
            return None
        
        cmd = parts[0].lower()
        args = parts[1:]
        
        # Якщо перше слово не схоже на ім'я команди — вважаємо, що це не команда
        known_commands = {
            "read_file", "search_files", "open_file", "copy_file", "move_file",
            "delete_file", "create_folder", "list_directory", "file_info",
            "search_in_files", "get_file_hash", "find_large_files", "find_duplicates",
            "analyze_folder", "index_directory",
            "list_programs", "launch_program", "close_program",
            "list_processes", "process_info", "kill_process",
            "system_info", "cpu_info", "memory_info", "disk_info",
            "network_info", "battery_info",
            "check_internet", "download_file", "open_webpage", "ping",
            "get_ip_info", "list_network_connections",
            "remember", "recall", "forget", "show_memory", "command_history",
            "calculator", "generate_password", "hash_text", "current_time",
            "help", "about"
        }
        
        if cmd not in known_commands:
            return None
        
        # --- ФАЙЛОВА СИСТЕМА ---
        if cmd == "read_file":
            if not args:
                return "❌ Вкажіть шлях до файлу. Приклад: read_file \"C:\\шлях\\до\\файлу.txt\""
            res = self.fs_manager.read_file(args[0])
            if not res.get("success"):
                return res.get("error", "❌ Помилка")
            content = res.get("content", "")
            max_preview = 5000
            if len(content) > max_preview:
                preview = content[:max_preview] + "\n... (обрізано)"
            else:
                preview = content
            return f"📄 Вміст файлу {args[0]} ({res.get('size', 0)} байт):\n\n{preview}"
        
        if cmd == "search_files":
            if not args:
                return "❌ Вкажіть директорію. Приклад: search_files \"C:\\Папка\" .txt"
            directory = args[0]
            pattern = "*"
            extension = None
            if len(args) >= 2:
                second = args[1]
                if second.startswith("."):
                    extension = second
                else:
                    pattern = second
            res = self.fs_manager.search_files(directory, pattern=pattern, extension=extension)
            if not res.get("success"):
                return res.get("error", "❌ Помилка")
            files = res.get("files", [])
            if not files:
                return "ℹ️ Файлів не знайдено."
            lines = [
                f"- {f['path']} ({f['size_mb']}, змінено {f['modified']})"
                for f in files
            ]
            return f"🔎 Знайдено {res.get('count', 0)} файл(ів):\n" + "\n".join(lines)
        
        if cmd == "open_file":
            if not args:
                return "❌ Вкажіть шлях до файлу. Приклад: open_file \"C:\\шлях\\файл.pdf\""
            res = self.fs_manager.open_file(args[0])
            return res.get("message") if res.get("success") else res.get("error", "❌ Помилка")
        
        if cmd == "copy_file":
            if len(args) < 2:
                return "❌ Вкажіть джерело та призначення. Приклад: copy_file source.txt dest.txt"
            res = self.fs_manager.copy_file(args[0], args[1])
            return res.get("message") if res.get("success") else res.get("error", "❌ Помилка")
        
        if cmd == "move_file":
            if len(args) < 2:
                return "❌ Вкажіть джерело та призначення. Приклад: move_file source.txt dest.txt"
            res = self.fs_manager.move_file(args[0], args[1])
            return res.get("message") if res.get("success") else res.get("error", "❌ Помилка")
        
        if cmd == "delete_file":
            if not args:
                return "❌ Вкажіть шлях до файлу/папки. Приклад: delete_file \"C:\\шлях\\до\\файлу.txt\""
            res = self.fs_manager.delete_file(args[0])
            return res.get("message") if res.get("success") else res.get("error", "❌ Помилка")
        
        if cmd == "create_folder":
            if not args:
                return "❌ Вкажіть шлях до папки. Приклад: create_folder \"C:\\НоваПапка\""
            res = self.fs_manager.create_folder(args[0])
            return res.get("message") if res.get("success") else res.get("error", "❌ Помилка")
        
        if cmd == "list_directory":
            if not args:
                return "❌ Вкажіть директорію. Приклад: list_directory \"C:\\Папка\""
            res = self.fs_manager.list_directory(args[0])
            if not res.get("success"):
                return res.get("error", "❌ Помилка")
            items = res.get("items", [])
            if not items:
                return "ℹ️ Папка порожня."
            lines = [
                f"[{'DIR' if i['type']=='folder' else 'FILE'}] {i['name']} "
                f"(size={i['size']} байт, modified={i['modified']})"
                for i in items
            ]
            return f"📂 Вміст директорії {args[0]} (елементів: {res.get('count', 0)}):\n" + "\n".join(lines)
        
        if cmd == "file_info":
            if not args:
                return "❌ Вкажіть шлях до файлу. Приклад: file_info \"C:\\шлях\\файл.txt\""
            res = self.fs_manager.file_info(args[0])
            if not res.get("success"):
                return res.get("error", "❌ Помилка")
            return "📑 Інформація про файл:\n" + self._json(res["info"])
        
        if cmd == "search_in_files":
            if len(args) < 2:
                return "❌ Використання: search_in_files <директорія> <текст> [розширення...]"
            directory = args[0]
            text = args[1]
            exts = args[2:] if len(args) > 2 else None
            res = self.fs_manager.search_in_files(directory, text, exts)
            if not res.get("success"):
                return res.get("error", "❌ Помилка")
            matches = res.get("matches", [])
            if not matches:
                return f"ℹ️ Текст \"{text}\" не знайдено."
            lines = [
                f"{m['file']}:{m['line_number']}: {m['line']}"
                for m in matches
            ]
            return f"🔎 Знайдено {res.get('count', 0)} збіг(ів):\n" + "\n".join(lines)
        
        if cmd == "get_file_hash":
            if not args:
                return "❌ Використання: get_file_hash <шлях> [алгоритм]"
            filepath = args[0]
            algo = args[1] if len(args) > 1 else 'sha256'
            res = self.fs_manager.get_file_hash(filepath, algo)
            if not res.get("success"):
                return res.get("error", "❌ Помилка")
            return f"🔐 Хеш файлу ({res['algorithm']}):\n{res['hash']}"
        
        if cmd == "find_large_files":
            if not args:
                return "❌ Використання: find_large_files <директорія> [мін_розмір_МБ]"
            directory = args[0]
            size_mb = 100
            if len(args) > 1:
                try:
                    size_mb = int(args[1])
                except ValueError:
                    return "❌ Мінімальний розмір має бути числом (МБ)."
            res = self.fs_manager.find_large_files(directory, size_mb)
            if not res.get("success"):
                return res.get("error", "❌ Помилка")
            files = res.get("files", [])
            if not files:
                return f"ℹ️ Файлів більших за {size_mb} МБ не знайдено."
            lines = [
                f"- {f['path']} ({f['size_mb']})"
                for f in files
            ]
            return f"📦 Великі файли (мін. {size_mb} МБ, знайдено {res.get('count', 0)}):\n" + "\n".join(lines)
        
        if cmd == "find_duplicates":
            if not args:
                return "❌ Використання: find_duplicates <директорія>"
            res = self.fs_manager.find_duplicates(args[0])
            if not res.get("success"):
                return res.get("error", "❌ Помилка")
            if res.get("groups", 0) == 0:
                return "ℹ️ Дублікатів не знайдено."
            return "🧬 Дублікати файлів:\n" + self._json(res)
        
        if cmd == "analyze_folder":
            if not args:
                return "❌ Використання: analyze_folder <директорія>"
            res = self.fs_manager.analyze_folder(args[0])
            if not res.get("success"):
                return res.get("error", "❌ Помилка")
            return "📊 Аналіз папки:\n" + self._json(res["analysis"])
        
        if cmd == "index_directory":
            if not args:
                return "❌ Використання: index_directory <директорія>"
            res = self.fs_manager.index_directory(args[0])
            if not res.get("success"):
                return res.get("error", "❌ Помилка")
            return f"✅ Проіндексовано файлів: {res.get('indexed_files', 0)}"
        
        # --- ПРОГРАМИ / ПРОЦЕСИ ---
        if cmd == "list_programs":
            res = self.app_manager.list_programs()
            if not res.get("success"):
                return res.get("error", "❌ Помилка")
            programs = res.get("programs", [])
            if not programs:
                return "ℹ️ Не знайдено встановлених програм (або не підтримується на цій ОС)."
            lines = [
                f"- {p['name']}" + (f" (версія {p['version']})" if p.get('version') else "")
                for p in programs[:100]
            ]
            return f"📦 Встановлені програми (показано {len(lines)} з {len(programs)}):\n" + "\n".join(lines)
        
        if cmd == "launch_program":
            if not args:
                return "❌ Використання: launch_program <шлях або назва>"
            program = " ".join(args)
            res = self.app_manager.launch_program(program)
            return res.get("message") if res.get("success") else res.get("error", "❌ Помилка")
        
        if cmd == "close_program":
            if not args:
                return "❌ Використання: close_program <назва_процесу>"
            res = self.app_manager.close_program(" ".join(args))
            if not res.get("success"):
                return res.get("error", "❌ Помилка")
            return "✅ Закрито процеси:\n" + "\n".join(res.get("terminated", []))
        
        if cmd == "list_processes":
            sort_by = "cpu"
            limit = 20
            if len(args) >= 1 and args[0] in ("cpu", "memory"):
                sort_by = args[0]
            if len(args) >= 2:
                try:
                    limit = int(args[1])
                except ValueError:
                    return "❌ Обмеження (limit) має бути числом."
            res = self.sys_monitor.list_processes(sort_by=sort_by, limit=limit)
            if not res.get("success"):
                return res.get("error", "❌ Помилка")
            procs = res.get("processes", [])
            lines = [
                f"{p['pid']}: {p['name']} | CPU {p['cpu']} | RAM {p['memory']:.2f}% | {p['status']}"
                for p in procs
            ]
            return f"🧾 Процеси (сортування: {sort_by}, показано {len(procs)}):\n" + "\n".join(lines)
        
        if cmd == "process_info":
            if not args:
                return "❌ Використання: process_info <pid або частина назви>"
            res = self.app_manager.process_info(args[0])
            if not res.get("success"):
                return res.get("error", "❌ Помилка")
            return "ℹ️ Інформація про процес:\n" + self._json(res["info"])
        
        if cmd == "kill_process":
            if not args:
                return "❌ Використання: kill_process <pid>"
            try:
                pid = int(args[0])
            except ValueError:
                return "❌ PID має бути числом."
            res = self.app_manager.kill_process(pid)
            return res.get("message") if res.get("success") else res.get("error", "❌ Помилка")
        
        # --- СИСТЕМА ---
        if cmd == "system_info":
            res = self.sys_monitor.get_system_info()
            if not res.get("success"):
                return res.get("error", "❌ Помилка")
            return "💻 Системна інформація:\n" + self._json(res["info"])
        
        if cmd == "cpu_info":
            res = self.sys_monitor.get_cpu_info()
            if not res.get("success"):
                return res.get("error", "❌ Помилка")
            return "🧠 Інформація про CPU:\n" + self._json(res["cpu"])
        
        if cmd == "memory_info":
            res = self.sys_monitor.get_memory_info()
            if not res.get("success"):
                return res.get("error", "❌ Помилка")
            return "💾 Інформація про пам'ять:\n" + self._json(res["memory"])
        
        if cmd == "disk_info":
            res = self.sys_monitor.get_disk_info()
            if not res.get("success"):
                return res.get("error", "❌ Помилка")
            return "💽 Інформація про диски:\n" + self._json(res["disks"])
        
        if cmd == "network_info":
            res = self.sys_monitor.get_network_info()
            if not res.get("success"):
                return res.get("error", "❌ Помилка")
            return "🌐 Мережева інформація:\n" + self._json(res["info"])
        
        if cmd == "battery_info":
            res = self.sys_monitor.get_battery_info()
            if not res.get("success"):
                return res.get("error", "❌ Помилка")
            return "🔋 Інформація про батарею:\n" + self._json(res["info"])
        
        # --- МЕРЕЖА ---
        if cmd == "check_internet":
            res = self.net_manager.check_internet()
            if not res.get("success"):
                return "❌ Помилка перевірки інтернету"
            if not res.get("connected"):
                return "⚠️ Інтернет-з'єднання відсутнє."
            return f"✅ Інтернет працює. Затримка: {res.get('latency_ms')}, статус HTTP: {res.get('status_code')}"
        
        if cmd == "download_file":
            if len(args) < 2:
                return "❌ Використання: download_file <url> <шлях_для_збереження>"
            res = self.net_manager.download_file(args[0], args[1])
            return res.get("message") if res.get("success") else res.get("error", "❌ Помилка")
        
        if cmd == "open_webpage":
            if not args:
                return "❌ Використання: open_webpage <url>"
            res = self.net_manager.open_webpage(args[0])
            return res.get("message") if res.get("success") else res.get("error", "❌ Помилка")
        
        if cmd == "ping":
            if not args:
                return "❌ Використання: ping <хост> [кількість]"
            host = args[0]
            count = 4
            if len(args) > 1:
                try:
                    count = int(args[1])
                except ValueError:
                    return "❌ Кількість має бути числом."
            res = self.net_manager.ping(host, count)
            if not res.get("success"):
                return res.get("error", "❌ Помилка")
            reachable = res.get("reachable", False)
            status = "✅ Доступний" if reachable else "⚠️ Недоступний"
            return f"{status} хост {host}:\n{res.get('output', '')}"
        
        if cmd == "get_ip_info":
            res = self.net_manager.get_ip_info()
            if not res.get("success"):
                return res.get("error", "❌ Помилка")
            return "🌍 IP-інформація:\n" + self._json(res)
        
        if cmd == "list_network_connections":
            res = self.net_manager.list_network_connections()
            if not res.get("success"):
                return res.get("error", "❌ Помилка")
            return "🔌 Мережеві з'єднання:\n" + self._json(res)
        
        # --- ПАМ'ЯТЬ / КОНТЕКСТ ---
        if cmd == "remember":
            if len(args) < 2:
                return "❌ Використання: remember <ключ> <значення>"
            key = args[0]
            value = " ".join(args[1:])
            self.db.save_preference(key, value)
            return f"✅ Запам'ятав: {key} = {value}"
        
        if cmd == "recall":
            if not args:
                return "❌ Використання: recall <ключ>"
            key = args[0]
            value = self.db.get_preference(key)
            if value is None:
                return f"ℹ️ Нічого не запам'ятано для ключа: {key}"
            return f"🧠 Пам'ять [{key}] = {value}"
        
        if cmd == "forget":
            if not args:
                return "❌ Використання: forget <ключ>"
            key = args[0]
            self.db.delete_preference(key)
            return f"✅ Забув ключ: {key}"
        
        if cmd == "show_memory":
            prefs = self.db.get_all_preferences()
            if not prefs:
                return "ℹ️ Пам'ять порожня."
            lines = [f"- {k}: {v}" for k, v in prefs.items()]
            return "🧠 Збережена пам'ять:\n" + "\n".join(lines)
        
        if cmd == "command_history":
            limit = 20
            if args:
                try:
                    limit = int(args[0])
                except ValueError:
                    return "❌ Кількість має бути числом."
            history = self.db.get_command_history(limit=limit)
            if not history:
                return "ℹ️ Історія команд порожня."
            lines = [
                f"{h['timestamp']} | {'✅' if h['success'] else '❌'} | {h['command']}"
                for h in history
            ]
            return "📜 Історія команд:\n" + "\n".join(lines)
        
        # --- УТИЛІТИ ---
        if cmd == "calculator":
            if not args:
                return "❌ Використання: calculator <вираз>"
            expr = " ".join(args)
            res = self.utilities.calculator(expr)
            if not res.get("success"):
                return res.get("error", "❌ Помилка")
            return f"🧮 Результат: {res['result']}"
        
        if cmd == "generate_password":
            length = 16
            if args:
                try:
                    length = int(args[0])
                except ValueError:
                    return "❌ Довжина має бути числом."
            res = self.utilities.generate_password(length)
            if not res.get("success"):
                return res.get("error", "❌ Помилка")
            return f"🔑 Згенерований пароль ({length}): {res['password']}"
        
        if cmd == "hash_text":
            if not args:
                return "❌ Використання: hash_text <текст> [алгоритм]"
            text = args[0]
            algorithm = args[1] if len(args) > 1 else "sha256"
            res = self.utilities.hash_text(text, algorithm)
            if not res.get("success"):
                return res.get("error", "❌ Помилка")
            return f"🔐 Хеш ({res['algorithm']}): {res['hash']}"
        
        if cmd == "current_time":
            res = self.utilities.current_time()
            if not res.get("success"):
                return "❌ Помилка отримання часу"
                return "❌ Помилка перевірки інтернету"
            if not res.get("connected"):
                return "⚠️ Інтернет-з'єднання відсутнє."
            return f"✅ Інтернет працює. Затримка: {res.get('latency_ms')}, статус HTTP: {res.get('status_code')}"
        
        if cmd == "download_file":
            if len(args) < 2:
                return "❌ Використання: download_file <url> <шлях_для_збереження>"
            res = self.net_manager.download_file(args[0], args[1])
            return res.get("message") if res.get("success") else res.get("error", "❌ Помилка")
        
        if cmd == "open_webpage":
            if not args:
                return "❌ Використання: open_webpage <url>"
            res = self.net_manager.open_webpage(args[0])
            return res.get("message") if res.get("success") else res.get("error", "❌ Помилка")
        
        if cmd == "ping":
            if not args:
                return "❌ Використання: ping <хост> [кількість]"
            host = args[0]
            count = 4
            if len(args) > 1:
                try:
                    count = int(args[1])
                except ValueError:
                    return "❌ Кількість має бути числом."
            res = self.net_manager.ping(host, count)
            if not res.get("success"):
                return res.get("error", "❌ Помилка")
            reachable = res.get("reachable", False)
            status = "✅ Доступний" if reachable else "⚠️ Недоступний"
            return f"{status} хост {host}:\n{res.get('output', '')}"
        
        if cmd == "get_ip_info":
            res = self.net_manager.get_ip_info()
            if not res.get("success"):
                return res.get("error", "❌ Помилка")
            return "🌍 IP-інформація:\n" + self._json(res)
        
        if cmd == "list_network_connections":
            res = self.net_manager.list_network_connections()
            if not res.get("success"):
                return res.get("error", "❌ Помилка")
            return "🔌 Мережеві з'єднання:\n" + self._json(res)
        
        # --- ПАМ'ЯТЬ / КОНТЕКСТ ---
        if cmd == "remember":
            if len(args) < 2:
                return "❌ Використання: remember <ключ> <значення>"
            key = args[0]
            value = " ".join(args[1:])
            self.db.save_preference(key, value)
            return f"✅ Запам'ятав: {key} = {value}"
        
        if cmd == "recall":
            if not args:
                return "❌ Використання: recall <ключ>"
            key = args[0]
            value = self.db.get_preference(key)
            if value is None:
                return f"ℹ️ Нічого не запам'ятано для ключа: {key}"
            return f"🧠 Пам'ять [{key}] = {value}"
        
        if cmd == "forget":
            if not args:
                return "❌ Використання: forget <ключ>"
            key = args[0]
            self.db.delete_preference(key)
            return f"✅ Забув ключ: {key}"
        
        if cmd == "show_memory":
            prefs = self.db.get_all_preferences()
            if not prefs:
                return "ℹ️ Пам'ять порожня."
            lines = [f"- {k}: {v}" for k, v in prefs.items()]
            return "🧠 Збережена пам'ять:\n" + "\n".join(lines)
        
        if cmd == "command_history":
            limit = 20
            if args:
                try:
                    limit = int(args[0])
                except ValueError:
                    return "❌ Кількість має бути числом."
            history = self.db.get_command_history(limit=limit)
            if not history:
                return "ℹ️ Історія команд порожня."
            lines = [
                f"{h['timestamp']} | {'✅' if h['success'] else '❌'} | {h['command']}"
                for h in history
            ]
            return "📜 Історія команд:\n" + "\n".join(lines)
        
        # --- УТИЛІТИ ---
        if cmd == "calculator":
            if not args:
                return "❌ Використання: calculator <вираз>"
            expr = " ".join(args)
            res = self.utilities.calculator(expr)
            if not res.get("success"):
                return res.get("error", "❌ Помилка")
            return f"🧮 Результат: {res['result']}"
        
        if cmd == "generate_password":
            length = 16
            if args:
                try:
                    length = int(args[0])
                except ValueError:
                    return "❌ Довжина має бути числом."
            res = self.utilities.generate_password(length)
            if not res.get("success"):
                return res.get("error", "❌ Помилка")
            return f"🔑 Згенерований пароль ({length}): {res['password']}"
        
        if cmd == "hash_text":
            if not args:
                return "❌ Використання: hash_text <текст> [алгоритм]"
            text = args[0]
            algorithm = args[1] if len(args) > 1 else "sha256"
            res = self.utilities.hash_text(text, algorithm)
            if not res.get("success"):
                return res.get("error", "❌ Помилка")
            return f"🔐 Хеш ({res['algorithm']}): {res['hash']}"
        
        if cmd == "current_time":
            res = self.utilities.current_time()
        
        if cmd == "forget":
            if not args:
                return "❌ Використання: forget <ключ>"
            key = args[0]
            self.db.delete_preference(key)
            return f"✅ Забув ключ: {key}"
        
        if cmd == "show_memory":
            prefs = self.db.get_all_preferences()
            if not prefs:
                return "ℹ️ Пам'ять порожня."
            lines = [f"- {k}: {v}" for k, v in prefs.items()]
            return "🧠 Збережена пам'ять:\n" + "\n".join(lines)
        
        if cmd == "command_history":
            limit = 20
            if args:
                try:
                    limit = int(args[0])
                except ValueError:
                    return "❌ Кількість має бути числом."
            history = self.db.get_command_history(limit=limit)
            if not history:
                return "ℹ️ Історія команд порожня."
            lines = [
                f"{h['timestamp']} | {'✅' if h['success'] else '❌'} | {h['command']}"
                for h in history
            ]
            return "📜 Історія команд:\n" + "\n".join(lines)
        
        # --- УТИЛІТИ ---
        if cmd == "calculator":
            if not args:
                return "❌ Використання: calculator <вираз>"
            expr = " ".join(args)
            res = self.utilities.calculator(expr)
            if not res.get("success"):
                return res.get("error", "❌ Помилка")
            return f"🧮 Результат: {res['result']}"
        
        if cmd == "generate_password":
            length = 16
            if args:
                try:
                    length = int(args[0])
                except ValueError:
                    return "❌ Довжина має бути числом."
            res = self.utilities.generate_password(length)
            if not res.get("success"):
                return res.get("error", "❌ Помилка")
            return f"🔑 Згенерований пароль ({length}): {res['password']}"
        
        if cmd == "hash_text":
            if not args:
                return "❌ Використання: hash_text <текст> [алгоритм]"
            text = args[0]
            algorithm = args[1] if len(args) > 1 else "sha256"
            res = self.utilities.hash_text(text, algorithm)
            if not res.get("success"):
                return res.get("error", "❌ Помилка")
            return f"🔐 Хеш ({res['algorithm']}): {res['hash']}"
        
        if cmd == "current_time":
            res = self.utilities.current_time()
            if not res.get("success"):
                return "❌ Помилка отримання часу"
            return f"⏰ Поточний час: {res['datetime']} (TZ: {res['timezone']})"
        
        # --- ДОВІДКА / ІНФО ---
        if cmd == "help":
            if not args:
                return (
                    "📚 Допомога по командам:\n"
                    "- read_file <шлях>\n"
                    "- search_files <директорія> [розширення]\n"
                    "- open_file <шлях>\n"
                    "- copy_file <src> <dst>\n"
                    "- move_file <src> <dst>\n"
                    "- delete_file <шлях>\n"
                    "- create_folder <шлях>\n"
                    "- list_directory <шлях>\n"
                    "- file_info <шлях>\n"
                    "- search_in_files <директорія> <текст> [розширення...]\n"
                    "- get_file_hash <шлях> [алгоритм]\n"
                    "- find_large_files <директорія> [мін_МБ]\n"
                    "- find_duplicates <директорія>\n"
                    "- analyze_folder <директорія>\n"
                    "- index_directory <директорія>\n"
                    "\n📦 Програми:\n"
                    "- list_programs\n"
                    "- launch_program <шлях>\n"
                    "- close_program <назва>\n"
                    "- list_processes [cpu|memory] [limit]\n"
                    "- process_info <pid>\n"
                    "- kill_process <pid>\n"
                    "\n💻 Система:\n"
                    "- system_info\n"
                    "- cpu_info\n"
                    "- memory_info\n"
                    "- disk_info\n"
                    "- network_info\n"
                    "- battery_info\n"
                    "\n🌐 Мережа:\n"
                    "- check_internet\n"
                    "- download_file <url> <шлях>\n"
                    "- open_webpage <url>\n"
                    "- ping <хост>\n"
                    "- get_ip_info\n"
                    "- list_network_connections\n"
                    "\n🧠 Пам'ять:\n"
                    "- remember <ключ> <значення>\n"
                    "- recall <ключ>\n"
                    "- forget <ключ>\n"
                    "- show_memory\n"
                    "- command_history\n"
                    "\n🔧 Утиліти:\n"
                    "- calculator <вираз>\n"
                    "- generate_password [довжина]\n"
                    "- hash_text <текст>\n"
                    "- current_time\n"
                    "\nℹ️ Інше:\n"
                    "- about\n"
                    "- exit"
                )
            return f"ℹ️ Довідка по команді {args[0]}: (тут має бути детальний опис, але поки див. загальний help)"

        if cmd == "about":
            return (
                "🤖 AIAgent Pro v2.0\n"
                "Потужний локальний асистент для керування комп'ютером.\n"
                "Використовує LM Studio для розуміння природної мови.\n"
                "Автор: AI Assistant (модифіковано)"
            )
            
        return None

    def process_llm_response(self, response: str) -> str:
        """Обробка відповіді від LLM та виконання функцій"""
        try:
            # Регулярний вираз для пошуку команд у форматі to=browser.func або to=functions.func
            cmd_pattern = r'to=(?:functions|browser)\.(\w+)\s*<\|message\|>\s*(\{.*?\})'
            match = re.search(cmd_pattern, response, re.DOTALL)
            
            if match:
                func_name = match.group(1)
                json_args = match.group(2)
                
                try:
                    args = json.loads(json_args)
                    
                    # Виконуємо команду через handle_direct_command
                    if func_name == "open_webpage" and "url" in args:
                        return self.handle_direct_command(f"open_webpage {args['url']}")
                    elif func_name == "calculator" and "expression" in args:
                        return self.handle_direct_command(f"calculator {args['expression']}")
                    elif func_name == "search_files" and "directory" in args:
                        pattern = args.get("pattern", "*")
                        return self.handle_direct_command(f"search_files {args['directory']} {pattern}")
                    elif func_name == "read_file" and "path" in args:
                        return self.handle_direct_command(f"read_file {args['path']}")
                    elif func_name == "list_directory" and "path" in args:
                        return self.handle_direct_command(f"list_directory {args['path']}")
                    
                    return f"✅ Команда '{func_name}' розпізнана: {json_args}"
                    
                except json.JSONDecodeError:
                    return f"❌ Помилка парсингу аргументів JSON для команди {func_name}"
            
            return response
            
        except Exception as e:
            logging.error(f"Помилка обробки відповіді LLM: {e}")
            return f"❌ Помилка обробки команди: {str(e)}"

    def interactive_mode(self):
        """Інтерактивний режим роботи агента"""
        print(f"📅 Час запуску: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"💻 Система: {platform.system()} {platform.release()}")
        print("="*60)
        print("💡 Введіть команду або запит звичайною мовою.")
        print("💡 Введіть 'help' для списку команд або 'exit' для виходу.")
        print("-" * 60)

        while True:
            try:
                user_input = input("\n👤 Ви: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ('exit', 'quit', 'вихід'):
                    print("👋 До побачення!")
                    break
                
                # Спробуємо виконати як пряму команду
                direct_result = self.handle_direct_command(user_input)
                
                if direct_result:
                    print(f"\n🤖 Агент:\n{direct_result}")
                else:
                    # Якщо це не пряма команда - відправляємо в LLM
                    print("\n⏳ Думаю...", end="", flush=True)
                    response = self.lm_client.send_message(user_input)
                    # Очищаємо рядок "Думаю..."
                    print("\r" + " " * 20 + "\r", end="", flush=True)
                    
                    # Обробляємо відповідь на наявність функцій
                    processed_response = self.process_llm_response(response)
                    print(f"🤖 Агент:\n{processed_response}")
                    
            except KeyboardInterrupt:
                print("\n👋 Перервано користувачем. До побачення!")
                break
            except Exception as e:
                logging.error(f"Критична помилка: {str(e)}")
                print(f"\n❌ Сталася помилка: {str(e)}")

if __name__ == "__main__":
    setup_logging()
    try:
        agent = AIAgent()
        agent.interactive_mode()
    except Exception as e:
        print(f"❌ Не вдалося запустити агента: {e}")
        logging.critical(f"Failed to start agent: {e}")