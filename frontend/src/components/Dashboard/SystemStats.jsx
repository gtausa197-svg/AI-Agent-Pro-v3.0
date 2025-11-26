import React from 'react';
import { Cpu, MemoryStick, HardDrive, Activity } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';
import { Progress } from '../ui/progress';

export function StatsCard({ title, value, icon: Icon, color }) {
    const getColorClass = () => {
        if (value >= 90) return 'text-red-500';
        if (value >= 70) return 'text-yellow-500';
        return 'text-green-500';
    };

    return (
        <Card>
            <CardContent className="pt-6">
                <div className="flex items-center justify-between mb-4">
                    <div>
                        <p className="text-sm text-muted-foreground">{title}</p>
                        <h3 className={`text-3xl font-bold ${getColorClass()}`}>
                            {Math.round(value)}%
                        </h3>
                    </div>
                    <Icon className={`h-12 w-12 ${color} opacity-50`} />
                </div>
                <Progress value={value} />
            </CardContent>
        </Card>
    );
}

export function SystemStats({ stats }) {
    if (!stats) {
        return (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {[1, 2, 3].map((i) => (
                    <Card key={i} className="animate-pulse">
                        <CardContent className="pt-6">
                            <div className="h-24 bg-muted rounded"></div>
                        </CardContent>
                    </Card>
                ))}
            </div>
        );
    }

    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <StatsCard
                title="CPU Usage"
                value={stats.cpu || 0}
                icon={Cpu}
                color="text-blue-500"
            />
            <StatsCard
                title="Memory Usage"
                value={stats.memory || 0}
                icon={MemoryStick}
                color="text-purple-500"
            />
            <StatsCard
                title="Disk Usage"
                value={stats.disk || 0}
                icon={HardDrive}
                color="text-orange-500"
            />
        </div>
    );
}
