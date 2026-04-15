import { useState, useEffect, useRef } from 'react'
import {
  getSessions, createSession, deleteSession,
  askQuestion, getRecords, getCapabilities,
} from './api'

// ========== Toast Component (T-034) ==========

const ERROR_MAP = {
  EMPTY_QUERY: { text: '请输入问题', action: 'focus' },
  INVALID_QUERY: { text: '问题过长，请控制在 500 字符以内', action: 'count' },
  MISSING_SESSION_ID: { text: '请先选择或创建一个会话', action: 'sidebar' },
  SESSION_NOT_FOUND: { text: '会话不存在，请重新选择', action: 'refresh' },
  INVALID_SESSION_TITLE: { text: '会话标题过长', action: null },
  INVALID_SEARCH_PARAM: { text: '搜索条件无效', action: null },
  UPSTREAM_ERROR: { text: '服务器内部错误', action: 'log' },
  NETWORK_ERROR: { text: '网络连接失败', action: 'banner' },
  TIMEOUT_ERROR: { text: '请求超时', action: null },
  RATE_LIMIT: { text: '请求过于频繁', action: null },
}

function Toast({ toast, onClose }) {
  useEffect(() => {
    if (!toast) return
    const t = setTimeout(onClose, 3000)
    return () => clearTimeout(t)
  }, [toast, onClose])
  if (!toast) return null
  return (
    <div className="toast">{toast}</div>
  )
}

// ========== Source Tag (T-029) ==========

function SourceTag({ source }) {
  const colors = { copaw: '#22c55e', bailian: '#3b82f6', demo: '#9ca3af' }
  const labels = { copaw: 'CoPaw', bailian: '百炼', demo: '演示' }
  return (
    <span className="source-tag" style={{ background: colors[source] || '#9ca3af' }}>
      {labels[source] || source}
    </span>
  )
}

// ========== Hot Questions (T-028) ==========

const HOT_QUESTIONS = [
  '最近一周热门研报有哪些？',
  '某公司的最新评级和目标价是多少？',
  '对比两家公司的研报分析',
  '查看某行业的最新动态',
  '某股票的近期研报摘要',
  '研报中的关键财务指标解读',
]

// ========== Demo Research Reports (T-031) ==========

const DEMO_REPORTS = [
  { id: 1, title: '贵州茅台2026Q1业绩点评', company: '贵州茅台', rating: '买入', targetPrice: 2100, keyPoint: '业绩超预期，白酒行业龙头地位稳固' },
  { id: 2, title: '宁德时代新能源产业链分析', company: '宁德时代', rating: '强烈推荐', targetPrice: 280, keyPoint: '全球动力电池市场份额持续扩大' },
  { id: 3, title: '比亚迪新能源汽车销量跟踪', company: '比亚迪', rating: '买入', targetPrice: 350, keyPoint: '新能源汽车销量持续高增长' },
  { id: 4, title: '招商银行零售转型深度分析', company: '招商银行', rating: '增持', targetPrice: 45, keyPoint: '零售业务护城河深厚' },
  { id: 5, title: '贵州茅台产能扩张分析', company: '贵州茅台', rating: '增持', targetPrice: 1950, keyPoint: '产能扩张将支撑长期增长' },
  { id: 6, title: '腾讯控股AI业务布局研究', company: '腾讯控股', rating: '买入', targetPrice: 480, keyPoint: 'AI大模型落地加速商业化进程' },
  { id: 7, title: '中芯国际半导体产业链分析', company: '中芯国际', rating: '增持', targetPrice: 68, keyPoint: '国产替代持续推进' },
  { id: 8, title: '隆基绿能光伏行业展望', company: '隆基绿能', rating: '中性', targetPrice: 25, keyPoint: '行业竞争加剧但龙头优势明显' },
  { id: 9, title: '比亚迪海外市场拓展报告', company: '比亚迪', rating: '强烈推荐', targetPrice: 380, keyPoint: '海外市场成为新增长极' },
  { id: 10, title: '药明康德CXO行业趋势', company: '药明康德', rating: '买入', targetPrice: 75, keyPoint: '全球CXO需求回暖' },
]

