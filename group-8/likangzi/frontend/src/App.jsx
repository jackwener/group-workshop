import { useState, useEffect, useCallback } from 'react'
import './App.css'

const API_BASE = '/api/v1/agent'

// 常见问题示例
const SUGGESTED_QUESTIONS = [
  '贵州茅台最新评级？',
  '沪深300指数近期走势如何？',
  '什么是量化投资？',
  '如何分析公司财报？',
  '基金定投的优势是什么？',
  'A股市场近期热点板块？',
]

// 错误码映射
const ERROR_MAP = {
  EMPTY_QUERY: '请输入问题',
  INVALID_QUERY: '问题过长',
  SESSION_NOT_FOUND: '会话不存在',
  INVALID_SESSION_ID: '会话 ID 格式错误',
  INVALID_FILE_TYPE: '不支持的文件类型，仅支持 PDF/HTML',
  FILE_TOO_LARGE: '文件大小超过 50MB 限制',
  REPORT_NOT_FOUND: '研报不存在',
  PARSE_FAILED: '研报解析失败',
}

function App() {
  // State 变量
  const [sessions, setSessions] = useState([])
  const [currentSession, setCurrentSession] = useState(null)
  const [records, setRecords] = useState([])
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [capabilities, setCapabilities] = useState(null)
  const [activeTab, setActiveTab] = useState('chat') // 'chat' | 'report'
  const [reports, setReports] = useState([])
  const [selectedReports, setSelectedReports] = useState([])
  const [compareResult, setCompareResult] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [selectedReport, setSelectedReport] = useState(null)

  // API 调用封装
  const apiCall = async (url, options = {}) => {
    try {
      const res = await fetch(url, {
        headers: { 'Content-Type': 'application/json' },
        ...options,
      })
      const data = await res.json()
      if (!res.ok) {
        throw data.error || { code: 'UNKNOWN', message: '请求失败' }
      }
      return data
    } catch (err) {
      if (err.code) throw err
      throw { code: 'NETWORK_ERROR', message: '服务异常，请稍后重试' }
    }
  }

  // 错误处理 - 3秒后自动消失
  const showError = useCallback((err) => {
    const message = ERROR_MAP[err.code] || err.message || '未知错误'
    setError(message)
    setTimeout(() => setError(null), 3000)
  }, [])

  // 加载能力状态
  useEffect(() => {
    const loadCapabilities = async () => {
      try {
        const data = await apiCall(`${API_BASE}/capabilities`)
        setCapabilities(data)
      } catch (err) {
        console.error('加载能力状态失败:', err)
        setCapabilities({ copaw_configured: false, bailian_configured: false })
      }
    }
    loadCapabilities()
  }, [])

  // 加载会话列表
  const loadSessions = useCallback(async () => {
    try {
      const data = await apiCall(`${API_BASE}/sessions`)
      setSessions(data.sessions || [])
      return data.sessions || []
    } catch (err) {
      showError(err)
      return []
    }
  }, [showError])

  // 页面加载时获取会话列表
  useEffect(() => {
    loadSessions().then((sessionsList) => {
      if (sessionsList.length > 0 && !currentSession) {
        setCurrentSession(sessionsList[0])
      }
    })
  }, [loadSessions])

  // 加载会话记录
  const loadRecords = useCallback(async (sessionId) => {
    try {
      const data = await apiCall(`${API_BASE}/sessions/${sessionId}/records`)
      setRecords(data.records || [])
    } catch (err) {
      if (err.code === 'SESSION_NOT_FOUND') {
        showError(err)
        loadSessions()
      } else {
        showError(err)
      }
    }
  }, [showError, loadSessions])

  // 切换会话时加载记录
  useEffect(() => {
    if (currentSession) {
      loadRecords(currentSession.session_id)
    } else {
      setRecords([])
    }
  }, [currentSession, loadRecords])

  // 加载研报列表
  const loadReports = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/reports`)
      const data = await res.json()
      if (res.ok) {
        setReports(data.reports || [])
      }
    } catch (err) {
      console.error('加载研报列表失败:', err)
    }
  }, [])

  // 切换到研报 tab 时加载列表
  useEffect(() => {
    if (activeTab === 'report') {
      loadReports()
    }
  }, [activeTab, loadReports])

  // 创建新会话
  const createSession = async () => {
    try {
      const data = await apiCall(`${API_BASE}/sessions`, {
        method: 'POST',
        body: JSON.stringify({ title: '新会话' }),
      })
      const newSession = {
        session_id: data.session_id,
        title: data.title,
        created_at: data.created_at,
        query_count: data.query_count,
      }
      setSessions((prev) => [newSession, ...prev])
      setCurrentSession(newSession)
    } catch (err) {
      showError(err)
    }
  }

  // 删除会话
  const deleteSession = async (sessionId, e) => {
    e.stopPropagation()
    if (!window.confirm('确认删除该会话？')) return

    try {
      await apiCall(`${API_BASE}/sessions/${sessionId}`, {
        method: 'DELETE',
      })
      setSessions((prev) => prev.filter((s) => s.session_id !== sessionId))
      if (currentSession?.session_id === sessionId) {
        setCurrentSession(null)
      }
    } catch (err) {
      showError(err)
    }
  }

  // 选择会话
  const selectSession = (session) => {
    setCurrentSession(session)
  }

  // 发送问题
  const sendQuery = async () => {
    if (!query.trim() || !currentSession) return

    setLoading(true)
    try {
      const data = await apiCall(`${API_BASE}/ask`, {
        method: 'POST',
        body: JSON.stringify({
          query: query.trim(),
          session_id: currentSession.session_id,
        }),
      })

      // 添加新记录
      const newRecord = {
        query: query.trim(),
        answer: data.answer,
        llm_used: data.llm_used,
        model: data.model,
        response_time_ms: data.response_time_ms,
        answer_source: data.answer_source,
        created_at: new Date().toISOString(),
      }
      setRecords((prev) => [...prev, newRecord])
      setQuery('')

      // 刷新会话列表（query_count 和 title 可能变化）
      loadSessions()
    } catch (err) {
      showError(err)
    } finally {
      setLoading(false)
    }
  }

  // 清空输入
  const clearQuery = () => {
    setQuery('')
  }

  // 上传研报
  const uploadReport = async (file) => {
    if (!file) return
    setUploading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      if (currentSession) {
        formData.append('session_id', currentSession.session_id)
      }
      const res = await fetch(`${API_BASE}/reports/upload`, {
        method: 'POST',
        body: formData,
      })
      const data = await res.json()
      if (!res.ok) {
        throw data.error || { code: 'UNKNOWN', message: '上传失败' }
      }
      // 刷新列表
      loadReports()
    } catch (err) {
      showError(err)
    } finally {
      setUploading(false)
    }
  }

  // 处理文件选择
  const handleFileSelect = (e) => {
    const file = e.target.files[0]
    if (file) uploadReport(file)
    e.target.value = '' // reset
  }

  // 处理拖拽
  const handleDrop = (e) => {
    e.preventDefault()
    const file = e.dataTransfer.files[0]
    if (file) uploadReport(file)
  }

  const handleDragOver = (e) => {
    e.preventDefault()
  }

  // 切换研报选择（用于对比）
  const toggleReportSelection = (reportId) => {
    setSelectedReports(prev => {
      if (prev.includes(reportId)) {
        return prev.filter(id => id !== reportId)
      }
      if (prev.length >= 5) return prev
      return [...prev, reportId]
    })
  }

  // 研报对比
  const compareReports = async () => {
    if (selectedReports.length < 2) return
    try {
      const data = await apiCall(`${API_BASE}/reports/compare`, {
        method: 'POST',
        body: JSON.stringify({ report_ids: selectedReports }),
      })
      setCompareResult(data.comparison_table)
    } catch (err) {
      showError(err)
    }
  }

  // 查看研报详情
  const viewReportDetail = async (reportId) => {
    try {
      const res = await fetch(`${API_BASE}/reports/${reportId}`)
      const data = await res.json()
      if (res.ok) {
        setSelectedReport(data.report)
      }
    } catch (err) {
      console.error('获取研报详情失败:', err)
    }
  }

  // 点击建议问题
  const useSuggestedQuestion = (question) => {
    setQuery(question)
  }

  // 格式化时间戳
  const formatTime = (isoString) => {
    if (!isoString) return ''
    const date = new Date(isoString)
    return date.toLocaleString('zh-CN', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  // 获取来源标签样式和文本
  const getSourceInfo = (source) => {
    switch (source) {
      case 'copaw':
        return { className: 'source-copaw', text: 'CoPaw' }
      case 'bailian':
        return { className: 'source-bailian', text: '百炼' }
      case 'demo':
      default:
        return { className: 'source-demo', text: '离线演示' }
    }
  }

  // 渲染能力状态芯片
  const renderCapabilityChips = () => {
    if (!capabilities) return null

    const chips = []
    if (capabilities.copaw_configured) {
      chips.push(
        <span key="copaw" className="capability-chip chip-copaw">
          CoPaw 桥接
        </span>
      )
    }
    if (capabilities.bailian_configured) {
      chips.push(
        <span key="bailian" className="capability-chip chip-bailian">
          百炼·{capabilities.model || 'qwen'}
        </span>
      )
    }
    if (chips.length === 0) {
      chips.push(
        <span key="demo" className="capability-chip chip-demo">
          离线演示
        </span>
      )
    }
    return chips
  }

  return (
    <div className="app-container">
      {/* 错误提示 */}
      {error && <div className="error-toast">{error}</div>}

      {/* Header 区域 */}
      <header className="header">
        <h1><svg className="logo-icon" width="26" height="26" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M14 2L4 8v12l10 6 10-6V8L14 2z" stroke="#fff" strokeWidth="1.5" fill="none" opacity="0.9"/><circle cx="14" cy="14" r="4" fill="#fff" opacity="0.95"/><line x1="14" y1="10" x2="14" y2="4" stroke="#fff" strokeWidth="1.2" opacity="0.7"/><line x1="17.5" y1="12" x2="22" y2="8" stroke="#fff" strokeWidth="1.2" opacity="0.7"/><line x1="17.5" y1="16" x2="22" y2="20" stroke="#fff" strokeWidth="1.2" opacity="0.7"/><line x1="14" y1="18" x2="14" y2="24" stroke="#fff" strokeWidth="1.2" opacity="0.7"/><line x1="10.5" y1="16" x2="6" y2="20" stroke="#fff" strokeWidth="1.2" opacity="0.7"/><line x1="10.5" y1="12" x2="6" y2="8" stroke="#fff" strokeWidth="1.2" opacity="0.7"/></svg>投研小策</h1>
        <div className="capability-chips">{renderCapabilityChips()}</div>
      </header>

      {/* 主体 */}
      <div className="body">
        {/* Sidebar 会话管理 */}
        <aside className="sidebar">
          <div className="sidebar-header">
            <button className="new-session-btn" onClick={createSession}>
              + 新建
            </button>
          </div>
          <div className="sessions-list">
            {sessions.length === 0 ? (
              <div className="empty-sessions">暂无会话</div>
            ) : (
              sessions.map((session) => (
                <div
                  key={session.session_id}
                  className={`session-item ${
                    currentSession?.session_id === session.session_id
                      ? 'active'
                      : ''
                  }`}
                  onClick={() => selectSession(session)}
                >
                  <div className="session-info">
                    <div className="session-title">{session.title}</div>
                    <div className="session-meta">
                      {session.query_count || 0} 条对话
                    </div>
                  </div>
                  <button
                    className="delete-btn"
                    onClick={(e) => deleteSession(session.session_id, e)}
                    title="删除会话"
                  >
                    ×
                  </button>
                </div>
              ))
            )}
          </div>
        </aside>

        {/* Main 内容区 */}
        <div className="main-area">
          {/* Tab 切换 */}
          {currentSession && (
            <div className="tab-bar">
              <button className={`tab-btn ${activeTab === 'chat' ? 'active' : ''}`} onClick={() => setActiveTab('chat')}>
                问答
              </button>
              <button className={`tab-btn ${activeTab === 'report' ? 'active' : ''}`} onClick={() => setActiveTab('report')}>
                研报分析
              </button>
            </div>
          )}

          <div className="content">
            {/* 状态 A：未选择会话 */}
            {!currentSession && (
              <div className="empty-state">
                <div className="empty-icon">💬</div>
                <div>请创建或选择一个会话开始</div>
              </div>
            )}

            {/* 状态 B：有会话但无记录 */}
            {currentSession && activeTab === 'chat' && records.length === 0 && (
              <div className="welcome-state">
                <h3>👋 欢迎使用投研小策</h3>
                <p>选择一个常见问题开始，或直接输入您的问题</p>
                <div className="suggested-questions">
                  {SUGGESTED_QUESTIONS.map((question, index) => (
                    <div
                      key={index}
                      className="question-card"
                      onClick={() => useSuggestedQuestion(question)}
                    >
                      {question}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 状态 C：有记录 */}
            {currentSession && activeTab === 'chat' && records.length > 0 && (
              <div className="chat-history">
                {records.map((record, index) => {
                  const sourceInfo = getSourceInfo(record.answer_source)
                  return (
                    <div key={index} className="chat-record">
                      {/* 用户问题 - 右侧 */}
                      <div className="message user-message">
                        <div className="message-bubble user-bubble">
                          {record.query}
                        </div>
                      </div>
                      {/* AI 回答 - 左侧 */}
                      <div className="message ai-message">
                        <div className="message-bubble ai-bubble">
                          <div className="answer-content">{record.answer}</div>
                          <div className="answer-meta">
                            <span className={`source-tag ${sourceInfo.className}`}>
                              {sourceInfo.text}
                            </span>
                            <span className="response-time">
                              {record.response_time_ms}ms
                            </span>
                            <span className="timestamp">
                              {formatTime(record.created_at)}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            )}

            {/* 研报分析区域 */}
            {currentSession && activeTab === 'report' && (
              <div className="report-section">
                {/* 上传区 */}
                <div className="report-upload-area" onDrop={handleDrop} onDragOver={handleDragOver}>
                  <div className="upload-icon">📄</div>
                  <p>拖拽文件到此处，或点击选择文件</p>
                  <p className="upload-hint">支持 PDF、HTML 格式，最大 50MB</p>
                  <input
                    type="file"
                    accept=".pdf,.html,.htm"
                    onChange={handleFileSelect}
                    style={{ display: 'none' }}
                    id="report-file-input"
                  />
                  <label htmlFor="report-file-input" className="upload-btn">
                    {uploading ? '上传中...' : '选择文件'}
                  </label>
                </div>

                {/* 研报列表 */}
                {reports.length > 0 && (
                  <div className="report-list">
                    <div className="report-list-header">
                      <h3>已上传研报 ({reports.length})</h3>
                      {selectedReports.length >= 2 && (
                        <button className="compare-btn" onClick={compareReports}>
                          对比选中 ({selectedReports.length})
                        </button>
                      )}
                    </div>
                    <div className="report-cards">
                      {reports.map(report => (
                        <div key={report.report_id} className={`report-card ${selectedReports.includes(report.report_id) ? 'selected' : ''}`}>
                          <div className="report-card-header">
                            <input
                              type="checkbox"
                              checked={selectedReports.includes(report.report_id)}
                              onChange={() => toggleReportSelection(report.report_id)}
                            />
                            <span className={`report-status ${report.status}`}>{report.status === 'parsed' ? '已解析' : '解析失败'}</span>
                          </div>
                          <div className="report-card-body" onClick={() => viewReportDetail(report.report_id)}>
                            <div className="report-filename">{report.file_name}</div>
                            <div className="report-meta">
                              <span>{report.file_type.toUpperCase()}</span>
                              <span>{(report.file_size / 1024).toFixed(1)} KB</span>
                              <span>{formatTime(report.uploaded_at)}</span>
                            </div>
                            {report.extracted_data && (
                              <div className="report-extract-preview">
                                {report.extracted_data.rating && <span className="extract-tag">评级: {report.extracted_data.rating}</span>}
                                {report.extracted_data.target_price && <span className="extract-tag">目标价: {report.extracted_data.target_price}元</span>}
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* 研报详情弹窗 */}
                {selectedReport && (
                  <div className="report-detail-overlay" onClick={() => setSelectedReport(null)}>
                    <div className="report-detail-modal" onClick={e => e.stopPropagation()}>
                      <div className="modal-header">
                        <h3>{selectedReport.file_name}</h3>
                        <button className="modal-close" onClick={() => setSelectedReport(null)}>×</button>
                      </div>
                      <div className="modal-body">
                        {selectedReport.extracted_data ? (
                          <>
                            <div className="detail-section">
                              <h4>评级</h4>
                              <p>{selectedReport.extracted_data.rating || '未识别'}</p>
                            </div>
                            <div className="detail-section">
                              <h4>目标价</h4>
                              <p>{selectedReport.extracted_data.target_price ? `${selectedReport.extracted_data.target_price}元` : '未识别'}</p>
                            </div>
                            <div className="detail-section">
                              <h4>核心观点</h4>
                              {selectedReport.extracted_data.key_points && selectedReport.extracted_data.key_points.length > 0 ? (
                                <ul>{selectedReport.extracted_data.key_points.map((point, i) => <li key={i}>{point}</li>)}</ul>
                              ) : <p>未识别</p>}
                            </div>
                            <div className="detail-section">
                              <h4>摘要</h4>
                              <p className="report-summary">{selectedReport.extracted_data.summary || '未识别'}</p>
                            </div>
                          </>
                        ) : (
                          <p className="parse-failed">解析失败: {selectedReport.error_message}</p>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {/* 对比结果 */}
                {compareResult && (
                  <div className="compare-section">
                    <div className="compare-header">
                      <h3>研报对比结果</h3>
                      <button className="close-compare" onClick={() => setCompareResult(null)}>关闭</button>
                    </div>
                    <div className="compare-table-wrapper">
                      <table className="compare-table">
                        <thead>
                          <tr>
                            <th>维度</th>
                            {compareResult.reports.map(r => <th key={r.report_id}>{r.file_name}</th>)}
                          </tr>
                        </thead>
                        <tbody>
                          <tr>
                            <td className="dim-label">评级</td>
                            {compareResult.reports.map(r => <td key={r.report_id}>{r.rating || '-'}</td>)}
                          </tr>
                          <tr>
                            <td className="dim-label">目标价</td>
                            {compareResult.reports.map(r => <td key={r.report_id}>{r.target_price ? `${r.target_price}元` : '-'}</td>)}
                          </tr>
                          <tr>
                            <td className="dim-label">核心观点</td>
                            {compareResult.reports.map(r => (
                              <td key={r.report_id}>
                                {r.key_points && r.key_points.length > 0
                                  ? <ul className="compare-points">{r.key_points.map((p, i) => <li key={i}>{p}</li>)}</ul>
                                  : '-'}
                              </td>
                            ))}
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Input Area 输入区域 */}
          {activeTab === 'chat' && (
            <div className="input-area">
              <textarea
                placeholder="请输入您的问题..."
                rows={3}
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                disabled={!currentSession || loading}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    sendQuery()
                  }
                }}
              />
              <div className="input-actions">
                <button
                  onClick={sendQuery}
                  disabled={!currentSession || loading || !query.trim()}
                >
                  {loading ? '发送中…' : '发送'}
                </button>
                <button
                  onClick={clearQuery}
                  disabled={!currentSession || loading || !query}
                >
                  清空
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default App
