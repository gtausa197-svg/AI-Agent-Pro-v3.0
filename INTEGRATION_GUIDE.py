"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║              📖 ІНСТРУКЦІЇ ПО ІНТЕГРАЦІЇ НОВИХ ФУНКЦІЙ                   ║
║                    в ai_agent.py                                          ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

⚠️ УВАГА: Це файл-інструкція! Не запускайте його напряму!
   Копіюйте фрагменти коду звідси в ваш ai_agent.py

═══════════════════════════════════════════════════════════════════════════
"""

r"""

# ============================================================================
# КРОК 1: Додайте імпорти на початку ai_agent.py
# ============================================================================

# Додайте до існуючих імпортів:
from extended_features import (
    MultimediaManager,
    SystemUtilities,
    MonitoringManager,
    NetworkUtilities,
    AutomationManager,
    StatisticsManager
)

# ============================================================================
# КРОК 2: Оновіть клас AIAgent
# ============================================================================

# У методі __init__ класу AIAgent додайте:
def __init__(self):
    # ... існуючий код ...
    
    # НОВІ МЕНЕДЖЕРИ
    self.multimedia = MultimediaManager(Config.SCREENSHOTS_DIR)
    self.system_utils = SystemUtilities()
    self.monitoring = MonitoringManager(self.db)
    self.network_utils = NetworkUtilities()
    self.automation = AutomationManager(self.db)
    self.statistics = StatisticsManager(self.db)

# ============================================================================
# КРОК 3: Додайте нові команди в handle_direct_command
# ============================================================================

# У методі handle_direct_command додайте в список known_commands:
known_commands = {
    # ... існуючі команди ...
    
    # МУЛЬТИМЕДІА
    "take_screenshot", "compress_image", "record_screen",
    
    # СИСТЕМНІ УТИЛІТИ
    "clipboard_get", "clipboard_set", "send_notification",
    "auto_cleanup", "kill_frozen_apps", "optimize_memory",
    
    # МОНІТОРИНГ
    "monitor_performance", "log_analyzer", "system_report",
    
    # МЕРЕЖА
    "speedtest", "check_website_status", "monitor_url",
    
    # АВТОМАТИЗАЦІЯ
    "backup_files", "schedule_task", "watch_directory",
    
    # СТАТИСТИКА
    "usage_statistics", "error_report",
    
    # БЕЗПЕКА
    "encrypt_file", "decrypt_file", "secure_delete", "find_old_files",
    
    # АРХІВИ
    "compress_archive", "extract_archive"
}

# ============================================================================
# КРОК 4: Додайте обробку нових команд
# ============================================================================

# Додайте ці блоки коду перед return None в handle_direct_command:

# --- МУЛЬТИМЕДІА ---
if cmd == "take_screenshot":
    filename = args[0] if args else None
    res = self.multimedia.take_screenshot(filename)
    if not res.get("success"):
        return res.get("error", "❌ Помилка")
    return f"📸 Скріншот збережено:\n- Файл: {res['filepath']}\n- Розмір: {res['size_kb']}\n- Роздільність: {res['resolution']}"

if cmd == "compress_image":
    if not args:
        return "❌ Використання: compress_image <шлях> [якість]"
    filepath = args[0]
    quality = int(args[1]) if len(args) > 1 else 85
    res = self.multimedia.compress_image(filepath, quality)
    if not res.get("success"):
        return res.get("error", "❌ Помилка")
    return f"🗜️ Зображення стиснуто:\n- Оригінал: {res['original_size_kb']}\n- Стиснуто: {res['compressed_size_kb']}\n- Заощаджено: {res['savings_percent']}\n- Файл: {res['output_path']}"

# --- СИСТЕМНІ УТИЛІТИ ---
if cmd == "clipboard_get":
    res = self.system_utils.clipboard_get()
    if not res.get("success"):
        return res.get("error", "❌ Помилка")
    content = res.get("content", "")
    preview = content[:200] + "..." if len(content) > 200 else content
    return f"📋 Буфер обміну ({res['length']} символів):\n{preview}"

if cmd == "clipboard_set":
    if not args:
        return "❌ Використання: clipboard_set <текст>"
    text = " ".join(args)
    res = self.system_utils.clipboard_set(text)
    return res.get("message") if res.get("success") else res.get("error", "❌ Помилка")

if cmd == "send_notification":
    if len(args) < 2:
        return "❌ Використання: send_notification <заголовок> <текст>"
    title = args[0]
    message = " ".join(args[1:])
    res = self.system_utils.send_notification(title, message)
    return res.get("message") if res.get("success") else res.get("error", "❌ Помилка")