// ========== Demo News (T-032) ==========

const DEMO_NEWS = [
  { id: 1, title: 'A股三大指数集体收涨 半导体板块领涨', keywords: ['A股', '半导体'], summary: '今日A股市场表现强劲，三大指数集体收涨。半导体板块表现亮眼，多只个股涨停。', time: '2026-04-14 10:30' },
  { id: 2, title: '央行公布最新LPR利率保持不变', keywords: ['央行', 'LPR', '利率'], summary: '中国人民银行公布最新贷款市场报价利率（LPR），一年期和五年期均保持不变。', time: '2026-04-14 09:15' },
  { id: 3, title: '新能源汽车一季度销量数据出炉', keywords: ['新能源', '汽车', '销量'], summary: '2026年第一季度新能源汽车销量达到320万辆，同比增长35%，渗透率再创新高。', time: '2026-04-13 16:00' },
  { id: 4, title: '多家券商上调贵州茅台目标价', keywords: ['茅台', '券商', '目标价'], summary: '近日多家头部券商发布研报，上调贵州茅台目标价至2000元以上，看好长期发展。', time: '2026-04-13 14:20' },
  { id: 5, title: 'AI大模型行业迎来新一轮融资潮', keywords: ['AI', '大模型', '融资'], summary: '国内多家AI创业公司获得新一轮融资，大模型应用落地加速推进。', time: '2026-04-13 11:45' },
  { id: 6, title: '光伏行业产能过剩问题引发关注', keywords: ['光伏', '产能'], summary: '业内人士表示光伏行业产能过剩问题短期难以缓解，企业盈利能力承压。', time: '2026-04-12 15:30' },
  { id: 7, title: '港股恒生指数连续三日上涨', keywords: ['港股', '恒生指数'], summary: '港股恒生指数今日收涨1.2%，连续三个交易日上涨，科技股表现强势。', time: '2026-04-12 16:10' },
  { id: 8, title: '医药板块迎来政策利好', keywords: ['医药', '政策'], summary: '国家医保局发布新政策，创新药支付标准迎来重大调整，利好创新药企。', time: '2026-04-12 10:00' },
  { id: 9, title: '人民币汇率走势平稳', keywords: ['人民币', '汇率'], summary: '近期人民币兑美元汇率保持平稳，央行通过多种工具维护汇率稳定。', time: '2026-04-11 14:00' },
  { id: 10, title: '芯片国产替代加速推进', keywords: ['芯片', '国产替代'], summary: '多家国内芯片企业在先进制程方面取得突破，国产替代进程加速。', time: '2026-04-11 09:30' },
]

const HOT_KEYWORDS = ['A股', '新能源', 'AI', '半导体', '茅台', '医药']

// ========== Main App ==========

