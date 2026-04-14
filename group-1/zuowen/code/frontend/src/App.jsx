/**
 * 投研问答助手 — 主应用组件
 * 对齐 Spec 06 功能规格说明
 * 布局: Header + Sidebar + Main + InputArea
 */
import { useState, useEffect } from 'react'
import './App.css'

const API_BASE = 'http://localhost:5001/api/v1/agent'

export default function App() {
  // ── 7 个 State 变量（对齐 Spec 06 §7）──
  const [sessions, setSessions] = useState([])
  const [currentSession, setCurrentSession] = useState(null)
  const [records, setRecords] = useState([])
  const [query, setQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [capabilities, setCapabilities] = useState({})
  const [error, setError] = useState(null)

  // ── 初始化：加载能力状态 + 会话列表 ──
  useEffect(() => {
    fetchCapabilities()
    fetchSessions()
  }, [])

  async function fetchCapabilities() {
    try {
      const res = await fetch(`${API_BASE}/capabilities`)
      const data = await res.json()
      setCapabilities(data)
    } catch (e) {
      console.error('能力探测失败:', e)
    }
  }

  async function fetchSessions() {
    try {
      const res = await fetch(`${API_BASE}/sessions`)
      const data = await res.json()
      setSessions(data.sessions || [])
    } catch (e) {
      console.error('加载会话失败:', e)
    }
  }

  // ── Sidebar：新建会话 ──
  async function createSession() {
    try {
      const res = await fetch(`${API_BASE}/sessions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: '新会话' }),
      })
      const data = await res.json()
      const newSession = {
        session_id: data.session_id,
        title: data.title,
        created_at: data.created_at,
        updated_at: data.created_at,
        query_count: data.query_count,
      }
      setSessions(prev => [newSession, ...prev])
      selectSession(newSession)
    } catch (e) {
      setError('创建会话失败')
    }
  }

  // ── Sidebar：删除会话 ──
  async function deleteSession(sessionId, e) {
    e.stopPropagation()
    if (!confirm('确认删除该会话？')) return
    try {
      await fetch(`${API_BASE}/sessions/${sessionId}`, { method: 'DELETE' })
      setSessions(prev => prev.filter(s => s.session_id !== sessionId))
      if (currentSession?.session_id === sessionId) {
        setCurrentSession(null)
        setRecords([])
      }
    } catch (e) {
      setError('删除会话失败')
    }
  }

  // ── Sidebar：选中会话 ──
  async function selectSession(session) {
    setCurrentSession(session)
    setError(null)
    try {
      const res = await fetch(`${API_BASE}/sessions/${session.session_id}/records`)
      const data = await res.json()
      setRecords(data.records || [])
    } catch (e) {
      setError('加载记录失败')
    }
  }

  // ── 提问提交 ──
  async function handleAsk() {
    if (!query.trim()) { setError('请输入问题'); return }
    if (!currentSession) { setError('请先创建或选择一个会话'); return }
    setIsLoading(true)
    setError(null)
    try {
      const res = await fetch(`${API_BASE}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: query.trim(),
          session_id: currentSession.session_id,
        }),
      })
      const data = await res.json()
      if (!res.ok) {
        const errMsg = {
          EMPTY_QUERY: '请输入问题',
          INVALID_QUERY: '问题过长',
          SESSION_NOT_FOUND: '会话不存在',
          UPSTREAM_ERROR: '服务暂时不可用，请稍后重试',
        }
        setError(errMsg[data.error?.code] || data.error?.message || '请求失败')
        return
      }
      // 追加记录
      const newRecord = {
        id: `rec_${Date.now()}`,
        query: query.trim(),
        answer: data.answer,
        llm_used: data.llm_used,
        model: data.model,
        answer_source: data.answer_source,
        response_time_ms: data.response_time_ms,
        timestamp: new Date().toISOString(),
      }
      setRecords(prev => [...prev, newRecord])
      setQuery('')
      // 刷新会话列表（标题可能自动更新）
      fetchSessions()
    } catch (e) {
      setError('网络错误，请检查后端服务')
    } finally {
      setIsLoading(false)
    }
  }

  // ── 来源标签 ──
  function SourceTag({ source }) {
    const styles = {
      copaw: { bg: '#e6f7e6', color: '#2e7d32', label: 'CoPaw' },
      bailian: { bg: '#e3f2fd', color: '#1565c0', label: '百炼' },
      demo: { bg: '#f5f5f5', color: '#757575', label: '离线演示' },
    }
    const s = styles[source] || styles.demo
    return (
      <span style={{
        background: s.bg, color: s.color,
        padding: '2px 8px', borderRadius: '12px', fontSize: '12px',
      }}>
        {s.label}
      </span>
    )
  }

  // ── 常见问题网格 ──
  const quickQuestions = [
    '贵州茅台最新研报摘要',
    '宁德时代对比分析',
    '比亚迪2026年营收预测',
    '光伏行业趋势研究',
  ]

  // ── 渲染 ──
  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <h1>投研问答助手</h1>
        <div className="chips">
          {capabilities.copaw_configured && (
            <span className="chip chip-green">CoPaw 桥接</span>
          )}
          {capabilities.bailian_configured ? (
            <span className="chip chip-blue">百炼 · {capabilities.model}</span>
          ) : (
            <span className="chip chip-gray">离线演示</span>
          )}
        </div>
      </header>

      <div className="body">
        {/* Sidebar */}
        <aside className="sidebar">
          <button className="btn-new" onClick={createSession}>+ 新建会话</button>
          <div className="session-list">
            {sessions.map(s => (
              <div
                key={s.session_id}
                className={`session-item ${currentSession?.session_id === s.session_id ? 'active' : ''}`}
                onClick={() => selectSession(s)}
              >
                <span className="session-title">{s.title}</span>
                <span className="session-count">{s.query_count}</span>
                <button className="btn-delete" onClick={(e) => deleteSession(s.session_id, e)}>×</button>
              </div>
            ))}
          </div>
        </aside>

        {/* Main Content */}
        <main className="main">
          {/* 错误提示 */}
          {error && <div className="error-bar">{error}</div>}

          {/* 三态渲染（对齐 Spec 06 §4）*/}
          {!currentSession ? (
            // A 空状态
            <div className="empty-state">
              <p>请创建或选择一个会话开始</p>
            </div>
          ) : records.length === 0 ? (
            // B 常见问题网格
            <div className="quick-questions">
              <p>试试问我：</p>
              <div className="grid">
                {quickQuestions.map((q, i) => (
                  <button key={i} className="quick-btn" onClick={() => { setQuery(q) }}>
                    {q}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            // C 对话历史
            <div className="records">
              {records.map(r => (
                <div key={r.id} className="record-card">
                  <div className="record-query">
                    <strong>Q:</strong> {r.query}
                  </div>
                  <div className="record-answer">
                    <strong>A:</strong> {r.answer}
                  </div>
                  <div className="record-meta">
                    <SourceTag source={r.answer_source} />
                    {r.model && <span className="meta-model">{r.model}</span>}
                    <span className="meta-time">{r.response_time_ms}ms</span>
                    <span className="meta-ts">{new Date(r.timestamp).toLocaleTimeString()}</span>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* 输入区域（对齐 Spec 06 §5）*/}
          {currentSession && (
            <div className="input-area">
              <textarea
                rows={3}
                placeholder="请输入您的问题..."
                value={query}
                onChange={e => setQuery(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleAsk() } }}
                disabled={isLoading}
              />
              <div className="input-actions">
                <button onClick={handleAsk} disabled={isLoading}>
                  {isLoading ? '发送中…' : '发送'}
                </button>
                <button onClick={() => setQuery('')} disabled={isLoading}>清空</button>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}