if cmd == "auto_cleanup":
    res = self.system_utils.auto_cleanup()
    if not res.get("success"):
        return res.get("error", "❌ Помилка")
    msg = f"🧹 Очищення завершено:\n- Видалено файлів: {res['cleaned_files']}\n- Звільнено: {res['freed_space_mb']}"
    if res.get('errors'):
        msg += f"\n⚠️ Помилок: {len(res['errors'])}"
    return msg

if cmd == "kill_frozen_apps":
    res = self.system_utils.kill_frozen_apps()
    if not res.get("success"):
        return res.get("error", "❌ Помилка")
    if res['count'] == 0:
        return "✅ Завислих програм не знайдено"
    return f"✅ Закрито завислих програм: {res['count']}\n" + "\n".join(res['terminated'])

if cmd == "optimize_memory":
    res = self.system_utils.optimize_memory()
    if not res.get("success"):
        return res.get("error", "❌ Помилка")
    return f"🚀 Оптимізація пам'яті:\n- Початково: {res['initial_usage']}\n- Після: {res['final_usage']}\n- Звільнено: {res['freed_mb']}"

# --- МОНІТОРИНГ ---
if cmd == "monitor_performance":
    duration = 60
    if args:
        try:
            duration = int(args[0])
        except ValueError:
            return "❌ Тривалість має бути числом (секунди)"
    print(f"⏳ Моніторинг системи протягом {duration} секунд...")
    res = self.monitoring.monitor_performance(duration)
    if not res.get("success"):
        return res.get("error", "❌ Помилка")
    msg = f"📊 Моніторинг завершено:\n- Зразків: {res['samples']}\n"
    msg += f"- Середній CPU: {res['average']['cpu']}\n"
    msg += f"- Середня RAM: {res['average']['memory']}\n"
    msg += f"- Піковий CPU: {res['peak']['cpu']}\n"
    msg += f"- Пікова RAM: {res['peak']['memory']}"
    if res.get('alerts'):
        msg += "\n\n⚠️ ПОПЕРЕДЖЕННЯ:\n" + "\n".join(res['alerts'])
    return msg

if cmd == "log_analyzer":
    path = args[0] if args else "logs"
    res = self.monitoring.log_analyzer(path)
    if not res.get("success"):
        return res.get("error", "❌ Помилка")
    msg = f"📝 Аналіз логів:\n- Файлів: {res['files_analyzed']}\n"
    msg += f"- Помилок: {res['errors']}\n- Попреджень: {res['warnings']}\n"
    msg += f"- Інфо: {res['info_messages']}"
    if res.get('recent_errors'):
        msg += "\n\nОстанні помилки:\n" + "\n".join(res['recent_errors'][:5])
    return msg

if cmd == "system_report":
    res = self.monitoring.system_report()
    if not res.get("success"):
        return res.get("error", "❌ Помилка")
    return "💻 Системний звіт:\n" + self._json(res['report'])

# --- МЕРЕЖА ---
if cmd == "speedtest":
    print("⏳ Тестування швидкості інтернету...")
    res = self.network_utils.speedtest()
    if not res.get("success"):
        return res.get("error", "❌ Помилка")
    return f"🌐 Тест швидкості:\n- Завантаження: {res['download_speed_mbps']}\n- Ping: {res['ping_ms']}"

if cmd == "check_website_status":
    if not args:
        return "❌ Використання: check_website_status <url>"
    url = args[0]
    res = self.network_utils.check_website_status(url)
    msg = f"🌍 Статус сайту {res.get('url', url)}:\n"
    msg += f"- Статус: {res.get('status', 'Невідомо')}"
    if res.get('success'):
        msg += f"\n- Код: {res['status_code']}\n- Час відповіді: {res['response_time_ms']}\n- Сервер: {res['server']}"
    return msg

# --- АВТОМАТИЗАЦІЯ ---
if cmd == "backup_files":
    if len(args) < 2:
        return "❌ Використання: backup_files <джерело> <призначення>"
    res = self.automation.backup_files(args[0], args[1])
    if not res.get("success"):
        return res.get("error", "❌ Помилка")
    return f"💾 Резервна копія створена:\n- Шлях: {res['backup_path']}\n- Файлів: {res['files_backed_up']}\n- Розмір: {res['backup_size_mb']}"

