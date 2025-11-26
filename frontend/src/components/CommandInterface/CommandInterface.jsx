import React, { useState, useRef, useEffect } from 'react';
import { Send, Terminal, CheckCircle, XCircle, Clock } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';
import { Button } from '../ui/button';
import { commandAPI } from '../../services/api';

export function CommandInterface() {
    const [command, setCommand] = useState('');
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(false);
    const inputRef = useRef(null);

    useEffect(() => {
        // Load command history on mount
        commandAPI.getHistory(20)
            .then(res => {
                if (res.data.history) {
                    setHistory(res.data.history);
                }
            })
            .catch(err => console.error('Error loading history:', err));
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!command.trim() || loading) return;

        setLoading(true);
        const cmd = command.trim();
        setCommand('');

        try {
            const response = await commandAPI.execute(cmd);

            // Add to history
            setHistory(prev => [{
                command: cmd,
                result: response.data.response || response.data.error,
                success: response.data.success,
                timestamp: new Date().toISOString(),
            }, ...prev].slice(0, 50));

        } catch (error) {
            setHistory(prev => [{
                command: cmd,
                result: error.message,
                success: false,
                timestamp: new Date().toISOString(),
            }, ...prev]);
        } finally {
            setLoading(false);
            inputRef.current?.focus();
        }
    };

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-4xl font-bold">Command Center</h1>
                <p className="text-muted-foreground mt-2">
                    Execute commands through natural language
                </p>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Terminal className="h-5 w-5" />
                        Command Input
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit} className="flex gap-4">
                        <input
                            ref={inputRef}
                            type="text"
                            value={command}
                            onChange={(e) => setCommand(e.target.value)}
                            placeholder="Type a command... (e.g., 'show system info', 'search for *.py files')"
                            className="flex-1 bg-background border border-input rounded-md px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                            disabled={loading}
                        />
                        <Button type="submit" disabled={loading || !command.trim()}>
                            {loading ? (
                                <Clock className="h-4 w-4 animate-spin" />
                            ) : (
                                <>
                                    <Send className="h-4 w-4 mr-2" />
                                    Execute
                                </>
                            )}
                        </Button>
                    </form>
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>Command History</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-4 max-h-[600px] overflow-y-auto">
                        {history.length === 0 ? (
                            <p className="text-muted-foreground text-center py-8">
                                No commands executed yet. Try running a command above!
                            </p>
                        ) : (
                            history.map((item, index) => (
                                <div
                                    key={index}
                                    className="border rounded-lg p-4 bg-card hover:bg-accent/50 transition-colors"
                                >
                                    <div className="flex items-start justify-between mb-2">
                                        <div className="flex items-center gap-2">
                                            {item.success ? (
                                                <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                                            ) : (
                                                <XCircle className="h-4 w-4 text-red-500 flex-shrink-0" />
                                            )}
                                            <code className="text-sm font-mono bg-muted px-2 py-1 rounded">
                                                {item.command}
                                            </code>
                                        </div>
                                        <span className="text-xs text-muted-foreground">
                                            {new Date(item.timestamp).toLocaleTimeString()}
                                        </span>
                                    </div>
                                    <div className="ml-6 mt-2">
                                        <pre className="text-sm text-muted-foreground whitespace-pre-wrap">
                                            {item.result?.substring(0, 300)}
                                            {item.result?.length > 300 ? '...' : ''}
                                        </pre>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
