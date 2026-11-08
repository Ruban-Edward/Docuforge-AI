import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_URL,
  timeout: 15000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('docuforge_token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authApi = {
  login: async (email: string, password: string) => {
    const response = await api.post('/api/v1/auth/login', { email, password });
    return response.data;
  },
  refresh: async (refreshToken: string) => {
    const response = await api.post('/api/v1/auth/refresh', { refresh_token: refreshToken });
    return response.data;
  },
  fetchCurrentUser: async () => {
    const response = await api.get('/api/v1/users');
    return response.data;
  },
};

export const adminApi = {
  stats: async () => {
    const response = await api.get('/api/v1/admin/stats');
    return response.data;
  },
};

export const usersApi = {
  list: async () => {
    const response = await api.get('/api/v1/users');
    return response.data;
  },
};

export const departmentsApi = {
  list: async () => {
    const response = await api.get('/api/v1/departments');
    return response.data;
  },
};

export const templatesApi = {
  list: async () => {
    const response = await api.get('/api/v1/templates');
    return response.data;
  },
};
