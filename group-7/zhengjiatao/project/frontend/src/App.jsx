import { useState, useEffect } from 'react';
import styles from './App.module.css';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import InputArea from './components/InputArea';
import { 
  getSessions, 
  createSession, 
  deleteSession, 
  getRecordsBySession,
  ask,
  getCapabilities 
} from './services/api';

function App() {
  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [capabilities, setCapabilities] = useState(null);

  // 加载会话列表
  const loadSessions = async () => {
    try {
      setLoading(true);
      const data = await getSessions();
      setSessions(data.sessions || []);
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('加载会话失败:', err);
    } finally {
      setLoading(false);
    }
  };

  // 创建新会话
  const handleCreateSession = async () => {
    try {
      setLoading(true);
      const data = await createSession();
      await loadSessions();
      // 选中新创建的会话
      const newSession = sessions.find(s => s.session_id === data.session_id) || data;
      setCurrentSession(newSession);
    } catch (err) {
      setError(err.message);
      console.error('创建会话失败:', err);
    } finally {
      setLoading(false);
    }
  };

  // 选择会话
  const handleSelectSession = async (session) => {
    setCurrentSession(session);
    // 加载该会话的记录
    if (session) {
      try {
        const data = await getRecordsBySession(session.session_id);
        setRecords(data.records || []);
      } catch (err) {
        console.error('加载记录失败:', err);
        setRecords([]);
      }
    } else {
      setRecords([]);
    }
  };

  // 删除会话
  const handleDeleteSession = async (sessionId) => {
    try {
      setLoading(true);
      await deleteSession(sessionId);
      await loadSessions();
      // 如果删除的是当前选中的会话，清空当前会话
      if (currentSession?.session_id === sessionId) {
        setCurrentSession(null);
      }
    } catch (err) {
      setError(err.message);
      console.error('删除会话失败:', err);
    } finally {
      setLoading(false);
    }
  };

  // 初始加载
  useEffect(() => {
    loadSessions();
    // 加载系统能力状态
    getCapabilities().then(data => {
      setCapabilities(data);
    }).catch(err => {
      console.error('加载能力状态失败:', err);
    });
  }, []);

  // 提交问答
  const handleAsk = async (query) => {
    if (!currentSession) return;
    
    try {
      setLoading(true);
      setError(null);
      
      await ask(currentSession.session_id, query);
      
      // 重新加载记录和会话列表（更新query_count）
      const [recordsData, sessionsData] = await Promise.all([
        getRecordsBySession(currentSession.session_id),
        getSessions()
      ]);
      
      setRecords(recordsData.records || []);
      setSessions(sessionsData.sessions || []);
      
      // 更新当前会话信息
      const updatedSession = sessionsData.sessions.find(
        s => s.session_id === currentSession.session_id
      );
      if (updatedSession) {
        setCurrentSession(updatedSession);
      }
    } catch (err) {
      setError(err.message);
      console.error('问答提交失败:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.app}>
      <Header capabilities={capabilities} />
      
      <div className={styles.main}>
        <Sidebar
          sessions={sessions}
          currentSession={currentSession}
          onSelectSession={handleSelectSession}
          onCreateSession={handleCreateSession}
          onDeleteSession={handleDeleteSession}
          loading={loading}
        />
        
        <div className={styles.content}>
          {error && (
            <div className={styles.errorBanner}>
              错误: {error}
            </div>
          )}
          
          <ChatArea
            session={currentSession}
            records={records}
            onAsk={handleAsk}
            loading={loading}
            inputArea={InputArea}
          />
        </div>
      </div>
    </div>
  );
}

export default App;