function App() {
  // S1: Session states (T-013)
  const [sessions, setSessions] = useState([])
  const [currentSession, setCurrentSession] = useState(null)
  const [sessionsLoading, setSessionsLoading] = useState(false)
  const [deleteConfirmId, setDeleteConfirmId] = useState(null)

  // S2: QA states (T-027)
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [records, setRecords] = useState([])
  const [error, setError] = useState(null)

  // S3: Capabilities (T-030)
  const [capabilities, setCapabilities] = useState(null)

  // S3: Research reports (T-031)
  const [searchParams, setSearchParams] = useState(null)
  const [reportRating, setReportRating] = useState('')
  const [reportCompany, setReportCompany] = useState('')
  const [reportPriceMin, setReportPriceMin] = useState('')
  const [reportPriceMax, setReportPriceMax] = useState('')

  // S3: News (T-032)
  const [newsKeyword, setNewsKeyword] = useState('')

  // S3: Selected session interaction (T-033)
  const [recordsLoading, setRecordsLoading] = useState(false)

  // UI states
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)
  const [toast, setToast] = useState(null)
  const [activeTab, setActiveTab] = useState('chat') // chat | reports | news

  const chatEndRef = useRef(null)
  const inputRef = useRef(null)

  // ========== Load initial data ==========

  useEffect(() => {
    loadSessions()
    loadCapabilities()
  }, [])

  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [records])

  const loadSessions = async () => {
    setSessionsLoading(true)
    try {
      const data = await getSessions()
      setSessions(data.sessions || [])
    } catch {
      showToast('网络连接失败')
    } finally {
      setSessionsLoading(false)
    }
  }

  const loadCapabilities = async () => {
    try {
      const data = await getCapabilities()
      setCapabilities(data)
    } catch {
      // silent
    }
  }

  // ========== Toast helper ==========

  const showToast = (msg) => setToast(msg)

  const handleApiError = (data) => {
    if (data?.error) {
      const code = data.error.code
      const mapped = ERROR_MAP[code]
      if (mapped) {
        showToast(mapped.text)
        if (mapped.action === 'focus' && inputRef.current) inputRef.current.focus()
        if (mapped.action === 'refresh') loadSessions()
        if (mapped.action === 'sidebar') setIsSidebarOpen(true)
        if (mapped.action === 'log') console.log('traceId:', data.error.traceId)
        return true
      }
      showToast(data.error.message || '未知错误')
      return true
    }
    return false
  }

  // ========== Session actions (T-013) ==========

  const handleCreateSession = async () => {
    try {
      const data = await createSession('新会话')
      if (handleApiError(data)) return
      const newSession = {
        session_id: data.session_id,
        title: data.title,
        created_at: data.created_at,
        query_count: data.query_count,
      }
      setSessions(prev => [newSession, ...prev])
      setCurrentSession(newSession)
      setRecords([])
      setActiveTab('chat')
    } catch {
      showToast('网络连接失败')
    }
  }

  const handleDeleteSession = async (id) => {
    try {
      const data = await deleteSession(id)
      if (handleApiError(data)) return
      setSessions(prev => prev.filter(s => s.session_id !== id))
      if (currentSession?.session_id === id) {
        setCurrentSession(null)
        setRecords([])
      }
      setDeleteConfirmId(null)
    } catch {
      showToast('网络连接失败')
    }
  }

  // ========== Select session - 8 step interaction (T-033) ==========

  const handleSelectSession = async (session) => {
    // Step 1-2: Highlight + set current
    setCurrentSession(session)
    setActiveTab('chat')
    // Step 3: Loading
    setRecordsLoading(true)
    try {
      // Step 4: Fetch records
      const data = await getRecords(session.session_id)
      if (handleApiError(data)) {
        setRecordsLoading(false)
        return
      }
      // Step 5: Write records
      setRecords(data.records || [])
    } catch {
      // Step 8: Error - keep previous content
      showToast('加载记录失败')
    } finally {
      setRecordsLoading(false)
    }
    // Steps 6-7: B/C state handled in render
  }

  // ========== Ask question (T-027) ==========

  const handleAsk = async (q) => {
    const questionText = q || query
    if (!questionText.trim()) {
      showToast('请输入问题')
      if (inputRef.current) inputRef.current.focus()
      return
    }
    if (!currentSession) {
      showToast('请先选择或创建一个会话')
      setIsSidebarOpen(true)
      return
    }
    setLoading(true)
    setError(null)
    try {
      const data = await askQuestion(questionText.trim(), currentSession.session_id)
      if (handleApiError(data)) {
        setLoading(false)
        return
      }
      // Refresh records
      const recData = await getRecords(currentSession.session_id)
      setRecords(recData.records || [])
      setQuery('')
      // Update session in list
      setSessions(prev => prev.map(s =>
        s.session_id === currentSession.session_id
          ? { ...s, query_count: (s.query_count || 0) + 1, title: s.query_count === 0 ? questionText.trim().slice(0, 20) + '...' : s.title }
          : s
      ))
    } catch {
      showToast('网络连接失败')
    } finally {
      setLoading(false)
    }
  }

  // ========== Research Reports filtering (T-031) ==========

  const getFilteredReports = () => {
    let filtered = [...DEMO_REPORTS]
    if (reportRating) filtered = filtered.filter(r => r.rating === reportRating)
    if (reportCompany) filtered = filtered.filter(r => r.company.includes(reportCompany))
    if (reportPriceMin) filtered = filtered.filter(r => r.targetPrice >= Number(reportPriceMin))
    if (reportPriceMax) filtered = filtered.filter(r => r.targetPrice <= Number(reportPriceMax))
    return filtered.slice(0, 10)
  }

  const getComparisonReports = () => {
    const filtered = getFilteredReports()
    const companies = {}
    filtered.forEach(r => {
      if (!companies[r.company]) companies[r.company] = []
      companies[r.company].push(r)
    })
    return Object.entries(companies).filter(([, reports]) => reports.length > 1)
  }

  // ========== News filtering (T-032) ==========

  const getFilteredNews = () => {
    if (!newsKeyword.trim()) return DEMO_NEWS.slice(0, 10)
    return DEMO_NEWS.filter(n =>
      n.keywords.some(k => k.includes(newsKeyword)) ||
      n.title.includes(newsKeyword) ||
      n.summary.includes(newsKeyword)
    ).slice(0, 10)
  }

  // ========== Format time ==========

  const formatTime = (ts) => {
    if (!ts) return ''
    const d = new Date(ts)
    const now = new Date()
    if (d.toDateString() === now.toDateString()) {
      return d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
    }
    return `${(d.getMonth() + 1).toString().padStart(2, '0')}-${d.getDate().toString().padStart(2, '0')} ${d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}`
  }

  // ========== Render ==========

  return (
    <div className="app">
      {/* Header (T-030) */}
      <header className="header">
        <button className="sidebar-toggle" onClick={() => setIsSidebarOpen(!isSidebarOpen)}>
          {isSidebarOpen ? '<<' : '>>'}
        </button>
        <h1 className="header-title">投研问答助手</h1>
        <div className="capability-chips">
          {capabilities?.copaw_configured && (
            <span className="chip chip-green">CoPaw 桥接</span>
          )}
          {capabilities?.bailian_configured ? (
            <span className="chip chip-blue">百炼 · {capabilities.model}</span>
          ) : (
            <span className="chip chip-gray">离线演示</span>
          )}
        </div>
      </header>

      <div className="body">
        {/* Sidebar (T-013) */}
        {isSidebarOpen && (
          <aside className="sidebar">
            <button className="btn btn-primary sidebar-new" onClick={handleCreateSession}>
              + 新建会话
            </button>
            {sessionsLoading ? (
              <div className="skeleton-list">
                {[1, 2, 3].map(i => <div key={i} className="skeleton-item" />)}
              </div>
            ) : (
              <ul className="session-list">
                {sessions.map(s => (
                  <li
                    key={s.session_id}
                    className={`session-item ${currentSession?.session_id === s.session_id ? 'active' : ''}`}
                    onClick={() => handleSelectSession(s)}
                  >
                    <div className="session-info">
                      <span className="session-title">{s.title}</span>
                      <span className="session-count">{s.query_count} 条问答</span>
                    </div>
                    <button
                      className="btn-delete"
                      onClick={(e) => { e.stopPropagation(); setDeleteConfirmId(s.session_id) }}
                      title="删除会话"
                    >x</button>
                  </li>
                ))}
              </ul>
            )}
            {/* Delete confirm dialog */}
            {deleteConfirmId && (
              <div className="modal-overlay" onClick={() => setDeleteConfirmId(null)}>
                <div className="modal" onClick={e => e.stopPropagation()}>
                  <p>确定要删除此会话吗？相关的问答记录也将被删除。</p>
                  <div className="modal-actions">
                    <button className="btn" onClick={() => setDeleteConfirmId(null)}>取消</button>
                    <button className="btn btn-danger" onClick={() => handleDeleteSession(deleteConfirmId)}>删除</button>
                  </div>
                </div>
              </div>
            )}
          </aside>
        )}

        {/* Main Area */}
        <main className="main">
          {/* Tab bar for switching views */}
          {currentSession && (
            <div className="tab-bar">
              <button className={`tab ${activeTab === 'chat' ? 'active' : ''}`} onClick={() => setActiveTab('chat')}>问答</button>
              <button className={`tab ${activeTab === 'reports' ? 'active' : ''}`} onClick={() => setActiveTab('reports')}>研报搜索</button>
              <button className={`tab ${activeTab === 'news' ? 'active' : ''}`} onClick={() => setActiveTab('news')}>新闻推送</button>
            </div>
          )}

          {/* A State: No session selected (T-013 step 5) */}
          {!currentSession && (
            <div className="empty-state">
              <div className="empty-icon">💬</div>
              <p>请创建或选择一个会话开始</p>
            </div>
          )}

          {/* Chat tab */}
          {currentSession && activeTab === 'chat' && (
            <div className="chat-container">
              {/* Loading skeleton (T-033) */}
              {recordsLoading ? (
                <div className="skeleton-list">
                  {[1, 2, 3].map(i => (
                    <div key={i} className="skeleton-bubble" />
                  ))}
                </div>
              ) : records.length === 0 ? (
                /* B State: Hot questions grid (T-028) */
                <div className="hot-questions">
                  <h3>试试问我这些问题</h3>
                  <div className="question-grid">
                    {HOT_QUESTIONS.map((q, i) => (
                      <div
                        key={i}
                        className="question-card"
                        onClick={() => handleAsk(q)}
                      >
                        {q}
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                /* C State: Chat history (T-029) */
                <div className="chat-history">
                  {records.map((r) => (
                    <div key={r.record_id} className="chat-pair">
                      {/* User question - right */}
                      <div className="bubble bubble-user">
                        <div className="bubble-content">{r.query}</div>
                        <div className="bubble-meta">{formatTime(r.timestamp)}</div>
                      </div>
                      {/* AI answer - left */}
                      <div className="bubble bubble-ai">
                        <div className="bubble-content">{r.answer}</div>
                        <div className="bubble-meta">
                          <SourceTag source={r.answer_source} />
                          {r.model && <span className="model-tag">{r.model}</span>}
                          <span className="response-time">{r.response_time_ms}ms</span>
                          <span>{formatTime(r.timestamp)}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                  <div ref={chatEndRef} />
                </div>
              )}

              {/* Input area (T-027) */}
              <div className="input-area">
                <textarea
                  ref={inputRef}
                  rows={3}
                  placeholder="请输入您的问题..."
                  value={query}
                  onChange={e => setQuery(e.target.value)}
                  onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleAsk() } }}
                  disabled={loading}
                />
                <div className="input-actions">
                  <span className="char-count">{query.length}/500</span>
                  <button className="btn" onClick={() => setQuery('')} disabled={loading || !query}>清空</button>
                  <button className="btn btn-primary" onClick={() => handleAsk()} disabled={loading || !query.trim()}>
                    {loading ? '发送中...' : '发送'}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* D State: Research Reports (T-031) */}
          {currentSession && activeTab === 'reports' && (
            <div className="reports-container">
              <div className="search-form">
                <h3>研报搜索</h3>
                <div className="search-fields">
                  <div className="field">
                    <label>评级</label>
                    <select value={reportRating} onChange={e => setReportRating(e.target.value)}>
                      <option value="">全部</option>
                      <option value="强烈推荐">强烈推荐</option>
                      <option value="买入">买入</option>
                      <option value="增持">增持</option>
                      <option value="中性">中性</option>
                      <option value="减持">减持</option>
                    </select>
                  </div>
                  <div className="field">
                    <label>公司名称</label>
                    <input type="text" placeholder="输入公司名" value={reportCompany} onChange={e => setReportCompany(e.target.value)} />
                  </div>
                  <div className="field">
                    <label>目标价范围</label>
                    <div className="price-range">
                      <input type="number" placeholder="最低" value={reportPriceMin} onChange={e => setReportPriceMin(e.target.value)} />
                      <span>-</span>
                      <input type="number" placeholder="最高" value={reportPriceMax} onChange={e => setReportPriceMax(e.target.value)} />
                    </div>
                  </div>
                </div>
              </div>

              {/* Report list */}
              <div className="report-list">
                {getFilteredReports().map(r => (
                  <div key={r.id} className="report-card">
                    <div className="report-header">
                      <span className="report-title">{r.title}</span>
                      <span className={`rating-tag rating-${r.rating === '强烈推荐' || r.rating === '买入' ? 'buy' : r.rating === '增持' ? 'hold' : 'neutral'}`}>
                        {r.rating}
                      </span>
                    </div>
                    <div className="report-info">
                      <span>公司: {r.company}</span>
                      <span>目标价: ¥{r.targetPrice}</span>
                    </div>
                    <p className="report-point">{r.keyPoint}</p>
                  </div>
                ))}
                {getFilteredReports().length === 0 && (
                  <div className="empty-state"><p>暂无匹配的研报</p></div>
                )}
              </div>

              {/* Comparison view */}
              {getComparisonReports().length > 0 && (
                <div className="comparison-section">
                  <h3>研报比对</h3>
                  {getComparisonReports().map(([company, reports]) => (
                    <div key={company} className="comparison-table-wrap">
                      <h4>{company}</h4>
                      <table className="comparison-table">
                        <thead>
                          <tr>
                            <th>研报标题</th>
                            <th>评级</th>
                            <th>目标价</th>
                            <th>核心观点</th>
                          </tr>
                        </thead>
                        <tbody>
                          {reports.map(r => (
                            <tr key={r.id}>
                              <td>{r.title}</td>
                              <td>{r.rating}</td>
                              <td>¥{r.targetPrice}</td>
                              <td>{r.keyPoint}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* E State: News (T-032) */}
          {currentSession && activeTab === 'news' && (
            <div className="news-container">
              <h3>新闻推送</h3>
              <div className="news-keywords">
                {HOT_KEYWORDS.map(kw => (
                  <span
                    key={kw}
                    className={`keyword-tag ${newsKeyword === kw ? 'active' : ''}`}
                    onClick={() => setNewsKeyword(newsKeyword === kw ? '' : kw)}
                  >
                    {kw}
                  </span>
                ))}
              </div>
              <div className="news-search">
                <input
                  type="text"
                  placeholder="输入关键词搜索..."
                  value={newsKeyword}
                  onChange={e => setNewsKeyword(e.target.value)}
                />
              </div>
              <div className="news-list">
                {getFilteredNews().map(n => (
                  <details key={n.id} className="news-card">
                    <summary>
                      <span className="news-title">{n.title}</span>
                      <span className="news-time">{n.time}</span>
                    </summary>
                    <div className="news-detail">
                      <div className="news-tags">
                        {n.keywords.map(k => <span key={k} className="keyword-tag small">{k}</span>)}
                      </div>
                      <p>{n.summary}</p>
                    </div>
                  </details>
                ))}
                {getFilteredNews().length === 0 && (
                  <div className="empty-state"><p>暂无匹配的新闻</p></div>
                )}
              </div>
            </div>
          )}
        </main>
      </div>

      {/* Toast (T-034) */}
      <Toast toast={toast} onClose={() => setToast(null)} />
    </div>
  )
}

export default App
