import { create } from 'zustand';

export const useStore = create((set) => ({
    theme: 'dark',
    toggleTheme: () => set((state) => ({
        theme: state.theme === 'dark' ? 'light' : 'dark'
    })),

    systemStats: null,
    setSystemStats: (stats) => set({ systemStats: stats }),

    commandHistory: [],
    addCommandToHistory: (command) => set((state) => ({
        commandHistory: [command, ...state.commandHistory].slice(0, 50)
    })),
}));
