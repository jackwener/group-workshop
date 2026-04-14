import { apiClient } from './api';
import { Message, ApiResponse } from '@/types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface MessagesResponse {
  items: Message[];
  total: number;
  page: number;
  page_size: number;
}

export const messageApi = {
  getMessages: (sessionId: number, page = 1, pageSize = 50): Promise<ApiResponse<MessagesResponse>> =>
    apiClient.get<ApiResponse<MessagesResponse>>(
      `/api/v1/sessions/${sessionId}/messages?page=${page}&page_size=${pageSize}`
    ),

  sendMessage: async (sessionId: number, content: string): Promise<Response> => {
    const url = `${API_BASE}/api/v1/sessions/${sessionId}/messages`;
    return fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content, stream: true, model: 'auto' }),
    });
  },
};
