/**
 * M1-QA 投研问答助手 — React SPA
 * 对齐 spec/06 功能规格说明
 */
import { useState, useEffect, useRef, useCallback } from 'react';
import {
  getCapabilities, getSessions, createSession, deleteSession,
  getRecords, askStream, searchRecords, findSimilar, getStockInfo,
} from './api';
import './App.css';

// ── 股票标签组件 ──
function StockTag({ name, code, onStockClick }) {
  return (
    <span className="stock-tag" onClick={() => onStockClick(code, name)} title={`查看 ${name}(${code})`}>
      {name}({code})
    </span>
  );
}

// ── 回答文本：内嵌股票标签渲染 ──
function AnswerText({ text, stocks, onStockClick }) {
  if (!stocks || stocks.length === 0) return <span className="answer-text">{text}</span>;
  // 替换股票名称/代码为可点击标签
  let parts = [text];
  stocks.forEach(({ name, code }) => {
    const newParts = [];
    parts.forEach((part) => {
      if (typeof part !== 'string') { newParts.push(part); return; }
      const pattern = `${name}(${code})`;
      const idx = part.indexOf(pattern);
      if (idx === -1) { newParts.push(part); return; }
      if (idx > 0) newParts.push(part.slice(0, idx));
      newParts.push(<StockTag key={`${code}-${idx}`} name={name} code={code} onStockClick={onStockClick} />);
      newParts.push(part.slice(idx + pattern.length));
    });
    parts = newParts;
  });
  return <span className="answer-text">{parts}</span>;
}

// ── 来源标签 ──
function SourceBadge({ source, llmUsed }) {
  const map = { copaw: 'CoPaw', bailian: '百炼', demo: '离线演示' };
  const cls = source === 'demo' ? 'badge-gray' : 'badge-blue';
  return <span className={`source-badge ${cls}`}>{map[source] || source}</span>;
}

// ── 相似提问弹窗 ──
function SimilarModal({ records, onViewHistory, onNewAsk, onClose }) {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h3>发现相似历史提问</h3>
        <div className="similar-list">
          {records.map((r, i) => (
            <div key={i} className="similar-item">
              <p className="similar-q">Q: {r.query}</p>
              <p className="similar-a">A: {r.answer?.slice(0, 100)}...</p>
              <small>相似度: {(r._similarity * 100).toFixed(0)}%</small>
            </div>
          ))}
        </div>
        <div className="modal-actions">
          <button className="btn-secondary" onClick={onViewHistory}>查看历史</button>
          <button className="btn-primary" onClick={onNewAsk}>发起新提问</button>
        </div>
      </div>
    </div>
  );
}

// ── 股票信息弹窗 ──
function StockModal({ stockInfo, onClose }) {
  if (!stockInfo) return null;
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal stock-modal" onClick={(e) => e.stopPropagation()}>
        <h3>{stockInfo.name}（{stockInfo.code}）</h3>
        <p>{stockInfo.summary}</p>
        {stockInfo.latest_reports?.map((r, i) => (
          <div key={i} className="stock-report">
            <span>{r.title}</span>
            <small>{r.broker} · {r.date}</small>
          </div>
        ))}
        <button className="btn-secondary" onClick={onClose}>关闭</button>
      </div>
    </div>
  );
}

