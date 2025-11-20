"""
Розширені функції для AI-агента v3.0
Модуль додаткових можливостей
"""

import os
import sys
import subprocess
import time
import hashlib
import json
import zipfile
import tarfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List
import psutil
import platform

try:
    from PIL import ImageGrab, Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️ Встановіть Pillow для роботи зі скріншотами: pip install Pillow")

try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except ImportError:
    PYPERCLIP_AVAILABLE = False
    print("⚠️ Встановіть pyperclip для роботи з буфером: pip install pyperclip")

try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False
    print("⚠️ Встановіть plyer для сповіщень: pip install plyer")

# ============================================================================
# МУЛЬТИМЕДІА ФУНКЦІЇ
# ============================================================================

class MultimediaManager:
    """Управління мультимедіа - скріншоти, запис екрану, стиснення"""
    
    def __init__(self, screenshots_dir: Path):
        self.screenshots_dir = screenshots_dir
        self.screenshots_dir.mkdir(exist_ok=True)
    
    def take_screenshot(self, filename: str = None) -> Dict[str, Any]:
        """Зробити скріншот"""
        if not PIL_AVAILABLE:
            return {"success": False, "error": "❌ Pillow не встановлено"}
        
        try:
            if not filename:
                filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            
            filepath = self.screenshots_dir / filename
            screenshot = ImageGrab.grab()
            screenshot.save(filepath, "PNG")
            
            file_size = os.path.getsize(filepath)
            return {
                "success": True, 
                "filepath": str(filepath),
                "size_kb": f"{file_size / 1024:.2f} KB",
                "resolution": f"{screenshot.width}x{screenshot.height}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def compress_image(self, filepath: str, quality: int = 85) -> Dict[str, Any]:
        """Стиснути зображення"""
        if not PIL_AVAILABLE:
            return {"success": False, "error": "❌ Pillow не встановлено"}
        
        try:
            if not os.path.exists(filepath):
                return {"success": False, "error": "❌ Файл не існує"}
            
            original_size = os.path.getsize(filepath)
            img = Image.open(filepath)
            
            output_path = str(Path(filepath).with_suffix('')) + '_compressed' + Path(filepath).suffix
            img.save(output_path, quality=quality, optimize=True)
            
            compressed_size = os.path.getsize(output_path)
            savings = ((original_size - compressed_size) / original_size) * 100
            
            return {
                "success": True,
                "output_path": output_path,
                "original_size_kb": f"{original_size / 1024:.2f} KB",
                "compressed_size_kb": f"{compressed_size / 1024:.2f} KB",
                "savings_percent": f"{savings:.1f}%"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def record_screen(self, duration: int = 10) -> Dict[str, Any]:
        """Запис відео з екрану (потребує додаткових бібліотек)"""
        return {
            "success": False, 
            "error": "⚠️ Функція запису екрану потребує opencv-python та pyautogui. Встановіть: pip install opencv-python pyautogui"
        }

# ============================================================================
# СИСТЕМНІ УТИЛІТИ
# ============================================================================

class SystemUtilities:
    """Системні утиліти - буфер, сповіщення, клінап"""
    
    @staticmethod
    def clipboard_get() -> Dict[str, Any]:
        """Отримати вміст буфера обміну"""
        if not PYPERCLIP_AVAILABLE:
            return {"success": False, "error": "❌ pyperclip не встановлено"}
        
        try:
            content = pyperclip.paste()
            return {"success": True, "content": content, "length": len(content)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def clipboard_set(text: str) -> Dict[str, Any]:
        """Встановити вміст буфера обміну"""
        if not PYPERCLIP_AVAILABLE:
            return {"success": False, "error": "❌ pyperclip не встановлено"}
        
        try:
            pyperclip.copy(text)
            return {"success": True, "message": f"✅ Скопійовано в буфер обміну ({len(text)} символів)"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def send_notification(title: str, message: str, timeout: int = 10) -> Dict[str, Any]:
        """Відправити системне сповіщення"""
        if not PLYER_AVAILABLE:
            # Fallback для Windows без plyer
            if platform.system() == "Windows":
                try:
                    from win10toast import ToastNotifier
                    toaster = ToastNotifier()
                    toaster.show_toast(title, message, duration=timeout, threaded=True)
                    return {"success": True, "message": "✅ Сповіщення відправлено"}
                except ImportError:
                    return {
                        "success": False, 
                        "error": "❌ Встановіть plyer або win10toast: pip install plyer win10toast"
                    }
        
        try:
            notification.notify(
                title=title,
                message=message,
                timeout=timeout
            )
            return {"success": True, "message": "✅ Сповіщення відправлено"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def auto_cleanup(temp_dirs: List[str] = None) -> Dict[str, Any]:
        """Автоматичне очищення тимчасових файлів"""
        try:
            if temp_dirs is None:
                temp_dirs = [
                    os.environ.get('TEMP', 'C:\\Windows\\Temp'),
                    os.path.expanduser('~\\AppData\\Local\\Temp')
                ]
            
            cleaned_files = 0
            freed_space = 0
            errors = []
            
            for temp_dir in temp_dirs:
                if not os.path.exists(temp_dir):
                    continue
                
                try:
                    for item in os.listdir(temp_dir):
                        item_path = os.path.join(temp_dir, item)
                        try:
                            if os.path.isfile(item_path):
                                size = os.path.getsize(item_path)
                                os.remove(item_path)
                                cleaned_files += 1
                                freed_space += size
                            elif os.path.isdir(item_path):
                                import shutil
                                size = sum(f.stat().st_size for f in Path(item_path).rglob('*') if f.is_file())
                                shutil.rmtree(item_path)
                                cleaned_files += 1
                                freed_space += size
                        except (PermissionError, OSError) as e:
                            errors.append(f"{item}: {str(e)}")
                            continue
                except Exception as e:
                    errors.append(f"Помилка доступу до {temp_dir}: {str(e)}")
            
            return {
                "success": True,
                "cleaned_files": cleaned_files,
                "freed_space_mb": f"{freed_space / 1024 / 1024:.2f} MB",
                "errors": errors if errors else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def kill_frozen_apps(cpu_threshold: float = 0.1) -> Dict[str, Any]:
        """Закрити завислі програми"""
        try:
            frozen_apps = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'status']):
                try:
                    if proc.info['status'] == 'stopped' or (proc.info['cpu_percent'] == 0 and proc.info['status'] == 'running'):
                        # Додаткова перевірка
                        time.sleep(0.5)
                        if not proc.is_running():
                            continue
                        
                        cpu = proc.cpu_percent(interval=1.0)
                        if cpu < cpu_threshold and proc.info['status'] not in ['sleeping', 'disk-sleep']:
                            proc.terminate()
                            frozen_apps.append(f"{proc.info['name']} (PID: {proc.info['pid']})")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            return {
                "success": True,
                "terminated": frozen_apps,
                "count": len(frozen_apps)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def optimize_memory() -> Dict[str, Any]:
        """Оптимізація використання пам'яті"""
        try:
            import gc
            gc.collect()
            
            initial_memory = psutil.virtual_memory()
            
            # Очищення кешу файлової системи (тільки Windows)
            if platform.system() == "Windows":
                try:
                    subprocess.run(['rundll32.exe', 'advapi32.dll,ProcessIdleTasks'], 
                                   timeout=10, capture_output=True)
                except Exception:
                    pass
            
            time.sleep(1)
            final_memory = psutil.virtual_memory()
            
            freed = initial_memory.used - final_memory.used
            
            return {
                "success": True,
                "initial_usage": f"{initial_memory.percent}%",
                "final_usage": f"{final_memory.percent}%",
                "freed_mb": f"{freed / 1024 / 1024:.2f} MB"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

# ============================================================================
# МОНІТОРИНГ ТА АНАЛІТИКА
# ============================================================================

class MonitoringManager:
    """Моніторинг системи та аналітика"""
    
    def __init__(self, db=None):
        self.db = db
        self.monitoring_active = False
        self.monitoring_thread = None
    
    def monitor_performance(self, duration: int = 60) -> Dict[str, Any]:
        """Моніторинг продуктивності системи"""
        try:
            samples = []
            interval = 2  # секунди
            num_samples = duration // interval
            
            for _ in range(num_samples):
                sample = {
                    "timestamp": datetime.now().isoformat(),
                    "cpu": psutil.cpu_percent(interval=1),
                    "memory": psutil.virtual_memory().percent,
                    "disk": psutil.disk_usage('/').percent if platform.system() != "Windows" else psutil.disk_usage('C:\\').percent
                }
                samples.append(sample)
                time.sleep(interval - 1)  # -1 секунда вже витрачена на cpu_percent
            
            # Аналіз
            avg_cpu = sum(s['cpu'] for s in samples) / len(samples)
            avg_memory = sum(s['memory'] for s in samples) / len(samples)
            max_cpu = max(s['cpu'] for s in samples)
            max_memory = max(s['memory'] for s in samples)
            
            alerts = []
            if avg_cpu > 80:
                alerts.append(f"⚠️ Високе навантаження CPU: {avg_cpu:.1f}%")
            if avg_memory > 85:
                alerts.append(f"⚠️ Високе використання RAM: {avg_memory:.1f}%")
            
            return {
                "success": True,
                "duration_seconds": duration,
                "samples": len(samples),
                "average": {
                    "cpu": f"{avg_cpu:.1f}%",
                    "memory": f"{avg_memory:.1f}%"
                },
                "peak": {
                    "cpu": f"{max_cpu:.1f}%",
                    "memory": f"{max_memory:.1f}%"
                },
                "alerts": alerts if alerts else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def log_analyzer(self, log_path: str = None) -> Dict[str, Any]:
        """Аналіз лог-файлів"""
        try:
            if not log_path:
                log_path = "logs"
            
            if not os.path.exists(log_path):
                return {"success": False, "error": "❌ Шлях не існує"}
            
            errors = []
            warnings = []
            info_count = 0
            
            # Якщо це директорія, знайти всі .log файли
            if os.path.isdir(log_path):
                log_files = list(Path(log_path).glob("*.log"))
            else:
                log_files = [Path(log_path)]
            
            for log_file in log_files:
                try:
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            line_lower = line.lower()
                            if 'error' in line_lower or 'exception' in line_lower:
                                errors.append(line.strip())
                            elif 'warning' in line_lower or 'warn' in line_lower:
                                warnings.append(line.strip())
                            elif 'info' in line_lower:
                                info_count += 1
                except Exception:
                    continue
            
            return {
                "success": True,
                "files_analyzed": len(log_files),
                "errors": len(errors),
                "warnings": len(warnings),
                "info_messages": info_count,
                "recent_errors": errors[-10:] if errors else [],
                "recent_warnings": warnings[-10:] if warnings else []
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def system_report(self) -> Dict[str, Any]:
        """Комплексний звіт про систему"""
        try:
            cpu = psutil.cpu_percent(interval=1, percpu=False)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('C:\\' if platform.system() == "Windows" else '/')
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            
            # Топ процесів
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append({
                        "name": proc.info['name'],
                        "cpu": proc.info['cpu_percent'],
                        "memory": proc.info['memory_percent']
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            processes.sort(key=lambda x: x['cpu'], reverse=True)
            top_processes = processes[:10]
            
            report = {
                "generated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "system": {
                    "os": f"{platform.system()} {platform.release()}",
                    "processor": platform.processor(),
                    "uptime": str(uptime).split('.')[0]
                },
                "resources": {
                    "cpu_usage": f"{cpu}%",
                    "memory_usage": f"{memory.percent}%",
                    "memory_available": f"{memory.available / 1024**3:.2f} GB",
                    "disk_usage": f"{disk.percent}%",
                    "disk_free": f"{disk.free / 1024**3:.2f} GB"
                },
                "top_processes_by_cpu": top_processes,
                "health_status": "🟢 Нормально" if cpu < 80 and memory.percent < 85 else "🟡 Потребує уваги"
            }
            
            return {"success": True, "report": report}
        except Exception as e:
            return {"success": False, "error": str(e)}

# ============================================================================
# МЕРЕЖЕВІ УТИЛІТИ
# ============================================================================

class NetworkUtilities:
    """Додаткові мережеві функції"""
    
    @staticmethod
    def speedtest() -> Dict[str, Any]:
        """Тест швидкості інтернету (базовий)"""
        try:
            import requests
            
            # Тест завантаження (download)
            url = "http://speedtest.ftp.otenet.gr/files/test1Mb.db"
            start_time = time.time()
            response = requests.get(url, timeout=30)
            elapsed = time.time() - start_time
            
            file_size_mb = len(response.content) / 1024 / 1024
            download_speed = file_size_mb / elapsed
            
            # Тест ping
            ping_start = time.time()
            requests.get("https://www.google.com", timeout=5)
            ping = (time.time() - ping_start) * 1000
            
            return {
                "success": True,
                "download_speed_mbps": f"{download_speed:.2f} Mbps",
                "ping_ms": f"{ping:.0f} ms",
                "test_file_size_mb": f"{file_size_mb:.2f} MB"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def check_website_status(url: str) -> Dict[str, Any]:
        """Перевірка статусу веб-сайту"""
        try:
            import requests
            
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            start_time = time.time()
            response = requests.get(url, timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            return {
                "success": True,
                "url": url,
                "status_code": response.status_code,
                "status": "✅ Онлайн" if response.status_code == 200 else f"⚠️ Статус {response.status_code}",
                "response_time_ms": f"{response_time:.0f} ms",
                "server": response.headers.get('Server', 'Unknown')
            }
        except Exception as e:
            return {"success": False, "url": url, "status": "❌ Офлайн", "error": str(e)}

# ============================================================================
# АВТОМАТИЗАЦІЯ
# ============================================================================

class AutomationManager:
    """Менеджер автоматизації та планування"""
    
    def __init__(self, db=None):
        self.db = db
    
    def backup_files(self, source: str, destination: str) -> Dict[str, Any]:
        """Резервне копіювання файлів"""
        try:
            if not os.path.exists(source):
                return {"success": False, "error": "❌ Джерело не існує"}
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"backup_{timestamp}"
            backup_path = os.path.join(destination, backup_name)
            
            import shutil
            if os.path.isfile(source):
                os.makedirs(destination, exist_ok=True)
                shutil.copy2(source, os.path.join(backup_path, os.path.basename(source)))
                backed_up = 1
            else:
                shutil.copytree(source, backup_path)
                backed_up = sum(1 for _ in Path(backup_path).rglob('*') if _.is_file())
            
            backup_size = sum(f.stat().st_size for f in Path(backup_path).rglob('*') if f.is_file())
            
            return {
                "success": True,
                "backup_path": backup_path,
                "files_backed_up": backed_up,
                "backup_size_mb": f"{backup_size / 1024 / 1024:.2f} MB"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def schedule_task(self, task_name: str, command: str, schedule_time: str, schedule_type: str = "once") -> Dict[str, Any]:
        """Запланувати завдання"""
        try:
            if self.db:
                self.db.add_scheduled_task(task_name, command, schedule_time, schedule_type)
                return {
                    "success": True,
                    "message": f"✅ Завдання '{task_name}' заплановано на {schedule_time}"
                }
            else:
                return {"success": False, "error": "❌ База даних недоступна"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def watch_directory(self, directory: str, duration: int = 60) -> Dict[str, Any]:
        """Моніторинг змін у папці"""
        try:
            if not os.path.isdir(directory):
                return {"success": False, "error": "❌ Директорія не існує"}
            
            initial_state = {}
            for item in Path(directory).rglob('*'):
                if item.is_file():
                    initial_state[str(item)] = {
                        "size": item.stat().st_size,
                        "mtime": item.stat().st_mtime
                    }
            
            print(f"🔍 Моніторинг {directory} протягом {duration} секунд...")
            time.sleep(duration)
            
            changes = {
                "added": [],
                "modified": [],
                "deleted": []
            }
            
            current_state = {}
            for item in Path(directory).rglob('*'):
                if item.is_file():
                    current_state[str(item)] = {
                        "size": item.stat().st_size,
                        "mtime": item.stat().st_mtime
                    }
            
            # Перевірка змін
            for path, info in current_state.items():
                if path not in initial_state:
                    changes["added"].append(path)
                elif info["mtime"] != initial_state[path]["mtime"]:
                    changes["modified"].append(path)
            
            for path in initial_state:
                if path not in current_state:
                    changes["deleted"].append(path)
            
            total_changes = len(changes["added"]) + len(changes["modified"]) + len(changes["deleted"])
            
            return {
                "success": True,
                "directory": directory,
                "duration_seconds": duration,
                "total_changes": total_changes,
                "changes": changes
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

# ============================================================================
# СТАТИСТИКА
# ============================================================================

class StatisticsManager:
    """Менеджер статистики та звітності"""
    
    def __init__(self, db=None):
        self.db = db
    
    def usage_statistics(self) -> Dict[str, Any]:
        """Статистика використання агента"""
        try:
            if not self.db:
                return {"success": False, "error": "❌ База даних недоступна"}
            
            history = self.db.get_command_history(limit=1000)
            
            total_commands = len(history)
            successful = sum(1 for h in history if h['success'])
            failed = total_commands - successful
            
            # Найпопулярніші команди
            command_counts = {}
            for h in history:
                cmd = h['command'].split()[0] if h['command'] else "unknown"
                command_counts[cmd] = command_counts.get(cmd, 0) + 1
            
            top_commands = sorted(command_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                "success": True,
                "total_commands": total_commands,
                "successful": successful,
                "failed": failed,
                "success_rate": f"{(successful / total_commands * 100):.1f}%" if total_commands > 0 else "0%",
                "top_commands": [{"command": cmd, "count": count} for cmd, count in top_commands]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def error_report(self) -> Dict[str, Any]:
        """Звіт про помилки"""
        try:
            if not self.db:
                return {"success": False, "error": "❌ База даних недоступна"}
            
            history = self.db.get_command_history(limit=500)
            errors = [h for h in history if not h['success']]
            
            # Групування помилок
            error_types = {}
            for error in errors:
                error_types[error['command']] = error_types.get(error['command'], 0) + 1
            
            return {
                "success": True,
                "total_errors": len(errors),
                "error_types": error_types,
                "recent_errors": errors[:10]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
