import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json',
    },
});

export const systemAPI = {
    getInfo: () => api.get('/api/system/info'),
    getStats: () => api.get('/api/system/stats'),
    getProcesses: (limit = 20) => api.get(`/api/system/processes?limit=${limit}`),
};

export const commandAPI = {
    execute: (command) => api.post(`/api/commands/execute?command=${encodeURIComponent(command)}`),
    getHistory: (limit = 50) => api.get(`/api/commands/history?limit=${limit}`),
};

export const filesAPI = {
    search: (pattern, directory = null, limit = 100) => {
        const params = new URLSearchParams({ pattern, limit });
        if (directory) params.append('directory', directory);
        return api.get(`/api/files/search?${params}`);
    },
};

export default api;
