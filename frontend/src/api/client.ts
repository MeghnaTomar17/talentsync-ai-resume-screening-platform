import axios from 'axios';
import type { ApiResponse } from '@/types/api';

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 90000,
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export async function unwrapResponse<T>(
  request: Promise<{ data: ApiResponse<T> }>
): Promise<T> {
  const response = await request;
  if (!response.data.success) {
    throw new Error(response.data.message || 'Request failed');
  }
  return response.data.data;
}
