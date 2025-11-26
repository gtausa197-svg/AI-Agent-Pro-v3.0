import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Home, Terminal, Moon, Sun, Menu } from 'lucide-react';
import { Dashboard } from './components/Dashboard/Dashboard';
import { CommandInterface } from './components/CommandInterface/CommandInterface';
import { useStore } from './store/store';
import './index.css';

function Navigation() {
    const location = useLocation();
    const { theme, toggleTheme } = useStore();
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    const links = [
        { path: '/', name: 'Dashboard', icon: Home },
        { path: '/commands', name: 'Commands', icon: Terminal },
    ];

    return (
        <nav className="bg-card border-b">
            <div className="container mx-auto px-4">
                <div className="flex items-center justify-between h-16">
                    <div className="flex items-center gap-8">
                        <h1 className="text-xl font-bold bg-gradient-to-r from-blue-500 to-purple-500 bg-clip-text text-transparent">
                            🤖 AI Local Agent
                        </h1>
                        <div className="hidden md:flex gap-4">
                            {links.map(({ path, name, icon: Icon }) => (
                                <Link
                                    key={path}
                                    to={path}
                                    className={`flex items-center gap-2 px-4 py-2 rounded-md transition-colors ${location.pathname === path
                                            ? 'bg-primary text-primary-foreground'
                                            : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                                        }`}
                                >
                                    <Icon className="h-4 w-4" />
                                    {name}
                                </Link>
                            ))}
                        </div>
                    </div>

                    <div className="flex items-center gap-4">
                        <button
                            onClick={toggleTheme}
                            className="p-2 rounded-md hover:bg-accent transition-colors"
                            aria-label="Toggle theme"
                        >
                            {theme === 'dark' ? (
                                <Sun className="h-5 w-5" />
                            ) : (
                                <Moon className="h-5 w-5" />
                            )}
                        </button>

                        <button
                            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                            className="md:hidden p-2 rounded-md hover:bg-accent transition-colors"
                        >
                            <Menu className="h-5 w-5" />
                        </button>
                    </div>
                </div>

                {/* Mobile menu */}
                {mobileMenuOpen && (
                    <div className="md:hidden py-4 space-y-2">
                        {links.map(({ path, name, icon: Icon }) => (
                            <Link
                                key={path}
                                to={path}
                                onClick={() => setMobileMenuOpen(false)}
                                className={`flex items-center gap-2 px-4 py-2 rounded-md transition-colors ${location.pathname === path
                                        ? 'bg-primary text-primary-foreground'
                                        : 'text-muted-foreground hover:bg-accent'
                                    }`}
                            >
                                <Icon className="h-4 w-4" />
                                {name}
                            </Link>
                        ))}
                    </div>
                )}
            </div>
        </nav>
    );
}

function App() {
    const { theme } = useStore();

    useEffect(() => {
        // Apply theme to document
        if (theme === 'dark') {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
    }, [theme]);

    return (
        <Router>
            <div className="min-h-screen bg-background text-foreground">
                <Navigation />
                <main className="container mx-auto px-4 py-8">
                    <Routes>
                        <Route path="/" element={<Dashboard />} />
                        <Route path="/commands" element={<CommandInterface />} />
                    </Routes>
                </main>
            </div>
        </Router>
    );
}

export default App;
