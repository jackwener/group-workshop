/**
 * 投研问答助手 - 主应用组件
 * 模块编号: M1-QA
 */
import React, { useState, useEffect, useCallback } from 'react';
import './App.css';

// 组件
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import InputArea from './components/InputArea';
import Toast from './components/Toast';

// Hooks
import { useSessionsApi, useAskApi, useCapabilitiesApi } from './hooks/useApi';
import { useToast } from './hooks/useToast';

function App() {
  // 状态
  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [records, setRecords] = useState([]);
  const [capabilities, setCapabilities] = useState(null);
  const [askLoading, setAskLoading] = useState(false);
  
  // Hooks
  const {
    getSessions,
    createSession: apiCreateSession,
    deleteSession: apiDeleteSession,
    getSessionRecords,
    loading: sessionsLoading,
    error: sessionsError,
    clearError: clearSessionsError,
  } = useSessionsApi();
  
  const {
    ask: apiAsk,
    loading: askApiLoading,
    error: askError,
    clearError: clearAskError,
  } = useAskApi();
  
  const {
    getCapabilities: apiGetCapabilities,
  } = useCapabilitiesApi();
  
  const { toast, showToast, hideToast } = useToast();
  
  // 初始化：加载会话列表和能力状态
  useEffect(() => {
    loadSessions();
    loadCapabilities();
  }, []);
  
  // 错误处理
  useEffect(() => {
    if (sessionsError) {
      showToast(sessionsError.message || '加载会话失败', 'error');
      clearSessionsError();
    }
  }, [sessionsError, showToast, clearSessionsError]);
  
  useEffect(() => {
    if (askError) {
      showToast(askError.message || '发送问题失败', 'error');
      clearAskError();
    }
  }, [askError, showToast, clearAskError]);
  
  // 加载会话列表
  const loadSessions = useCallback(async () => {
    try {
      const data = await getSessions();
      setSessions(data);
    } catch (err) {
      console.error('加载会话失败:', err);
    }
  }, [getSessions]);
  
  // 加载能力状态
  const loadCapabilities = useCallback(async () => {
    try {
      const data = await apiGetCapabilities();
      setCapabilities(data);
    } catch (err) {
      console.error('加载能力状态失败:', err);
    }
  }, [apiGetCapabilities]);
  
  // 加载会话记录
  const loadSessionRecords = useCallback(async (sessionId) => {
    try {
      const data = await getSessionRecords(sessionId);
      setRecords(data);
    } catch (err) {
      console.error('加载会话记录失败:', err);
      setRecords([]);
    }
  }, [getSessionRecords]);
  
  // 选择会话
  const handleSelectSession = useCallback(async (session) => {
    setCurrentSession(session);
    await loadSessionRecords(session.session_id);
  }, [loadSessionRecords]);
  
  // 创建新会话
  const handleCreateSession = useCallback(async () => {
    try {
      const newSession = await apiCreateSession('新会话');
      setSessions((prev) => [newSession, ...prev]);
      setCurrentSession(newSession);
      setRecords([]);
      showToast('会话创建成功', 'success');
    } catch (err) {
      console.error('创建会话失败:', err);
    }
  }, [apiCreateSession, showToast]);
  
  // 删除会话
  const handleDeleteSession = useCallback(async (sessionId) => {
    try {
      await apiDeleteSession(sessionId);
      setSessions((prev) => prev.filter((s) => s.session_id !== sessionId));
      
      // 如果删除的是当前会话，清空当前会话
      if (currentSession?.session_id === sessionId) {
        setCurrentSession(null);
        setRecords([]);
      }
      
      showToast('会话已删除', 'success');
    } catch (err) {
      console.error('删除会话失败:', err);
      showToast('删除会话失败', 'error');
    }
  }, [apiDeleteSession, currentSession, showToast]);
  
  // 发送问题
  const handleSendQuestion = useCallback(async (question) => {
    if (!currentSession) {
      showToast('请先选择一个会话', 'warning');
      return;
    }
    
    setAskLoading(true);
    
    try {
      // 乐观更新：先添加用户问题到记录
      const tempRecord = {
        id: `temp_${Date.now()}`,
        session_id: currentSession.session_id,
        query: question,
        answer: '',
        llm_used: false,
        model: null,
        response_time_ms: 0,
        answer_source: 'loading',
        timestamp: new Date().toISOString(),
      };
      setRecords((prev) => [...prev, tempRecord]);
      
      // 调用 API
      const result = await apiAsk(question, currentSession.session_id);
      
      // 更新记录
      setRecords((prev) =>
        prev.map((r) =>
          r.id === tempRecord.id
            ? {
                ...tempRecord,
                answer: result.answer,
                llm_used: result.llm_used,
                model: result.model,
                response_time_ms: result.response_time_ms,
                answer_source: result.answer_source,
              }
            : r
        )
      );
      
      // 更新会话列表（更新 query_count）
      loadSessions();
    } catch (err) {
      // 移除临时记录
      setRecords((prev) => prev.filter((r) => !r.id.startsWith('temp_')));
      console.error('发送问题失败:', err);
    } finally {
      setAskLoading(false);
    }
  }, [currentSession, apiAsk, showToast, loadSessions]);
  
  return (
    <div className="app">
      <Header capabilities={capabilities} />
      
      <div className="main-container">
        <Sidebar
          sessions={sessions}
          currentSession={currentSession}
          onSelectSession={handleSelectSession}
          onCreateSession={handleCreateSession}
          onDeleteSession={handleDeleteSession}
          loading={sessionsLoading}
        />
        
        <div className="content-area">
          <ChatArea
            currentSession={currentSession}
            records={records}
            onSendQuestion={handleSendQuestion}
            loading={askLoading || askApiLoading}
          />
          
          <InputArea
            onSend={handleSendQuestion}
            loading={askLoading || askApiLoading}
            disabled={!currentSession}
          />
        </div>
      </div>
      
      <Toast
        message={toast?.message}
        type={toast?.type}
        onClose={hideToast}
      />
    </div>
  );
}

export default App;
