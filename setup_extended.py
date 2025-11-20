"""
Швидке налаштування AI-Агента v3.0
Автоматичне встановлення залежностей та перевірка системи
"""

import subprocess
import sys
import os
from pathlib import Path

def print_section(title):
    """Друкує секцію"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def check_python_version():
    """Перевірка версії Python"""
    print_section("Перевірка Python")
    version = sys.version_info
    print(f"Версія Python: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Потрібна Python 3.8 або новіша!")
        return False
    print("✅ Версія Python підходить")
    return True

def install_packages():
    """Встановлення пакетів"""
    print_section("Встановлення залежностей")
    
    # Основні пакети
    basic_packages = [
        "psutil",
        "requests"
    ]
    
    # Розширені пакети
    extended_packages = [
        "Pillow",
        "pyperclip",
        "plyer"
    ]
    
    # Windows специфічні
    windows_packages = [
        "win10toast"
    ]
    
    all_packages = basic_packages + extended_packages
    
    if sys.platform == "win32":
        all_packages += windows_packages
    
    print(f"\n📦 Буде встановлено {len(all_packages)} пакетів...")
    print("Пакети:", ", ".join(all_packages))
    
    choice = input("\n❓ Продовжити встановлення? (y/n): ").strip().lower()
    if choice != 'y':
        print("❌ Встановлення скасовано")
        return False
    
    print("\n⏳ Встановлення...")
    
    failed = []
    for package in all_packages:
        try:
            print(f"\n📥 Встановлення {package}...")
            subprocess.check_call([
                sys.executable, 
                "-m", 
                "pip", 
                "install", 
                "--upgrade",
                package
            ], stdout=subprocess.DEVNULL)
            print(f"✅ {package} встановлено")
        except subprocess.CalledProcessError:
            print(f"❌ Не вдалося встановити {package}")
            failed.append(package)
    
    if failed:
        print(f"\n⚠️ Не встановлено: {', '.join(failed)}")
        print("Спробуйте встановити вручну:")
        print(f"pip install {' '.join(failed)}")
        return False
    
    print("\n✅ Всі пакети встановлено успішно!")
    return True

def check_directories():
    """Перевірка та створення директорій"""
    print_section("Перевірка директорій")
    
    base_dir = Path(__file__).parent
    
    dirs_to_create = [
        "logs",
        "knowledge_base",
        "cache",
        "backups",
        "screenshots",
        "recordings",
        "archives",
        "temp"
    ]
    
    for dir_name in dirs_to_create:
        dir_path = base_dir / dir_name
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"📁 Створено: {dir_name}/")
        else:
            print(f"✅ Існує: {dir_name}/")
    
    print("\n✅ Всі директорії готові")
    return True

def test_imports():
    """Тест імпортів"""
    print_section("Тестування імпортів")
    
    imports_to_test = [
        ("psutil", "Системний моніторинг"),
        ("requests", "HTTP запити"),
        ("PIL", "Робота з зображеннями"),
        ("pyperclip", "Буфер обміну"),
        ("plyer", "Системні сповіщення")
    ]
    
    failed = []
    for module_name, description in imports_to_test:
        try:
            __import__(module_name)
            print(f"✅ {description:30} ({module_name})")
        except ImportError:
            print(f"❌ {description:30} ({module_name}) - НЕ ВСТАНОВЛЕНО")
            failed.append(module_name)
    
    if failed:
        print(f"\n⚠️ Деякі модулі не встановлено: {', '.join(failed)}")
        print("Функції, що використовують ці модулі, не будуть доступні")
        return False
    
    print("\n✅ Всі модулі імпортуються успішно")
    return True

def show_summary():
    """Підсумок"""
    print_section("Інформація про агента")
    
    print("""
🤖 AIAgent Pro v3.0 - Готовий до роботи!

📋 ДОСТУПНІ ФАЙЛИ:
- ai_agent.py                 - Основний агент (оригінальна версія)
- extended_features.py         - Розширені функції (новий модуль)
- НОВI_ФУНКЦІЇ.md              - Документація нових функцій
- INTEGRATION_GUIDE.py         - Інструкції по інтеграції
- requirements_extended.txt    - Список залежностей

🚀 ШВИДКИЙ СТАРТ:

1. Запустіть LM Studio на http://localhost:1234
2. Запустіть агента:
   python ai_agent.py

3. Для використання нових функцій:
   - Імпортуйте модуль extended_features.py
   - Або відкрийте INTEGRATION_GUIDE.py для інструкцій

📚 ДОКУМЕНТАЦІЯ:
   Відкрийте НОВI_ФУНКЦІЇ.md для переліку всіх функцій

💡 ПРИКЛАДИ КОМАНД:
   - take_screenshot               - Зробити скріншот
   - system_report                 - Системний звіт
   - auto_cleanup                  - Очистити систему
   - monitor_performance 60        - Моніторинг 60 сек
   - backup_files C:\\Docs C:\\Backup - Резервна копія

⚙️ НАЛАШТУВАННЯ:
   Відредагуйте Config клас в ai_agent.py для зміни параметрів

""")

def main():
    """Головна функція"""
    print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║          🤖 AI-АГЕНТ v3.0 - НАЛАШТУВАННЯ                  ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
""")
    
    # Перевірки
    if not check_python_version():
        return
    
    if not check_directories():
        return
    
    # Встановлення
    choice = input("\n❓ Встановити/оновити залежності? (y/n): ").strip().lower()
    if choice == 'y':
        install_packages()
    
    # Тест
    test_imports()
    
    # Підсумок
    show_summary()
    
    print("\n✅ Налаштування завершено!\n")
    input("Натисніть Enter для виходу...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Перервано користувачем")
    except Exception as e:
        print(f"\n❌ Помилка: {e}")
        input("Натисніть Enter для виходу...")
