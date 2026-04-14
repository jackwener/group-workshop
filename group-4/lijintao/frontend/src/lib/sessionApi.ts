import { apiClient } from './api';
import { Session, ApiResponse } from '@/types';

interface SessionsResponse {
  sessions: Session[];
  total: number;
  page: number;
  page_size: number;
}

interface CreateSessionRequest {
  title?: string;
}

interface CreateSessionResponse {
  id: number;
  title: string;
  message_count: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export const sessionApi = {
  list: (page = 1, pageSize = 20): Promise<ApiResponse<SessionsResponse>> =>
    apiClient.get<ApiResponse<SessionsResponse>>(`/api/v1/sessions?page=${page}&page_size=${pageSize}`),
  
  create: (title?: string): Promise<ApiResponse<CreateSessionResponse>> =>
    apiClient.post<ApiResponse<CreateSessionResponse>>('/api/v1/sessions', { title } as CreateSessionRequest),
  
  get: (id: number): Promise<ApiResponse<Session>> =>
    apiClient.get<ApiResponse<Session>>(`/api/v1/sessions/${id}`),
  
  delete: (id: number): Promise<ApiResponse<void>> =>
    apiClient.delete<ApiResponse<void>>(`/api/v1/sessions/${id}`),
};
