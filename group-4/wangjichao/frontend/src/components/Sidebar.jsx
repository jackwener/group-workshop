import { useState } from 'react'

function Sidebar({ sessions, currentSession, onSelectSession, onNewSession, onDeleteSession, onRenameSession }) {
  const [editingId, setEditingId] = useState(null)
  const [editTitle, setEditTitle] = useState('')

  const handleDoubleClick = (session) => {
    setEditingId(session.session_id)
    setEditTitle(session.title)
  }

  const handleRename = (sessionId) => {
    if (editTitle.trim()) {
      onRenameSession(sessionId, editTitle.trim())
    }
    setEditingId(null)
  }

  const handleKeyDown = (e, sessionId) => {
    if (e.key === 'Enter') handleRename(sessionId)
    else if (e.key === 'Escape') setEditingId(null)
  }

  return (
    <aside className="w-72 bg-navy-900 flex flex-col border-r border-slate-700/50">
      {/* 新建按钮 */}
      <div className="p-4">
        <button
          onClick={onNewSession}
          className="w-full py-2.5 px-4 bg-gradient-to-r from-brand-500 to-brand-600 text-white rounded-lg hover:from-brand-600 hover:to-brand-700 transition-all duration-200 text-sm font-semibold shadow-lg shadow-brand-500/20 active:scale-[0.98] flex items-center justify-center space-x-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" /></svg>
          <span>新建会话</span>
        </button>
      </div>

      {/* 分隔线 */}
      <div className="px-4 mb-2">
        <p className="text-[10px] text-slate-500 uppercase tracking-widest font-semibold">会话记录</p>
      </div>

      {/* 会话列表 */}
      <div className="flex-1 overflow-y-auto px-3 pb-3">
        {sessions.length === 0 ? (
          <p className="text-slate-500 text-sm text-center py-8">暂无会话</p>
        ) : (
          sessions.map(session => (
            <div
              key={session.session_id}
              onClick={() => onSelectSession(session)}
              onDoubleClick={() => handleDoubleClick(session)}
              className={`group flex items-center justify-between p-3 rounded-lg cursor-pointer mb-1 transition-all duration-150 ${
                currentSession?.session_id === session.session_id
                  ? 'bg-brand-500/10 border border-brand-500/20'
                  : 'hover:bg-white/5 border border-transparent'
              }`}
            >
              <div className="flex-1 min-w-0">
                {editingId === session.session_id ? (
                  <input
                    type="text"
                    value={editTitle}
                    onChange={(e) => setEditTitle(e.target.value)}
                    onBlur={() => handleRename(session.session_id)}
                    onKeyDown={(e) => handleKeyDown(e, session.session_id)}
                    className="w-full text-sm bg-navy-800 border border-brand-500/40 rounded px-2 py-1 text-white focus:outline-none focus:border-brand-500"
                    autoFocus
                  />
                ) : (
                  <>
                    <p className={`text-sm font-medium truncate ${
                      currentSession?.session_id === session.session_id ? 'text-brand-400' : 'text-slate-300'
                    }`}>{session.title}</p>
                    <p className="text-xs text-slate-500 mt-0.5">{session.query_count || 0} 条对话</p>
                  </>
                )}
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  if (window.confirm('确定删除该会话？')) onDeleteSession(session.session_id)
                }}
                className="opacity-0 group-hover:opacity-100 ml-2 text-slate-500 hover:text-rose-400 transition-all text-lg"
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
