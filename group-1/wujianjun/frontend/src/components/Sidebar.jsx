function Sidebar({ 
  sessions, 
  currentSessionId, 
  onSelectSession, 
  onCreateSession, 
  onDeleteSession 
}) {
  return (
    <aside className="sidebar">
      <button className="new-session-btn" onClick={onCreateSession}>
        + 新建会话
      </button>
      <div className="session-list">
        {sessions.map(session => (
          <div
            key={session.session_id}
            className={`session-item ${session.session_id === currentSessionId ? 'active' : ''}`}
            onClick={() => onSelectSession(session.session_id)}
          >
            <span className="session-title">{session.title}</span>
            <button
              className="session-delete"
              onClick={(e) => {
                e.stopPropagation()
                onDeleteSession(session.session_id)
              }}
            >
              ×
            </button>
          </div>
        ))}
        {sessions.length === 0 && (
          <div style={{ padding: '20px', textAlign: 'center', color: '#999', fontSize: '14px' }}>
            暂无会话，点击上方按钮创建
          </div>
        )}
      </div>
    </aside>
  )
}

export default Sidebar