if cmd == "schedule_task":
    if len(args) < 4:
        return "❌ Використання: schedule_task <назва> <команда> <час> <тип>"
    task_name, command, schedule_time, schedule_type = args[0], args[1], args[2], args[3]
    res = self.automation.schedule_task(task_name, command, schedule_time, schedule_type)
    return res.get("message") if res.get("success") else res.get("error", "❌ Помилка")

if cmd == "watch_directory":
    if not args:
        return "❌ Використання: watch_directory <шлях> [тривалість_секунд]"
    directory = args[0]
    duration = int(args[1]) if len(args) > 1 else 60
    res = self.automation.watch_directory(directory, duration)
    if not res.get("success"):
        return res.get("error", "❌ Помилка")
    changes = res['changes']
    msg = f"👁️ Моніторинг завершено:\n- Змін: {res['total_changes']}\n"
    msg += f"- Додано: {len(changes['added'])}\n"
    msg += f"- Змінено: {len(changes['modified'])}\n"
    msg += f"- Видалено: {len(changes['deleted'])}"
    return msg

# --- СТАТИСТИКА ---
if cmd == "usage_statistics":
    res = self.statistics.usage_statistics()
    if not res.get("success"):
        return res.get("error", "❌ Помилка")
    msg = f"📊 Статистика використання:\n- Всього команд: {res['total_commands']}\n"
    msg += f"- Успішних: {res['successful']}\n- Невдалих: {res['failed']}\n"
    msg += f"- Успішність: {res['success_rate']}\n\nТоп команд:\n"
    for tc in res['top_commands'][:5]:
        msg += f"- {tc['command']}: {tc['count']}\n"
    return msg

if cmd == "error_report":
    res = self.statistics.error_report()
    if not res.get("success"):
        return res.get("error", "❌ Помилка")
    return "❌ Звіт про помилки:\n" + self._json(res)

# --- БЕЗПЕКА ---
if cmd == "encrypt_file":
    if len(args) < 2:
        return "❌ Використання: encrypt_file <шлях> <пароль>"
    res = self.fs_manager.encrypt_file(args[0], args[1])
    return res.get("message") if res.get("success") else res.get("error", "❌ Помилка")

if cmd == "decrypt_file":
    if len(args) < 2:
        return "❌ Використання: decrypt_file <шлях> <пароль>"
    res = self.fs_manager.decrypt_file(args[0], args[1])
    return res.get("message") if res.get("success") else res.get("error", "❌ Помилка")

if cmd == "secure_delete":
    if not args:
        return "❌ Використання: secure_delete <шлях>"
    res = self.fs_manager.secure_delete(args[0])
    return res.get("message") if res.get("success") else res.get("error", "❌ Помилка")

if cmd == "find_old_files":
    if not args:
        return "❌ Використання: find_old_files <шлях> [дні]"
    directory = args[0]
    days = int(args[1]) if len(args) > 1 else 365
    res = self.fs_manager.find_old_files(directory, days)
    if not res.get("success"):
        return res.get("error", "❌ Помилка")
    if res['count'] == 0:
        return f"ℹ️ Файлів старше {days} днів не знайдено"
    files_list = [f"{f['path']} ({f['modified']})" for f in res['files'][:10]]
    return f"📁 Знайдено старих файлів: {res['count']}\n" + "\n".join(files_list)

# --- АРХІВИ ---
if cmd == "compress_archive":
    if len(args) < 2:
        return "❌ Використання: compress_archive <джерела...> <архів.zip>"
    sources = args[:-1]
    archive = args[-1]
    res = self.fs_manager.compress_archive(sources, archive)
    return res.get("message") if res.get("success") else res.get("error", "❌ Помилка")

if cmd == "extract_archive":
    if len(args) < 2:
        return "❌ Використання: extract_archive <архів> <призначення>"
    res = self.fs_manager.extract_archive(args[0], args[1])
    return res.get("message") if res.get("success") else res.get("error", "❌ Помилка")

# ============================================================================
# КРОК 5: Оновіть системний контекст в LMStudioClient.build_system_context()
# ============================================================================

# Додайте нові команди до списку можливостей (вже включено в extended_features.py)

# ============================================================================
# ГОТОВО!
# ============================================================================
"""

# Цей блок виконується, якщо файл запускається напряму
if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║              📖 ІНСТРУКЦІЇ ПО ІНТЕГРАЦІЇ                                 ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

✅ Інструкції по інтеграції готові!

Для застосування нових функцій:
1. Скопіюйте код вище в відповідні місця ai_agent.py
2. Встановіть залежності: pip install Pillow pyperclip plyer
3. Перезапустіть агента

Або використайте готовий файл ai_agent_extended.py як основу!
""")
