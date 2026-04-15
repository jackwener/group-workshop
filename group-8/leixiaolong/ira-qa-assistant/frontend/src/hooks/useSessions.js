import { useState, useCallback } from 'react';
import { getSessions, createSession as apiCreateSession, deleteSession as apiDeleteSession } from '../api/client';

export function useSessions() {
  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);

  const fetchSessions = useCallback(async () => {
    const data = await getSessions();
    setSessions(data.sessions || []);
    return data.sessions || [];
  }, []);

  const createSession = useCallback(async (title) => {
    const data = await apiCreateSession(title);
    const newSession = {
      session_id: data.session_id,
      title: data.title,
      created_at: data.created_at,
      updated_at: data.updated_at,
      query_count: data.query_count,
    };
    setSessions(prev => [newSession, ...prev]);
    setCurrentSession(newSession);
    return newSession;
  }, []);

  const removeSession = useCallback(async (sessionId) => {
    await apiDeleteSession(sessionId);
    setSessions(prev => prev.filter(s => s.session_id !== sessionId));
    setCurrentSession(prev => {
      if (prev && prev.session_id === sessionId) return null;
      return prev;
    });
  }, []);

  const selectSession = useCallback((session) => {
    setCurrentSession(session);
  }, []);

  return {
    sessions,
    currentSession,
    fetchSessions,
    createSession,
    removeSession,
    selectSession,
    setSessions,
    setCurrentSession,
  };
}
