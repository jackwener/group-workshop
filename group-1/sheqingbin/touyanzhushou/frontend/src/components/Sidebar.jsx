/**
 * Sidebar 组件
 * 会话列表管理：新建、删除、切换会话
 */
import React, { useState } from 'react';
import './Sidebar.css';

function Sidebar({
  sessions,
  currentSession,
  onSelectSession,
  onCreateSession,
  onDeleteSession,
  loading,
}) {
  const [sessionToDelete, setSessionToDelete] = useState(null);
  
  const handleDeleteClick = (e, sessionId) => {
    e.stopPropagation();
    setSessionToDelete(sessionId);
  };
  
  const handleConfirmDelete = () => {
    if (sessionToDelete) {
      onDeleteSession(sessionToDelete);
      setSessionToDelete(null);
    }
  };
  
  const handleCancelDelete = () => {
    setSessionToDelete(null);
  };
  
  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    const now = new Date();
    const isToday = date.toDateString() === now.toDateString();
    
    if (isToday) {
      return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
    }
    return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
  };
  
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <button
          className="btn btn-primary new-session-btn"
          onClick={onCreateSession}
          disabled={loading}
        >
          <span className="icon">+</span>
          新建会话
        </button>
      </div>
      
      <div className="sessions-list">
        {sessions.length === 0 ? (
          <div className="empty-sessions">
            <p>暂无会话</p>
            <p className="empty-hint">点击上方按钮创建新会话</p>
          </div>
        ) : (
          sessions.map((session) => (
            <div
              key={session.session_id}
              className={`session-item ${currentSession?.session_id === session.session_id ? 'active' : ''}`}
              onClick={() => onSelectSession(session)}
            >
              <div className="session-info">
                <div className="session-title">{session.title}</div>
                <div className="session-meta">
                  <span>{formatDate(session.updated_at)}</span>
                  {session.query_count > 0 && (
                    <span className="query-count">{session.query_count} 条对话</span>
                  )}
                </div>
              </div>
              <button
                className="delete-btn"
                onClick={(e) => handleDeleteClick(e, session.session_id)}
                title="删除会话"
              >
                ×
              </button>
            </div>
          ))
        )}
      </div>
      
      {/* 删除确认模态框 */}
      {sessionToDelete && (
        <div className="modal-overlay" onClick={handleCancelDelete}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-title">确认删除</div>
            <p>确定要删除这个会话吗？此操作不可恢复。</p>
            <div className="modal-actions">
              <button className="btn" onClick={handleCancelDelete}>
                取消
              </button>
              <button className="btn btn-danger" onClick={handleConfirmDelete}>
                删除
              </button>
            </div>
          </div>
        </div>
      )}
    </aside>
  );
}

export default Sidebar;
