import React from 'react';

export function Button({ children, className = '', variant = 'default', ...props }) {
    const baseStyles = 'inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50';

    const variants = {
        default: 'bg-primary text-primary-foreground hover:bg-primary/90',
        secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
        outline: 'border border-input bg-background hover:bg-accent hover:text-accent-foreground',
        ghost: 'hover:bg-accent hover:text-accent-foreground',
    };

    const sizes = 'h-10 px-4 py-2';

    return (
        <button
            className={`${baseStyles} ${variants[variant]} ${sizes} ${className}`}
            {...props}
        >
            {children}
        </button>
    );
}
