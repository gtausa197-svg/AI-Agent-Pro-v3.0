# 🚀 AI Local Agent - Web Interface Quick Start Guide

## 📋 Overview

Ви успішно створили **професійний веб-інтерфейс** для AI Local Agent!

**Що включено:**
- ✅ **Backend API** (FastAPI) з WebSocket
- ✅ **Frontend** (React + Vite + Tailwind CSS)
- ✅ **Dashboard** з real-time моніторингом
- ✅ **Command Interface** для виконання команд
- ✅ **Dark/Light теми**
- ✅ **Responsive дизайн**

---

## 🎯 Швидкий Старт

### Крок 1: Запустити Backend API

```bash
# Перейти в backend директорію
cd c:\Users\elev-n\Desktop\ai_local_agent\backend

# Створити virtual environment
python -m venv venv

# Активувати (Windows)
venv\Scripts\activate

# Встановити залежності
pip install -r requirements_api.txt

# Запустити сервер
python -m uvicorn api.main:app --reload --port 8000
```

**Перевірте:**
- API: http://localhost:8000
- Docs: http://localhost:8000/api/docs

### Крок 2: Запустити Frontend

```bash
# Відкрити НОВИЙ термінал
cd c:\Users\elev-n\Desktop\ai_local_agent\frontend

# Встановити Node.js залежності
npm install

# Запустити dev server
npm run dev
```

**Відкрийте браузер:**
http://localhost:5173

---

## 🎨 Що Ви Побачите

### Dashboard (/)
- 📊 **CPU, RAM, Disk** cards з live оновленням
- 📈 **Live charts** для моніторингу
- 🎯 **Quick actions** кнопки
- 🌐 **WebSocket** статус
- Автооновлення кожні 2 секунди!

### Command Center (/commands)
- 💬 **Command input** - вводите команду природною мовою
- 📜 **Command history** - всі виконані команди
- ✅ Іконки success/failure
- ⏱️ Timestamps

---

## 📁 Структура Проекту

```
ai_local_agent/
├── backend/
│   ├── api/
│   │   ├── main.py              # FastAPI app
│   │   ├── utils/
│   │   │   └── agent_bridge.py  # Інтеграція з AI агентом
│   │   └── __init__.py
│   ├── requirements_api.txt
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard/
│   │   │   │   ├── Dashboard.jsx
│   │   │   │   ├── SystemStats.jsx
│   │   │   │   └── LiveChart.jsx
│   │   │   ├── CommandInterface/
│   │   │   │   └── CommandInterface.jsx
│   │   │   └── ui/
│   │   │       ├── card.jsx
│   │   │       ├── button.jsx
│   │   │       └── progress.jsx
│   │   ├── hooks/
│   │   │   └── useWebSocket.js
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── store/
│   │   │   └── store.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── README.md
│
└── (ваші існуючі файли)
```

---

## 🔌 API Endpoints

### System
```
GET  /api/system/info       # Повна інформація
GET  /api/system/stats      # CPU, RAM, Disk %
GET  /api/system/processes  # Список процесів
```

### Commands
```
POST /api/commands/execute?command=...  # Виконати команду
GET  /api/commands/history?limit=50     # Історія команд
```

### Files
```
GET /api/files/search?pattern=*.py&limit=100
```

### WebSocket
```
WS /ws  # Real-time stats (кожні 2 сек)
```

---

## 🎯 Тестування

### 1. Перевірити Backend

```bash
# System stats
curl http://localhost:8000/api/system/stats

# Execute command
curl -X POST "http://localhost:8000/api/commands/execute?command=system_info"
```

### 2. Перевірити Frontend

1. Відкрити http://localhost:5173
2. Перевірити Dashboard - повинні бути stats cards
3. Натиснути Commands
4. Ввести команду: `show system info`
5. Натиснути Execute
6. Побачити результат в історії!

### 3. Перевірити WebSocket

1. Відкрити DevTools → Network → WS tab
2. Переконатися що з'єднання активне
3. Побачити повідомлення кожні 2 секунди
4. Stats cards повинні оновлюватися live!

---

## 🎨 Features

### ✨ Реалізовано:
- ✅ Real-time Dashboard з CPU/RAM/Disk
- ✅ Live charts (Recharts)
- ✅ Command execution через API
- ✅ Command history з пошуком
- ✅ WebSocket для live updates
- ✅ Dark/Light theme toggle
- ✅ Responsive design
- ✅ Beautiful UI (Tailwind CSS)
- ✅ Error handling
- ✅ Loading states

### 🚧 Для подальшого розвитку:
- ⏳ File Manager з tree view
- ⏳ System Monitor з процесами
- ⏳ Auto-complete для команд
- ⏳ Notifications
- ⏳ Keyboard shortcuts (Ctrl+K)
- ⏳ File upload/download

---

## 🛠️ Налаштування

### Backend Port

Змінити в `backend/api/main.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8000)  # Змінити 8000
```

### Frontend Port

Змінити в `frontend/vite.config.js`:
```javascript
server: {
  port: 5173  // Змінити тут
}
```

### Theme Colors

Редагувати `frontend/src/index.css` - змінити CSS variables:
```css
:root {
  --primary: 221.2 83.2% 53.3%;  /* Змінити */
}
```

---

## 🐛 Troubleshooting

### Backend Помилки

**ImportError: No module named 'fastapi'**
```bash
cd backend
pip install -r requirements_api.txt
```

**Can't import ai_agent modules**
- Переконайтеся що `ai_agent.py` існує в кореневій директорії
- Перевірте `sys.path` в `agent_bridge.py`

### Frontend Помилки

**npm install fails**
```bash
# Видалити node_modules
rm -rf node_modules package-lock.json
npm install
```

**WebSocket не підключається**
- Переконайтеся backend запущений на порту 8000
- Перевірте CORS налаштування в `main.py`
- Відкрийте DevTools → Console для помилок

**Білий екран**
- Перевірте console errors
- Запустіть `npm run dev` знову
- Очистіть browser cache

---

## 📚 Команди

### Backend
```bash
# Development
python -m uvicorn api.main:app --reload

# Production
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
# Development
npm run dev

# Build для production
npm run build

# Preview production build
npm run preview
```

---

## 🎉 Готово!

Ваш веб-інтерфейс готовий до використання!

**Що далі?**
1. ✅ Додати File Manager
2. ✅ Додати System Monitor
3. ✅ Додати Authentication
4. ✅ Деплой на сервер

**Потрібна допомога?**
- Backend README: `backend/README.md`
- Frontend README: `frontend/README.md`
- API Docs: http://localhost:8000/api/docs

---

**Приємного використання! 🚀**
