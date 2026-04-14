'use client';

import { useCallback } from 'react';
import { useChatStore } from '@/store/chatStore';
import { sessionApi } from '@/lib/sessionApi';
import { Session } from '@/types';

export function useSessions() {
  const { 
    sessions, 
    setSessions, 
    addSession, 
    removeSession, 
    setLoading, 
    setError 
  } = useChatStore();

  const fetchSessions = useCallback(async (page = 1, pageSize = 20) => {
    setLoading(true);
    setError(null);
    try {
      const response = await sessionApi.list(page, pageSize);
      setSessions(response.data.sessions);
      return response.data.sessions;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '获取会话列表失败';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [setSessions, setLoading, setError]);

  const createSession = useCallback(async (title?: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await sessionApi.create(title);
      const newSession: Session = {
        id: response.data.id,
        title: response.data.title,
        message_count: response.data.message_count,
        is_active: response.data.is_active,
        created_at: response.data.created_at,
        updated_at: response.data.updated_at,
      };
      addSession(newSession);
      return newSession;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '创建会话失败';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [addSession, setLoading, setError]);

  const deleteSession = useCallback(async (id: number) => {
    setLoading(true);
    setError(null);
    try {
      await sessionApi.delete(id);
      removeSession(id);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '删除会话失败';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [removeSession, setLoading, setError]);

  return {
    sessions,
    fetchSessions,
    createSession,
    deleteSession,
  };
}
