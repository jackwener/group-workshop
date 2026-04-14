import React from 'react';
import './Sidebar.css';

/**
 * Sidebar组件
 * 会话列表管理：新建、删除、选中会话
 */
function Sidebar({
  sessions,
  currentSession,
  onCreateSession,
  onDeleteSession,
  onSelectSession,
}) {
  // 格式化时间
  const formatTime = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // 确认删除
  const handleDelete = (e, sessionId) => {
    e.stopPropagation();
    if (window.confirm('确定要删除这个会话吗？')) {
      onDeleteSession(sessionId);
    }
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h2 className="sidebar-title">历史会话</h2>
        <button
          className="btn btn-primary sidebar-new-btn"
          onClick={onCreateSession}
        >
          + 新建
        </button>
      </div>

      <div className="sidebar-list">
        {sessions.length === 0 ? (
          <div className="sidebar-empty">
            <p>暂无会话</p>
            <p className="sidebar-empty-hint">点击"+ 新建"创建会话</p>
          </div>
        ) : (
          sessions.map((session) => (
            <div
              key={session.session_id}
              className={`session-item ${
                currentSession?.session_id === session.session_id
                  ? 'session-item-active'
                  : ''
              }`}
              onClick={() => onSelectSession(session)}
            >
              <div className="session-item-content">
                <div className="session-item-title">{session.title}</div>
                <div className="session-item-meta">
                  <span>{session.query_count || 0} 条对话</span>
                  <span>{formatTime(session.updated_at)}</span>
                </div>
              </div>
              <button
                className="session-item-delete"
                onClick={(e) => handleDelete(e, session.session_id)}
                title="删除会话"
              >
                ×
              </button>
            </div>
          ))
        )}
      </div>
    </aside>
  );
}

export default Sidebar;
