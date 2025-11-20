"""
Інтеграційний скрипт для запуску AI-агента з розширеними функціями
Просто запустіть цей файл замість ai_agent.py
"""

import sys
from pathlib import Path

# Додаємо поточну директорію в шлях пошуку
sys.path.insert(0, str(Path(__file__).parent))

# Завантажуємо розширені функції
try:
    from extended_features import (
        MultimediaManager,
        SystemUtilities,
        MonitoringManager,
        NetworkUtilities,
        AutomationManager,
        StatisticsManager
    )
    EXTENDED_AVAILABLE = True
    print("✅ Розширені функції завантажено!")
except ImportError as e:
    EXTENDED_AVAILABLE = False
    print(f"⚠️  Розширені функції недоступні: {e}")
    print("💡 Встановіть: pip install Pillow pyperclip plyer")

# Імпортуємо оригінальний агент
try:
    import ai_agent
    
    # Патч класу AIAgent для додавання нових функцій
    original_init = ai_agent.AIAgent.__init__
    
    def new_init(self):
        # Викликаємо оригінальний __init__
        original_init(self)
        
        # Додаємо нові менеджери якщо доступні
        if EXTENDED_AVAILABLE:
            self.multimedia = MultimediaManager(ai_agent.Config.SCREENSHOTS_DIR)
            self.system_utils = SystemUtilities()
            self.monitoring = MonitoringManager(self.db)
            self.network_utils = NetworkUtilities()
            self.automation = AutomationManager(self.db)
            self.statistics = StatisticsManager(self.db)
            print("✅ Нові менеджери ініціалізовано!")
        
    # Патч методу handle_direct_command
    original_handle = ai_agent.AIAgent.handle_direct_command
    
    def new_handle_direct_command(self, user_input: str):
        # Спочатку викликаємо оригінальну обробку
        result = original_handle(self, user_input)
        
        # Якщо команда не розпізнана і розширення доступні - перевіряємо нові команди
        if result is None and EXTENDED_AVAILABLE and hasattr(self, 'multimedia'):
            try:
                import shlex
                parts = shlex.split(user_input, posix=False)
            except ValueError:
                return None
            
            if not parts:
                return None
            
            cmd = parts[0].lower()
            args = parts[1:]
            
            # Обробка нових команд
            if cmd == "take_screenshot":
                filename = args[0] if args else None
                res = self.multimedia.take_screenshot(filename)
                if not res.get("success"):
                    return res.get("error", "❌ Помилка")
                return f"📸 Скріншот: {res['filepath']} ({res['size_kb' ]}, {res['resolution']})"
            
            elif cmd == "clipboard_get":
                res = self.system_utils.clipboard_get()
                if not res.get("success"):
                    return res.get("error")
                content = res.get("content", "")
                preview = content[:200] + "..." if len(content) > 200 else content
                return f"📋 Буфер ({res['length']} символів):\n{preview}"
            
            elif cmd == "clipboard_set":
                if not args:
                    return "❌ Використання: clipboard_set <текст>"
                text = " ".join(args)
                res = self.system_utils.clipboard_set(text)
                return res.get("message") if res.get("success") else res.get("error")
            
            elif cmd == "send_notification":
                if len(args) < 2:
                    return "❌ Використання: send_notification <заголовок> <текст>"
                title, message = args[0], " ".join(args[1:])
                res = self.system_utils.send_notification(title, message)
                return res.get("message") if res.get("success") else res.get("error")
            
            elif cmd == "auto_cleanup":
                res = self.system_utils.auto_cleanup()
                if not res.get("success"):
                    return res.get("error")
                return f"🧹 Видалено: {res['cleaned_files']} файлів, звільнено: {res['freed_space_mb']}"
            
            elif cmd == "monitor_performance":
                duration = int(args[0]) if args else 60
                print(f"⏳ Моніторинг {duration} сек...")
                res = self.monitoring.monitor_performance(duration)
                if not res.get("success"):
                    return res.get("error")
                msg = f"📊 CPU: {res['average']['cpu']}, RAM: {res['average']['memory']}"
                if res.get('alerts'):
                    msg += "\n⚠️ " + "\n".join(res['alerts'])
                return msg
            
            elif cmd == "system_report":
                res = self.monitoring.system_report()
                if not res.get("success"):
                    return res.get("error")
                return "💻 Системний звіт:\n" + self._json(res['report'])
            
            elif cmd == "speedtest":
                print("⏳ Тестування швидкості...")
                res = self.network_utils.speedtest()
                if not res.get("success"):
                    return res.get("error")
                return f"🌐 Download: {res['download_speed_mbps']}, Ping: {res['ping_ms']}"
            
            elif cmd == "check_website_status":
                if not args:
                    return "❌ Використання: check_website_status <url>"
                res = self.network_utils.check_website_status(args[0])
                return f"🌍 {res.get('url')}: {res.get('status')}"
            
            elif cmd == "backup_files":
                if len(args) < 2:
                    return "❌ Використання: backup_files <джерело> <призначення>"
                res = self.automation.backup_files(args[0], args[1])
                if not res.get("success"):
                    return res.get("error")
                return f"💾 Бекап: {res['files_backed_up']} файлів, {res['backup_size_mb']}"
            
            elif cmd == "usage_statistics":
                res = self.statistics.usage_statistics()
                if not res.get("success"):
                    return res.get("error")
                return f"📊 Команд: {res['total_commands']}, Успішність: {res['success_rate']}"
            
            elif cmd == "error_report":
                res = self.statistics.error_report()
                if not res.get("success"):
                    return res.get("error")
                return f"❌ Помилок: {res['total_errors']}"
            
            elif cmd == "help" and EXTENDED_AVAILABLE:
                return original_handle(self, user_input) + """

🎨 РОЗШИРЕНІ КОМАНДИ (50+ нових):
- take_screenshot [ім'я]          - Скріншот
- clipboard_get / clipboard_set   - Буфер обміну
- send_notification <title> <msg> - Сповіщення
- auto_cleanup                    - Очищення системи
- monitor_performance [сек]       - Моніторинг
- system_report                   - Системний звіт
- speedtest                       - Тест швидкості
- check_website_status <url>      - Статус сайту
- backup_files <src> <dst>        - Резервна копія
- usage_statistics                - Статистика
- error_report                    - Звіт про помилки

Повний список: дивіться НОВI_ФУНКЦІЇ.md
"""
        
        return result
    
    # Застосовуємо патчі
    ai_agent.AIAgent.__init__ = new_init
    ai_agent.AIAgent.handle_direct_command = new_handle_direct_command
    
    print("🚀 AI-Агент готовий з розширеними функціями!")
    
    # Запускаємо агент
    if __name__ == "__main__":
        ai_agent.setup_logging()
        try:
            agent = ai_agent.AIAgent()
            agent.interactive_mode()
        except Exception as e:
            print(f"❌ Помилка: {e}")
            ai_agent.logging.critical(f"Failed to start agent: {e}")

except ImportError as e:
    print(f"❌ Не вдалося імпортувати ai_agent.py: {e}")
    print("Переконайтеся, що файл ai_agent.py знаходиться в тій же папці!")
    sys.exit(1)
