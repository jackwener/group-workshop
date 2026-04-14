import { useState, useEffect, useRef } from 'react'
import './App.css'

const API_BASE = '/api/v1/agent'

const ERROR_MESSAGES = {
  EMPTY_QUERY: '请输入问题',
  INVALID_QUERY: '问题过长，最多500字符',
  INVALID_SESSION: '会话不存在或已失效，请重新选择',
  INVALID_FILE_FORMAT: '仅支持PDF或HTML格式研报',
  FILE_TOO_LARGE: '文件过大，请上传小于10MB的文件',
  NOT_FOUND: '请求的资源不存在',
  LLM_UNAVAILABLE: 'AI服务暂时不可用，已切换至离线演示模式',
  UNAUTHORIZED: '请先登录系统',
}

const SUGGESTIONS = [
  '如何分析研报中的核心观点？',
  '这只股票的评级和目标价是多少？',
  '研报中的风险提示有哪些？',
  '对比最近3份研报的观点变化',
  '这只股票的投资逻辑是什么？',
  '研报中的财务数据摘要',
]

function App() {
  // T-036: 9 React useState
  const [sessions, setSessions] = useState([])
  const [currentSession, setCurrentSession] = useState(null)
  const [records, setRecords] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [capabilities, setCapabilities] = useState({})
  const [reports, setReports] = useState([])
  const [uploading, setUploading] = useState(false)

  const [deleteTarget, setDeleteTarget] = useState(null)
  const [reportDetail, setReportDetail] = useState(null)
  const [reportSearch, setReportSearch] = useState('')
  const fileInputRef = useRef(null)
  const chatEndRef = useRef(null)

  // Auto-dismiss error
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(null), 4000)
      return () => clearTimeout(timer)
    }
  }, [error])

  // Load capabilities and sessions on mount
  useEffect(() => {
    fetchCapabilities()
    fetchSessions()
  }, [])

  // Load records when session changes
  useEffect(() => {
    if (currentSession) {
      fetchRecords(currentSession.id)
      fetchReports()
    } else {
      setRecords([])
    }
  }, [currentSession])

  // Scroll to bottom when records change
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [records])

  // ── API helpers ──

  async function apiFetch(url, options = {}) {
    try {
      const res = await fetch(API_BASE + url, options)
      const data = await res.json()
      if (!res.ok) {
        const code = data?.error?.code || 'UNKNOWN'
        throw new Error(ERROR_MESSAGES[code] || data?.error?.message || '请求失败')
      }
      return data
    } catch (err) {
      if (err.message !== 'Failed to fetch') {
        setError(err.message)
      } else {
        setError('网络连接失败，请检查后端服务是否启动')
      }
      throw err
    }
  }

  // T-030: Load capabilities
  async function fetchCapabilities() {
    try {
      const data = await apiFetch('/capabilities')
      setCapabilities(data)
    } catch {}
  }

  // Load sessions
  async function fetchSessions() {
    try {
      const data = await apiFetch('/sessions')
      setSessions(data.sessions || [])
      if (!currentSession && data.sessions?.length > 0) {
        setCurrentSession(data.sessions[0])
      }
    } catch {}
  }

  // Load records for a session
  async function fetchRecords(sessionId) {
    try {
      const data = await apiFetch(`/sessions/${sessionId}/records`)
      setRecords(data.records || [])
    } catch {}
  }

  // Load reports
  async function fetchReports(keyword) {
    try {
      const url = keyword ? `/reports?keyword=${encodeURIComponent(keyword)}` : '/reports'
      const data = await apiFetch(url)
      setReports(data.reports || [])
    } catch {}
  }

  // T-015: Create new session
  async function handleCreateSession() {
    try {
      const data = await apiFetch('/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: '新会话' }),
      })
      const newSession = {
        id: data.session_id,
        title: data.title,
        created_at: data.created_at,
        updated_at: data.created_at,
        query_count: data.query_count,
      }
      setSessions(prev => [newSession, ...prev])
      setCurrentSession(newSession)
      setRecords([])
    } catch {}
  }

  // T-016: Delete session
  async function handleDeleteSession() {
    if (!deleteTarget) return
    try {
      await apiFetch(`/sessions/${deleteTarget}`, { method: 'DELETE' })
      setSessions(prev => {
        const filtered = prev.filter(s => s.id !== deleteTarget)
        if (currentSession?.id === deleteTarget) {
          setCurrentSession(filtered[0] || null)
        }
        return filtered
      })
    } catch {}
    setDeleteTarget(null)
  }

  // T-032: Submit question
  async function handleSend(query) {
    const q = query || inputValue.trim()
    if (!q || !currentSession || isLoading) return

    setIsLoading(true)
    setInputValue('')
    try {
      const data = await apiFetch('/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: q, session_id: currentSession.id }),
      })
      const newRecord = {
        id: `rec_${Date.now()}`,
        query: q,
        answer: data.answer,
        timestamp: data.timestamp,
        llm_used: data.llm_used,
        answer_source: data.answer_source,
        response_time_ms: data.response_time_ms,
      }
      setRecords(prev => [...prev, newRecord])
      // Update session in list
      setSessions(prev => prev.map(s =>
        s.id === currentSession.id
          ? { ...s, query_count: s.query_count + 1, updated_at: data.timestamp,
              title: s.query_count === 0 ? q.slice(0, 20) + (q.length > 20 ? '...' : '') : s.title }
          : s
      ))
      if (currentSession.query_count === 0) {
        setCurrentSession(prev => ({
          ...prev,
          title: q.slice(0, 20) + (q.length > 20 ? '...' : ''),
          query_count: 1,
        }))
      }
    } catch {}
    setIsLoading(false)
  }

  // T-053: Upload report
  async function handleUploadReport(e) {
    const file = e.target.files?.[0]
    if (!file || !currentSession) return

    setUploading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('session_id', currentSession.id)

      const res = await fetch(API_BASE + '/reports', { method: 'POST', body: formData })
      const data = await res.json()
      if (!res.ok) {
        const code = data?.error?.code || 'UNKNOWN'
        setError(ERROR_MESSAGES[code] || data?.error?.message || '上传失败')
      } else {
        fetchReports()
      }
    } catch {
      setError('上传失败，请重试')
    }
    setUploading(false)
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  // T-056: View report detail
  async function handleViewReport(reportId) {
    try {
      const data = await apiFetch(`/reports/${reportId}`)
      setReportDetail(data)
    } catch {}
  }

  // Report search with debounce
  useEffect(() => {
    const timer = setTimeout(() => fetchReports(reportSearch), 300)
    return () => clearTimeout(timer)
  }, [reportSearch])

  // Copy to clipboard
  function handleCopy(text) {
    navigator.clipboard.writeText(text)
  }

  // ── Render helpers ──

  const inputTooLong = inputValue.length > 500
  const canSend = inputValue.trim() && currentSession && !isLoading && !inputTooLong

  function getSourceLabel(source) {
    switch (source) {
      case 'copaw': return { text: 'CoPaw', cls: 'source-copaw' }
      case 'bailian': return { text: '百炼', cls: 'source-bailian' }
      default: return { text: '离线演示', cls: 'source-demo' }
    }
  }

  function formatTime(ts) {
    if (!ts) return ''
    try {
      return new Date(ts).toLocaleString('zh-CN')
    } catch { return ts }
  }

  // ── Capability chips ──
  function renderChips() {
    if (capabilities.copaw_configured) {
      return <span className="chip chip-green">CoPaw 桥接</span>
    }
    if (capabilities.bailian_configured) {
      return <span className="chip chip-blue">百炼</span>
    }
    return <span className="chip chip-gray">离线演示</span>
  }

  // ── Main content ──
  function renderMainContent() {
    // T-017: State A - no session
    if (!currentSession) {
      return (
        <div className="empty-state">
          <div className="empty-state-icon">💬</div>
          <div>请创建或选择一个会话开始</div>
        </div>
      )
    }

    // T-033: State B - session but no records
    if (records.length === 0 && !isLoading) {
      return (
        <div>
          <div className="empty-state" style={{ height: 'auto', marginBottom: 20 }}>
            <div className="empty-state-icon">🔍</div>
            <div>试试以下常见问题</div>
          </div>
          <div className="suggestions-grid">
            {SUGGESTIONS.map((q, i) => (
              <div key={i} className="suggestion-card" onClick={() => handleSend(q)}>
                {q}
              </div>
            ))}
          </div>
        </div>
      )
    }

    // T-034: State C - chat history
    return (
      <div className="chat-list">
        {records.map(r => {
          const source = getSourceLabel(r.answer_source)
          return (
            <div key={r.id} className="chat-pair">
              <div className="chat-message">
                <div className="chat-avatar avatar-user">U</div>
                <div className="chat-bubble bubble-user">{r.query}</div>
              </div>
              <div className="chat-message">
                <div className="chat-avatar avatar-ai">AI</div>
                <div className="chat-bubble bubble-ai">{r.answer}</div>
              </div>
              <div className="chat-meta">
                <span className={`source-badge ${source.cls}`}>{source.text}</span>
                {r.response_time_ms !== undefined && (
                  <span className="chat-time">{r.response_time_ms}ms</span>
                )}
                <span className="chat-time">{formatTime(r.timestamp)}</span>
                <button className="copy-btn" onClick={() => handleCopy(r.answer)}>
                  复制
                </button>
              </div>
            </div>
          )
        })}
        {isLoading && (
          <div className="chat-message">
            <div className="chat-avatar avatar-ai">AI</div>
            <div className="loading-dots"><span/><span/><span/></div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>
    )
  }

  return (
    <div className="app">
      {/* T-035: Error toast */}
      {error && <div className="error-toast">{error}</div>}

      {/* Confirm dialog */}
      {deleteTarget && (
        <div className="confirm-overlay" onClick={() => setDeleteTarget(null)}>
          <div className="confirm-dialog" onClick={e => e.stopPropagation()}>
            <div className="confirm-title">删除会话</div>
            <div className="confirm-message">确定删除此会话及其所有记录吗？此操作不可撤销。</div>
            <div className="confirm-actions">
              <button className="confirm-cancel" onClick={() => setDeleteTarget(null)}>取消</button>
              <button className="confirm-ok" onClick={handleDeleteSession}>确认删除</button>
            </div>
          </div>
        </div>
      )}

      {/* Report detail modal */}
      {reportDetail && (
        <div className="report-detail-overlay" onClick={() => setReportDetail(null)}>
          <div className="report-detail" onClick={e => e.stopPropagation()}>
            <h3>{reportDetail.title || '研报详情'}</h3>
            <div className="report-field">
              <label>评级</label>
              <div className="report-field-value">{reportDetail.rating || '-'}</div>
            </div>
            <div className="report-field">
              <label>目标价</label>
              <div className="report-field-value">{reportDetail.target_price || '-'}</div>
            </div>
            <div className="report-field">
              <label>核心观点</label>
              <div className="report-field-value">
                {(reportDetail.core_views || []).map((v, i) => (
                  <div key={i} style={{marginBottom: 4}}>• {v}</div>
                ))}
              </div>
            </div>
            <div className="report-field">
              <label>完整内容</label>
              <div className="report-field-value" style={{maxHeight: 300, overflow: 'auto', whiteSpace: 'pre-wrap'}}>
                {reportDetail.full_content || '-'}
              </div>
            </div>
            <button className="report-close" onClick={() => setReportDetail(null)}>关闭</button>
          </div>
        </div>
      )}

      {/* T-013: Header */}
      <header className="header">
        <div className="header-left">
          <span className="header-title">投研问答助手</span>
          {renderChips()}
        </div>
        <div className="header-right">
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.html"
            style={{ display: 'none' }}
            onChange={handleUploadReport}
          />
          <button
            className="upload-btn"
            disabled={!currentSession || uploading}
            onClick={() => fileInputRef.current?.click()}
          >
            {uploading ? '上传中...' : '上传研报'}
          </button>
        </div>
      </header>

      {/* T-013: Body = Sidebar + Main */}
      <div className="body">
        {/* T-014: Sidebar */}
        <aside className="sidebar">
          <div className="sidebar-header">
            <button className="new-session-btn" onClick={handleCreateSession}>
              + 新建会话
            </button>
          </div>
          <div className="session-list">
            {sessions.map(s => (
              <div
                key={s.id}
                className={`session-item ${currentSession?.id === s.id ? 'active' : ''}`}
                onClick={() => setCurrentSession(s)}
              >
                <div className="session-info">
                  <div className="session-title">{s.title}</div>
                  <div className="session-meta">{s.query_count} 条问答</div>
                </div>
                <button
                  className="session-delete"
                  onClick={e => { e.stopPropagation(); setDeleteTarget(s.id) }}
                >
                  ×
                </button>
              </div>
            ))}
          </div>

          {/* Reports section in sidebar */}
          {reports.length > 0 && (
            <div className="reports-section" style={{padding: '0 12px 12px'}}>
              <div className="reports-title">研报列表</div>
              <input
                className="search-input"
                placeholder="搜索研报..."
                value={reportSearch}
                onChange={e => setReportSearch(e.target.value)}
              />
              {reports.map(r => (
                <div key={r.id} className="report-card" onClick={() => handleViewReport(r.id)}>
                  <div className="report-card-title">{r.title || '未知标题'}</div>
                  <div className="report-card-meta">
                    {r.rating} | {r.target_price}
                  </div>
                </div>
              ))}
            </div>
          )}
        </aside>

        {/* Main content area */}
        <div className="main">
          <div className="main-content">
            {renderMainContent()}
          </div>

          {/* T-031: Input area */}
          <div className="input-area">
            <div className="input-wrapper">
              <textarea
                className={`input-textarea ${inputTooLong ? 'error' : ''}`}
                rows={3}
                placeholder={currentSession ? '请输入您的问题...' : '请先创建或选择会话'}
                value={inputValue}
                onChange={e => setInputValue(e.target.value)}
                onKeyDown={e => {
                  if (e.key === 'Enter' && !e.shiftKey && canSend) {
                    e.preventDefault()
                    handleSend()
                  }
                }}
                disabled={!currentSession}
              />
              <div className="input-actions">
                <button className="send-btn" disabled={!canSend} onClick={() => handleSend()}>
                  {isLoading ? '发送中...' : '发送'}
                </button>
                <button className="clear-btn" onClick={() => setInputValue('')}>
                  清空
                </button>
              </div>
            </div>
            {inputTooLong && (
              <div className="input-hint hint-error">问题过长，请精简（{inputValue.length}/500）</div>
            )}
            {!currentSession && (
              <div className="input-hint hint-info">请先创建或选择会话</div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
