export interface Session {
  id: number;
  title: string;
  message_count: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: number;
  session_id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  tokens?: number;
  model?: string;
  provider?: string;
  latency_ms?: number;
  is_degraded?: boolean;
  created_at: string;
}

export interface ChatRequest {
  content: string;
  stream?: boolean;
  model?: string;
}

export interface ApiResponse<T> {
  traceId: string;
  data: T;
  timestamp: string;
}
