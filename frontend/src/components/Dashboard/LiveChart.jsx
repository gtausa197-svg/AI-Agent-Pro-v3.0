import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';

export function LiveChart({ data }) {
    const [chartData, setChartData] = useState([]);

    useEffect(() => {
        if (data?.data) {
            const { cpu, memory, disk, timestamp } = data.data;
            const time = new Date(timestamp).toLocaleTimeString();

            setChartData(prev => {
                const newData = [...prev, { time, cpu, memory, disk }];
                // Keep only last 20 points
                return newData.slice(-20);
            });
        }
    }, [data]);

    return (
        <Card>
            <CardHeader>
                <CardTitle>Real-time Performance</CardTitle>
            </CardHeader>
            <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                        <XAxis
                            dataKey="time"
                            tick={{ fontSize: 12 }}
                            className="text-muted-foreground"
                        />
                        <YAxis
                            domain={[0, 100]}
                            tick={{ fontSize: 12 }}
                            className="text-muted-foreground"
                        />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: 'hsl(var(--card))',
                                border: '1px solid hsl(var(--border))'
                            }}
                        />
                        <Legend />
                        <Line type="monotone" dataKey="cpu" stroke="#3b82f6" name="CPU %" />
                        <Line type="monotone" dataKey="memory" stroke="#a855f7" name="Memory %" />
                        <Line type="monotone" dataKey="disk" stroke="#f97316" name="Disk %" />
                    </LineChart>
                </ResponsiveContainer>
            </CardContent>
        </Card>
    );
}
