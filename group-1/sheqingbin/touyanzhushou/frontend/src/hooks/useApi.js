/**
 * API 调用 Hook
 * 封装 fetch API，统一处理错误和 loading 状态
 */
import { useState, useCallback } from 'react';

const API_BASE = '/api/v1/agent';

/**
 * 通用 API 请求函数
 */
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };
  
  if (config.body && typeof config.body === 'object') {
    config.body = JSON.stringify(config.body);
  }
  
  const response = await fetch(url, config);
  const data = await response.json();
  
  if (!response.ok) {
    const error = new Error(data.error?.message || '请求失败');
    error.code = data.error?.code || 'UNKNOWN_ERROR';
    error.status = response.status;
    error.details = data.error?.details || {};
    throw error;
  }
  
  return data;
}

/**
 * 使用 API 的 Hook
 */
export function useApi() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const request = useCallback(async (endpoint, options = {}) => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await apiRequest(endpoint, options);
      return data;
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);
  
  const clearError = useCallback(() => {
    setError(null);
  }, []);
  
  return { request, loading, error, clearError };
}

/**
 * 会话相关 API
 */
export function useSessionsApi() {
  const { request, loading, error, clearError } = useApi();
  
  const getSessions = useCallback(async () => {
    const data = await request('/sessions');
    return data.sessions || [];
  }, [request]);
  
  const createSession = useCallback(async (title) => {
    const data = await request('/sessions', {
      method: 'POST',
      body: { title },
    });
    return data;
  }, [request]);
  
  const deleteSession = useCallback(async (sessionId) => {
    await request(`/sessions/${sessionId}`, {
      method: 'DELETE',
    });
  }, [request]);
  
  const getSessionRecords = useCallback(async (sessionId) => {
    const data = await request(`/sessions/${sessionId}/records`);
    return data.records || [];
  }, [request]);
  
  return {
    getSessions,
    createSession,
    deleteSession,
    getSessionRecords,
    loading,
    error,
    clearError,
  };
}

/**
 * 问答相关 API
 */
export function useAskApi() {
  const { request, loading, error, clearError } = useApi();
  
  const ask = useCallback(async (query, sessionId) => {
    const data = await request('/ask', {
      method: 'POST',
      body: { query, session_id: sessionId },
    });
    return data;
  }, [request]);
  
  return {
    ask,
    loading,
    error,
    clearError,
  };
}

/**
 * 能力状态 API
 */
export function useCapabilitiesApi() {
  const { request, loading, error } = useApi();
  
  const getCapabilities = useCallback(async () => {
    const data = await request('/capabilities');
    return data;
  }, [request]);
  
  return {
    getCapabilities,
    loading,
    error,
  };
}
