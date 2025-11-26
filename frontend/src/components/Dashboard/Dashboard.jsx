import React from 'react';
import { useWebSocket } from '../../hooks/useWebSocket';
import { SystemStats } from './SystemStats';
import { LiveChart } from './LiveChart';
import { Activity, Wifi, WifiOff } from 'lucide-react';

export function Dashboard() {
    const { data: wsData, connected } = useWebSocket('ws://localhost:8000/ws');

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-4xl font-bold">Dashboard</h1>
                    <p className="text-muted-foreground mt-2">
                        Real-time system monitoring and control
                    </p>
                </div>
                <div className="flex items-center gap-2">
                    {connected ? (
                        <>
                            <Wifi className="h-5 w-5 text-green-500" />
                            <span className="text-sm text-green-500">Connected</span>
                        </>
                    ) : (
                        <>
                            <WifiOff className="h-5 w-5 text-red-500" />
                            <span className="text-sm text-red-500">Disconnected</span>
                        </>
                    )}
                </div>
            </div>

            {/* System Stats Cards */}
            <SystemStats stats={wsData?.data} />

            {/* Live Chart */}
            <LiveChart data={wsData} />

            {/* Quick Info */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-card border rounded-lg p-6">
                    <div className="flex items-center gap-3 mb-4">
                        <Activity className="h-6 w-6 text-primary" />
                        <h3 className="text-lg font-semibold">System Status</h3>
                    </div>
                    <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                            <span className="text-muted-foreground">WebSocket</span>
                            <span className={connected ? 'text-green-500' : 'text-red-500'}>
                                {connected ? 'Active' : 'Inactive'}
                            </span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-muted-foreground">API</span>
                            <span className="text-green-500">Running</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-muted-foreground">Agent</span>
                            <span className="text-green-500">Ready</span>
                        </div>
                    </div>
                </div>

                <div className="bg-card border rounded-lg p-6">
                    <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
                    <div className="grid grid-cols-2 gap-3">
                        <button className="bg-primary text-primary-foreground hover:bg-primary/90 rounded-md p-3 text-sm font-medium transition-colors">
                            Scan Files
                        </button>
                        <button className="bg-secondary text-secondary-foreground hover:bg-secondary/80 rounded-md p-3 text-sm font-medium transition-colors">
                            Cleanup
                        </button>
                        <button className="bg-secondary text-secondary-foreground hover:bg-secondary/80 rounded-md p-3 text-sm font-medium transition-colors">
                            Backup
                        </button>
                        <button className="bg-secondary text-secondary-foreground hover:bg-secondary/80 rounded-md p-3 text-sm font-medium transition-colors">
                            Optimize
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
