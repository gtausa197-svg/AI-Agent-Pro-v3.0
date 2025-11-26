import React from 'react';

export function Card({ children, className = '' }) {
    return (
        <div className={`bg-card text-card-foreground rounded-lg border shadow-sm ${className}`}>
            {children}
        </div>
    );
}

export function CardHeader({ children, className = '' }) {
    return (
        <div className={`flex flex-col space-y-1.5 p-6 ${className}`}>
            {children}
        </div>
    );
}

export function CardTitle({ children, className = '' }) {
    return (
        <h3 className={`text-2xl font-semibold leading-none tracking-tight ${className}`}>
            {children}
        </h3>
    );
}

export function CardContent({ children, className = '' }) {
    return (
        <div className={`p-6 pt-0 ${className}`}>
            {children}
        </div>
    );
}
