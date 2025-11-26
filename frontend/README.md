# 🌐 AI Local Agent - Web Interface

## Quick Start

### Prerequisites
- Node.js 18+ installed
- Backend API running on port 8000

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

Visit: http://localhost:5173

### Build for Production

```bash
npm run build
npm run preview
```

## Features

- ✅ **Real-time Dashboard** - Live CPU, RAM, Disk monitoring
- ✅ **Live Charts** - Interactive performance graphs
- ✅ **Command Interface** - Natural language command execution
- ✅ **Command History** - View all executed commands
- ✅ **Dark/Light Theme** - Toggle between themes
- ✅ **Responsive Design** - Works on desktop and mobile
- ✅ **WebSocket** - Real-time updates every 2 seconds

## Tech Stack

- **React 18** - UI library
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Recharts** - Charts
- **Zustand** - State management
- **Axios** - HTTP client
- **React Router** - Routing

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Dashboard/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── SystemStats.jsx
│   │   │   └── LiveChart.jsx
│   │   ├── CommandInterface/
│   │   │   └── CommandInterface.jsx
│   │   └── ui/
│   │       ├── card.jsx
│   │       ├── button.jsx
│   │       └── progress.jsx
│   ├── hooks/
│   │   └── useWebSocket.js
│   ├── services/
│   │   └── api.js
│   ├── store/
│   │   └── store.js
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── package.json
└── vite.config.js
```

## Available Pages

- `/` - Dashboard with real-time stats
- `/commands` - Command execution interface

## API Endpoints Used

- `GET /api/system/stats` - System statistics
- `POST /api/commands/execute` - Execute command
- `GET /api/commands/history` - Command history
- `WS /ws` - WebSocket for live updates

## Customization

### Theme

Edit `src/index.css` to customize colors.

### Add New Page

1. Create component in `src/components/`
2. Add route in `src/App.jsx`
3. Add navigation link

## Troubleshooting

**WebSocket not connecting?**
- Ensure backend is running on port 8000
- Check browser console for errors

**Styles not loading?**
- Run `npm install` again
- Clear browser cache

**API errors?**
- Verify backend is running
- Check CORS settings in backend
