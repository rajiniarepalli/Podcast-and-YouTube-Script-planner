import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 60000,
});

export const scriptApi = {
  checkHealth: async () => {
    const response = await apiClient.get('/api/health');
    return response.data;
  },
  generateScript: async (payload) => {
    const response = await apiClient.post('/api/generate-script', payload);
    return response.data;
  },
  refineScript: async (payload) => {
    const response = await apiClient.post('/api/refine-script', payload);
    return response.data;
  },
};
