import { useState, useEffect, useCallback } from 'react';
import ConfirmDialog from '../common/ConfirmDialog';
import { formatTime } from '../../utils/formatTime';
import styles from './Sidebar.module.css';

export default function Sidebar({ sessions, currentSession, onSelect, onCreate, onDelete }) {
  const [contextMenu, setContextMenu] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);

  const handleContextMenu = useCallback((e, session) => {
    e.preventDefault();
    setContextMenu({ x: e.clientX, y: e.clientY, session });
  }, []);

  const handleDeleteClick = useCallback(() => {
    if (contextMenu) {
      setDeleteTarget(contextMenu.session);
      setContextMenu(null);
    }
  }, [contextMenu]);

  const handleConfirmDelete = useCallback(() => {
    if (deleteTarget) {
      onDelete(deleteTarget.session_id);
      setDeleteTarget(null);
    }
  }, [deleteTarget, onDelete]);

  useEffect(() => {
    const close = () => setContextMenu(null);
    document.addEventListener('click', close);
    return () => document.removeEventListener('click', close);
  }, []);

  return (
    <aside className={styles.sidebar}>
      <button className={styles.newBtn} onClick={() => onCreate()}>
        + 新建
      </button>
      <div className={styles.list}>
        {sessions.map(session => (
          <div
            key={session.session_id}
            className={`${styles.sessionItem} ${
              currentSession?.session_id === session.session_id ? styles.sessionItemActive : ''
            }`}
            onClick={() => onSelect(session)}
            onContextMenu={e => handleContextMenu(e, session)}
          >
            <span className={styles.sessionTitle}>{session.title}</span>
            <span className={styles.sessionTime}>{formatTime(session.updated_at)}</span>
          </div>
        ))}
      </div>

      {contextMenu && (
        <div
          className={styles.contextMenu}
          style={{ left: contextMenu.x, top: contextMenu.y }}
        >
          <button className={styles.contextMenuItem} onClick={handleDeleteClick}>
            删除
          </button>
        </div>
      )}

      {deleteTarget && (
        <ConfirmDialog
          title="删除会话"
          message={`确认删除「${deleteTarget.title}」？删除后不可恢复。`}
          onConfirm={handleConfirmDelete}
          onCancel={() => setDeleteTarget(null)}
        />
      )}
    </aside>
  );
}