export default function App() {
  // ── 状态 ── 对齐 spec/06 §7
  const [caps, setCaps] = useState({});
  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [records, setRecords] = useState([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [streamingAnswer, setStreamingAnswer] = useState('');
  const [searchKeyword, setSearchKeyword] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [similarRecords, setSimilarRecords] = useState(null);
  const [stockInfo, setStockInfo] = useState(null);
  const [openStockCodes, setOpenStockCodes] = useState(new Set()); // US-004 AC-004-02
  const messagesEndRef = useRef(null);

  // ── 初始化：加载能力 + 会话列表 ──
  useEffect(() => {
    getCapabilities().then(setCaps).catch(() => {});
    loadSessions();
  }, []);

  // ── 自动滚动到底部 ──
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [records, streamingAnswer]);

  const loadSessions = async () => {
    try {
      const list = await getSessions();
      setSessions(list);
    } catch (e) { setError(e.message); }
  };

  const loadRecords = async (sessionId) => {
    try {
      const list = await getRecords(sessionId);
      setRecords(list);
    } catch (e) { setError(e.message); }
  };

  // ── 会话操作 ──
  const handleNewSession = async () => {
    try {
      const s = await createSession();
      setSessions((prev) => [s, ...prev]);
      setCurrentSession(s);
      setRecords([]);
      setSearchResults(null);
    } catch (e) { setError(e.message); }
  };

  const handleDeleteSession = async (sid, e) => {
    e.stopPropagation();
    if (!confirm('确定删除此会话？删除后不可恢复。')) return;
    try {
      await deleteSession(sid);
      setSessions((prev) => prev.filter((s) => s.session_id !== sid));
      if (currentSession?.session_id === sid) {
        setCurrentSession(null);
        setRecords([]);
      }
    } catch (e) { setError(e.message); }
  };

  const handleSelectSession = (s) => {
    setCurrentSession(s);
    setSearchResults(null);
    loadRecords(s.session_id);
  };

  // ── 发送问答（SSE 流式）── 对齐 spec/06 §4.1
  const handleSend = useCallback(async (forceNew = false) => {
    if (!query.trim() || !currentSession || loading) return;
    const q = query.trim();
    setQuery('');
    setError(null);

    // 相似性检测（对齐 US-003 AC-003-02）
    if (!forceNew) {
      try {
        const sim = await findSimilar(q);
        if (sim.has_similar && sim.similar_records.length > 0) {
          setSimilarRecords({ query: q, records: sim.similar_records });
          return;
        }
      } catch { /* 忽略，继续发送 */ }
    }

    doSend(q);
  }, [query, currentSession, loading]);

  const doSend = (q) => {
    setLoading(true);
    setStreamingAnswer('');
    // 添加临时问题卡片
    setRecords((prev) => [...prev, { query: q, answer: null, _pending: true }]);

    askStream(q, currentSession.session_id, {
      onChunk: (text) => setStreamingAnswer((prev) => prev + text),
      onDone: (data) => {
        setStreamingAnswer('');
        setLoading(false);
        // 替换临时卡片为完整记录
        setRecords((prev) => {
          const copy = [...prev];
          const idx = copy.findIndex((r) => r._pending);
          if (idx >= 0) copy[idx] = { ...data, query: q };
          return copy;
        });
        // 刷新会话列表（标题可能更新）
        loadSessions();
      },
      onError: (msg) => {
        setLoading(false);
        setStreamingAnswer('');
        setError(msg);
        setRecords((prev) => prev.filter((r) => !r._pending));
      },
    });
  };

  // ── 搜索 ── 对齐 spec/06 §4.4
  const handleSearch = async () => {
    if (!searchKeyword.trim()) return;
    try {
      const results = await searchRecords(searchKeyword.trim());
      setSearchResults(results);
    } catch (e) { setError(e.message); }
  };

  // ── 股票点击 ── 对齐 spec/06 §4.3, US-004 AC-004-02
  const handleStockClick = async (code, name) => {
    // 复用已打开的窗口（AC-004-02）
    if (openStockCodes.has(code)) {
      try {
        const info = await getStockInfo(code);
        setStockInfo(info);
      } catch (e) { setError(e.message); }
      return;
    }
    try {
      const info = await getStockInfo(code);
      setStockInfo(info);
      setOpenStockCodes((prev) => new Set(prev).add(code));
    } catch (e) { setError(e.message); }
  };

  // ── 能力芯片 ──
  const renderCapChips = () => {
    if (caps.copaw_configured) return <span className="cap-chip cap-active">CoPaw 桥接</span>;
    if (caps.bailian_configured) return <span className="cap-chip cap-active">百炼</span>;
    return <span className="cap-chip cap-demo">离线演示</span>;
  };

  // ── 渲染 ──
  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <h1>投研问答助手</h1>
        <div className="header-chips">{renderCapChips()}</div>
      </header>

      <div className="main-layout">
        {/* Sidebar */}
        <aside className="sidebar">
          <button className="btn-new-session" onClick={handleNewSession}>+ 新建会话</button>
          <div className="search-box">
            <input
              type="text" placeholder="搜索历史记录…" value={searchKeyword}
              onChange={(e) => setSearchKeyword(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            />
            <button onClick={handleSearch} className="btn-search">🔍</button>
          </div>
          <div className="session-list">
            {sessions.map((s) => (
              <div
                key={s.session_id}
                className={`session-item ${currentSession?.session_id === s.session_id ? 'active' : ''}`}
                onClick={() => handleSelectSession(s)}
              >
                <span className="session-title">{s.title}</span>
                <span className="session-count">{s.query_count}条</span>
                <button className="btn-delete" onClick={(e) => handleDeleteSession(s.session_id, e)}>×</button>
              </div>
            ))}
          </div>
        </aside>

        {/* Main Content */}
        <main className="content">
          {error && <div className="error-bar" onClick={() => setError(null)}>{error} ×</div>}

          {/* 搜索结果视图 */}
          {searchResults && (
            <div className="search-results">
              <div className="search-header">
                <h3>搜索结果："{searchKeyword}" ({searchResults.length}条)</h3>
                <button className="btn-secondary" onClick={() => setSearchResults(null)}>返回</button>
              </div>
              {searchResults.map((r, i) => (
                <div key={i} className="record-card search-result-card">
                  <div className="record-q">Q: {r.query}</div>
                  <div className="record-a">A: {r.answer?.slice(0, 200)}</div>
                  <small>{r.timestamp}</small>
                </div>
              ))}
            </div>
          )}

          {/* 对话区 */}
          {!searchResults && (
            <>
              <div className="messages">
                {!currentSession && (
                  <div className="empty-state">
                    <h2>请创建或选择一个会话开始</h2>
                    <p>点击左侧"+ 新建会话"开始对话</p>
                  </div>
                )}
                {currentSession && records.length === 0 && !loading && (
                  <div className="empty-state">
                    <h2>新会话</h2>
                    <p>请输入研报相关问题，如：某公司的最新评级和目标价</p>
                  </div>
                )}
                {records.map((r, i) => (
                  <div key={i} className="record-card">
                    <div className="record-q">
                      <span className="label">Q</span> {r.query}
                    </div>
                    {r._pending ? (
                      <div className="record-a streaming">
                        <span className="label">A</span>
                        {streamingAnswer ? (
                          <span>{streamingAnswer}<span className="cursor">▌</span></span>
                        ) : (
                          <span className="typing">回答中…</span>
                        )}
                      </div>
                    ) : r.answer ? (
                      <div className="record-a">
                        <span className="label">A</span>
                        <AnswerText text={r.answer} stocks={r.stocks} onStockClick={handleStockClick} />
                        <div className="record-meta">
                          <SourceBadge source={r.answer_source} llmUsed={r.llm_used} />
                          {r.response_time_ms != null && <small>{r.response_time_ms}ms</small>}
                        </div>
                      </div>
                    ) : null}
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>

              {/* 输入区 */}
              {currentSession && (
                <div className="input-area">
                  <textarea
                    rows={3} value={query} placeholder="请输入您的问题..."
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); } }}
                    disabled={loading}
                  />
                  <div className="input-actions">
                    <button className="btn-primary" onClick={() => handleSend()} disabled={loading || !query.trim()}>
                      {loading ? '发送中…' : '发送'}
                    </button>
                    <button className="btn-secondary" onClick={() => setQuery('')} disabled={loading}>清空</button>
                  </div>
                </div>
              )}
            </>
          )}
        </main>
      </div>

      {/* 相似提问弹窗 */}
      {similarRecords && (
        <SimilarModal
          records={similarRecords.records}
          onViewHistory={() => { setSimilarRecords(null); }}
          onNewAsk={() => { const q = similarRecords.query; setSimilarRecords(null); setQuery(q); setTimeout(() => doSend(q), 0); }}
          onClose={() => setSimilarRecords(null)}
        />
      )}

      {/* 股票信息弹窗 */}
      {stockInfo && <StockModal stockInfo={stockInfo} onClose={() => setStockInfo(null)} />}
    </div>
  );
}
