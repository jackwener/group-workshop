import { useState } from 'react';
import styles from './Sidebar.module.css';

function Sidebar({ 
  sessions, 
  currentSession, 
  onSelectSession, 
  onCreateSession, 
  onDeleteSession,
  loading 
}) {
  const [deleteConfirmId, setDeleteConfirmId] = useState(null);

  const handleDelete = (e, sessionId) => {
    e.stopPropagation();
    if (deleteConfirmId === sessionId) {
      onDeleteSession(sessionId);
      setDeleteConfirmId(null);
    } else {
      setDeleteConfirmId(sessionId);
      // 3秒后自动取消确认状态
      setTimeout(() => setDeleteConfirmId(null), 3000);
    }
  };

  return (
    <aside className={styles.sidebar}>
      <div className={styles.header}>
        <h3 className={styles.title}>历史会话</h3>
        <button 
          className={styles.newBtn}
          onClick={onCreateSession}
          disabled={loading}
        >
          + 新建
        </button>
      </div>
      
      <div className={styles.sessionList}>
        {sessions.length === 0 ? (
          <div className={styles.empty}>暂无会话</div>
        ) : (
          sessions.map((session) => (
            <div
              key={session.session_id}
              className={`${styles.sessionItem} ${
                currentSession?.session_id === session.session_id ? styles.active : ''
              }`}
              onClick={() => onSelectSession(session)}
            >
              <div className={styles.sessionInfo}>
                <div className={styles.sessionTitle}>{session.title}</div>
                <div className={styles.sessionMeta}>
                  {session.query_count} 条对话
                </div>
              </div>
              <button
                className={`${styles.deleteBtn} ${
                  deleteConfirmId === session.session_id ? styles.confirm : ''
                }`}
                onClick={(e) => handleDelete(e, session.session_id)}
                title={deleteConfirmId === session.session_id ? '再次点击确认删除' : '删除会话'}
              >
                {deleteConfirmId === session.session_id ? '✓' : '×'}
              </button>
            </div>
          ))
        )}
      </div>
    </aside>
  );
}

export default Sidebar;
