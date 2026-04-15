import { useState, useEffect, useCallback } from 'react';
import Header from './components/Header/Header';
import Sidebar from './components/Sidebar/Sidebar';
import MainContent from './components/MainContent/MainContent';
import InputArea from './components/InputArea/InputArea';
import Toast from './components/common/Toast';
import { useSessions } from './hooks/useSessions';
import { useRecords } from './hooks/useRecords';
import { useToast } from './hooks/useToast';
import { getErrorMessage } from './utils/errorMessages';
import styles from './App.module.css';

export default function App() {
  const {
    sessions,
    currentSession,
    fetchSessions,
    createSession,
    removeSession,
    selectSession,
  } = useSessions();

  const { records, isLoading, fetchRecords, askQuestion, clearRecords } = useRecords();
  const { toastMessage, showToast } = useToast();
  const [query, setQuery] = useState('');
  const [capabilities] = useState(null);

  // Load sessions on mount
  useEffect(() => {
    fetchSessions().catch(err => showToast(getErrorMessage(err.code)));
  }, [fetchSessions, showToast]);

  // Load records when session changes
  useEffect(() => {
    if (currentSession) {
      fetchRecords(currentSession.session_id).catch(err =>
        showToast(getErrorMessage(err.code))
      );
    } else {
      clearRecords();
    }
  }, [currentSession, fetchRecords, clearRecords, showToast]);

  const handleCreateSession = useCallback(async () => {
    try {
      await createSession();
    } catch (err) {
      showToast(getErrorMessage(err.code));
    }
  }, [createSession, showToast]);

  const handleDeleteSession = useCallback(async (sessionId) => {
    try {
      await removeSession(sessionId);
    } catch (err) {
      showToast(getErrorMessage(err.code));
    }
  }, [removeSession, showToast]);

  const handleSend = useCallback(async () => {
    const trimmed = query.trim();
    if (!trimmed || !currentSession) return;
    if (trimmed.length > 500) {
      showToast(getErrorMessage('INVALID_QUERY'));
      return;
    }
    try {
      await askQuestion(trimmed, currentSession.session_id);
      setQuery('');
      // Refresh sessions to get updated title (auto-rename on first question)
      fetchSessions();
    } catch (err) {
      showToast(getErrorMessage(err.code));
      if (err.code === 'SESSION_NOT_FOUND') {
        fetchSessions();
      }
    }
  }, [query, currentSession, askQuestion, showToast, fetchSessions]);

  const handleQuestionClick = useCallback(async (questionText) => {
    // If no session, create one first
    if (!currentSession) {
      try {
        await createSession();
      } catch (err) {
        showToast(getErrorMessage(err.code));
        return;
      }
    }
    setQuery(questionText);
  }, [currentSession, createSession, showToast]);

  return (
    <div className={styles.layout}>
      <div className={styles.header}>
        <Header capabilities={capabilities} />
      </div>
      <div className={styles.sidebar}>
        <Sidebar
          sessions={sessions}
          currentSession={currentSession}
          onSelect={selectSession}
          onCreate={handleCreateSession}
          onDelete={handleDeleteSession}
        />
      </div>
      <div className={styles.mainWrapper}>
        <MainContent
          currentSession={currentSession}
          records={records}
          isLoading={isLoading}
          onQuestionClick={handleQuestionClick}
        />
        <InputArea
          query={query}
          setQuery={setQuery}
          onSend={handleSend}
          onClear={() => setQuery('')}
          isLoading={isLoading}
          disabled={!currentSession}
        />
      </div>
      <Toast message={toastMessage} />
    </div>
  );
}
