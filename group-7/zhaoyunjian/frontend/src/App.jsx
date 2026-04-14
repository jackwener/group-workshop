import React, { useState, useEffect, useCallback } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import MainContent from './components/MainContent';
import InputArea from './components/InputArea';
import { capabilitiesApi, sessionsApi, qaApi } from './services/api';
import './App.css';

function App() {
  // 状态管理
  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(false);
  const [query, setQuery] = useState('');
  const [error, setError] = useState(null);
  const [capabilities, setCapabilities] = useState(null);

  // 加载系统能力配置
  useEffect(() => {
    loadCapabilities();
    loadSessions();
  }, []);

  // 当前会话变化时加载问答记录
  useEffect(() => {
    if (currentSession) {
      loadRecords(currentSession.session_id);
    } else {
      setRecords([]);
    }
  }, [currentSession]);

  // 加载能力配置
  const loadCapabilities = async () => {
    try {
      const data = await capabilitiesApi.get();
      setCapabilities(data.caps);
    } catch (err) {
      console.error('加载能力配置失败:', err);
    }
  };

  // 加载会话列表
  const loadSessions = async () => {
    try {
      const data = await sessionsApi.list();
      setSessions(data.sessions || []);
      
      // 如果有会话，默认选中第一个
      if (data.sessions && data.sessions.length > 0 && !currentSession) {
        setCurrentSession(data.sessions[0]);
      }
    } catch (err) {
      console.error('加载会话列表失败:', err);
      setError('加载会话列表失败');
    }
  };

  // 加载问答记录
  const loadRecords = async (sessionId) => {
    try {
      const data = await sessionsApi.getRecords(sessionId);
      setRecords(data.records || []);
    } catch (err) {
      console.error('加载问答记录失败:', err);
      setError('加载问答记录失败');
    }
  };

  // 创建新会话
  const handleCreateSession = async () => {
    try {
      const data = await sessionsApi.create();
      setSessions([data, ...sessions]);
      setCurrentSession(data);
    } catch (err) {
      console.error('创建会话失败:', err);
      setError('创建会话失败');
    }
  };

  // 删除会话
  const handleDeleteSession = async (sessionId) => {
    try {
      await sessionsApi.delete(sessionId);
      const newSessions = sessions.filter(s => s.session_id !== sessionId);
      setSessions(newSessions);
      
      // 如果删除的是当前会话，切换到第一个会话或清空
      if (currentSession && currentSession.session_id === sessionId) {
        setCurrentSession(newSessions.length > 0 ? newSessions[0] : null);
      }
    } catch (err) {
      console.error('删除会话失败:', err);
      setError('删除会话失败');
    }
  };

  // 选择会话
  const handleSelectSession = (session) => {
    setCurrentSession(session);
  };

  // 发送问题
  const handleSend = async () => {
    if (!query.trim() || !currentSession) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const data = await qaApi.ask(currentSession.session_id, query);
      
      // 添加新记录到列表
      const newRecord = {
        record_id: Date.now().toString(),
        query: query,
        answer: data.answer,
        timestamp: new Date().toISOString(),
        llm_used: data.llm_used,
        model: data.model,
        answer_source: data.answer_source,
        response_time_ms: data.response_time_ms,
      };
      
      setRecords([newRecord, ...records]);
      setQuery('');
      
      // 刷新会话列表（更新query_count）
      loadSessions();
    } catch (err) {
      console.error('发送问题失败:', err);
      setError(err.message || '发送问题失败');
    } finally {
      setLoading(false);
    }
  };

  // 清空输入
  const handleClear = () => {
    setQuery('');
  };

  return (
    <div className="app">
      <Header capabilities={capabilities} />
      <div className="app-body">
        <Sidebar
          sessions={sessions}
          currentSession={currentSession}
          onCreateSession={handleCreateSession}
          onDeleteSession={handleDeleteSession}
          onSelectSession={handleSelectSession}
        />
        <div className="app-main">
          <MainContent
            currentSession={currentSession}
            records={records}
            loading={loading}
            error={error}
            onClearError={() => setError(null)}
          />
          <InputArea
            query={query}
            loading={loading}
            onQueryChange={setQuery}
            onSend={handleSend}
            onClear={handleClear}
            disabled={!currentSession}
          />
        </div>
      </div>
    </div>
  );
}

export default App;
