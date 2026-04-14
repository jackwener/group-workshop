function Sidebar({
  sessions,
  currentSession,
  onSelectSession,
  onCreateSession,
  onDeleteSession,
  loading
}) {
  const formatTime = (isoString) => {
    if (!isoString) return ''
    const date = new Date(isoString)
    return date.toLocaleString('zh-CN', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <button
          className="new-session-btn"
          onClick={onCreateSession}
          disabled={loading}
        >
          {loading ? '创建中...' : '+ 新建会话'}
        </button>
      </div>
      <div className="session-list">
        {sessions.length === 0 ? (
          <div style={{ padding: '20px', textAlign: 'center', color: '#999' }}>
            暂无会话
          </div>
        ) : (
          sessions.map(session => (
            <div
              key={session.session_id}
              className={`session-item ${currentSession?.session_id === session.session_id ? 'active' : ''}`}
              onClick={() => onSelectSession(session)}
            >
              <div style={{ flex: 1, minWidth: 0 }}>
                <div className="session-title">{session.title}</div>
                <div className="session-time">{formatTime(session.updated_at)}</div>
              </div>
              <button
                className="delete-btn"
                onClick={(e) => {
                  e.stopPropagation()
                  onDeleteSession(session.session_id)
                }}
                title="删除会话"
              >
                ×
              </button>
            </div>
          ))
        )}
      </div>
    </aside>
  )
}

export default Sidebar
