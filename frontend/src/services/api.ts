import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle token expiration
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export interface RegisterData {
  username: string;
  password: string;
  email?: string;
  confirm_password?: string;
}

export interface LoginData {
  username: string;
  password: string;
}

export interface User {
  username: string;
  email?: string;
  role: string;
  created_at: string;
  is_active: boolean;
}

export interface Task {
  task_id: string;
  status: string;
  file_name?: string;
  progress: number;
  message: string;
  result?: any;
  error?: string;
  output_files?: string[];
  created_at: string;
}

export const authAPI = {
  register: async (data: RegisterData) => {
    const response = await api.post('/auth/register', data);
    return response.data;
  },
  login: async (data: LoginData) => {
    const response = await api.post('/auth/login', data, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return response.data;
  },
  getCurrentUser: async () => {
    const response = await api.get('/api/v1/users/me');
    return response.data;
  },
  changePassword: async (data: any) => {
    const response = await api.post('/auth/change-password', data);
    return response.data;
  },
  listUsers: async (activeOnly: boolean = true) => {
    const response = await api.get(`/api/v1/users?active_only=${activeOnly}`);
    return response.data;
  },
  listAllTasks: async () => {
    const response = await api.get('/api/v1/admin/tasks');
    return response.data;
  },
  getStats: async () => {
    const response = await api.get('/api/v1/admin/stats');
    return response.data;
  },
  forgotPassword: async (email: string) => {
    const response = await api.post('/auth/forgot-password', { email });
    return response.data;
  },
};

export const taskAPI = {
  runPipeline: async (file: File, options: any) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('file_type', options.file_type || 'csv');
    formData.append('profile_data', String(options.profile_data ?? true));
    formData.append('include_visuals', String(options.include_visuals ?? false));
    formData.append('apply_cleaning', String(options.apply_cleaning ?? true));
    formData.append('enable_feature_suggestions', String(options.enable_feature_suggestions ?? false));
    formData.append('validate_final_data', String(options.validate_final_data ?? true));
    if (options.export_formats) {
      formData.append('export_formats', JSON.stringify(options.export_formats));
    }

    const response = await api.post('/api/v1/pipeline/run', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
  getTask: async (taskId: string) => {
    const response = await api.get(`/api/v1/tasks/${taskId}`);
    return response.data;
  },
  listTasks: async (limit: number = 10) => {
    const response = await api.get(`/api/v1/tasks?limit=${limit}`);
    return response.data;
  },
  downloadTask: async (taskId: string, fileType: string = 'csv') => {
    const response = await api.get(`/api/v1/tasks/${taskId}/download?file_type=${fileType}`, {
      responseType: 'blob',
    });
    return response.data;
  },
  deleteTask: async (taskId: string) => {
    const response = await api.delete(`/api/v1/tasks/${taskId}`);
    return response.data;
  },
};

export default api;

