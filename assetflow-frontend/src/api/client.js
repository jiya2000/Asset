import axios from 'axios';
import toast from 'react-hot-toast';

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
});

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('assetflow_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Global error handler
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status;
    const message = error.response?.data?.detail || error.message || 'Something went wrong';

    if (status === 401) {
      // Only redirect if not already on login page
      if (!window.location.pathname.includes('/login')) {
        localStorage.removeItem('assetflow_token');
        localStorage.removeItem('assetflow_user');
        window.location.href = '/login';
      }
    } else if (status !== 422) {
      // Don't toast validation errors (handled by form), toast everything else
      toast.error(message);
    }
    return Promise.reject(error);
  }
);

export default api;
