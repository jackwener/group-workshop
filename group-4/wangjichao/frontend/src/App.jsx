import { useState, useEffect } from 'react'
import Header from './components/Header'
import Sidebar from './components/Sidebar'
import ChatArea from './components/ChatArea'
import InputArea from './components/InputArea'
import ReportList from './components/ReportList'
import ReportDetail from './components/ReportDetail'
import CompareTab from './components/CompareTab'

function App() {
  // ========= 9 个 State 变量 =========
  const [sessions, setSessions] = useState([])
  const [currentSession, setCurrentSession] = useState(null)
  const [reports, setReports] = useState([])
  const [currentReport, setCurrentReport] = useState(null)
  const [qaRecords, setQaRecords] = useState([])
  const [activeTab, setActiveTab] = useState('session')
  const [isLoading, setIsLoading] = useState(false)
  const [inputValue, setInputValue] = useState('')
  const [capabilities, setCapabilities] = useState({})

  // 页面加载
  useEffect(() => {
    fetch('/api/v1/agent/capabilities')
      .then(res => res.json())
      .then(data => { if (data.success) setCapabilities(data.data) })
      .catch(err => console.error('Failed to fetch capabilities:', err))
    
    loadSessions()
  }, [])

  // ========= 会话操作 =========
  const loadSessions = () => {
    fetch('/api/v1/agent/sessions')
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          setSessions(data.data.sessions)
        }
      })
      .catch(err => console.error('Failed to load sessions:', err))
  }

  const handleNewSession = () => {
    fetch('/api/v1/agent/sessions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({})
    })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          setSessions(prev => [data.data, ...prev])
          setCurrentSession(data.data)
          setQaRecords([])
        }
      })
      .catch(err => console.error('Failed to create session:', err))
  }

  const handleSelectSession = (session) => {
    setCurrentSession(session)
    fetch(`/api/v1/agent/sessions/${session.session_id}/records`)
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          setQaRecords(data.data.records)
        }
      })
      .catch(err => console.error('Failed to load records:', err))
  }

  const handleDeleteSession = (sessionId) => {
    fetch(`/api/v1/agent/sessions/${sessionId}`, { method: 'DELETE' })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          setSessions(prev => prev.filter(s => s.session_id !== sessionId))
          if (currentSession?.session_id === sessionId) {
            setCurrentSession(null)
            setQaRecords([])
          }
        }
      })
      .catch(err => console.error('Failed to delete session:', err))
  }

  const handleRenameSession = (sessionId, newTitle) => {
    fetch(`/api/v1/agent/sessions/${sessionId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: newTitle })
    })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          setSessions(prev => prev.map(s =>
            s.session_id === sessionId ? { ...s, title: newTitle } : s
          ))
          if (currentSession?.session_id === sessionId) {
            setCurrentSession(prev => ({ ...prev, title: newTitle }))
          }
        }
      })
      .catch(err => console.error('Failed to rename session:', err))
  }

  // ========= 问答操作 =========
  const handleSend = (query) => {
    if (!currentSession || isLoading) return
    setIsLoading(true)
    setInputValue('')

    fetch('/api/v1/agent/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, session_id: currentSession.session_id })
    })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          const newRecord = {
            id: `rec_${Date.now()}`,
            query,
            answer: data.data.answer,
            llm_used: data.data.llm_used,
            model: data.data.model,
            response_time_ms: data.data.response_time_ms,
            answer_source: data.data.answer_source,
            timestamp: new Date().toISOString()
          }
          setQaRecords(prev => [...prev, newRecord])
          // 更新会话列表中的 query_count
          setSessions(prev => prev.map(s =>
            s.session_id === currentSession.session_id
              ? { ...s, query_count: (s.query_count || 0) + 1 }
              : s
          ))
        } else if (data.error) {
          const code = data.error.code
          let msg = data.error.message
          if (code === 'EMPTY_QUERY') msg = '请输入问题'
          else if (code === 'INVALID_QUERY') msg = '问题过长，请限制在500字符以内'
          else if (code === 'LLM_UNAVAILABLE') msg = 'AI服务暂不可用，已切换离线模式'
          alert(msg)
        }
      })
      .catch(err => {
        console.error('Failed to send question:', err)
        alert('发送失败，请重试')
      })
      .finally(() => setIsLoading(false))
  }

  const handleQuickQuestion = (question) => {
    setInputValue(question)
  }

  // ========= 研报操作 =========
  const loadReports = () => {
    fetch('/api/v1/agent/reports')
      .then(res => res.json())
      .then(data => {
        if (data.success) setReports(data.data.items || [])
      })
      .catch(err => console.error('Failed to load reports:', err))
  }

  useEffect(() => {
    if (activeTab === 'report' || activeTab === 'compare') {
      loadReports()
    }
  }, [activeTab])

  return (
    <div className="h-screen flex flex-col bg-slate-50">
      <Header capabilities={capabilities} />

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <Sidebar
          sessions={sessions}
          currentSession={currentSession}
          onSelectSession={handleSelectSession}
          onNewSession={handleNewSession}
          onDeleteSession={handleDeleteSession}
          onRenameSession={handleRenameSession}
        />

        {/* Main Content */}
        <main className="flex-1 flex flex-col overflow-hidden">
          {/* Tab Navigation */}
          <div className="border-b border-slate-200 bg-white px-6">
            <nav className="flex space-x-6">
              {[
                { key: 'session', label: '会话' },
                { key: 'report', label: '研报' },
                { key: 'compare', label: '对比' }
              ].map(tab => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key)}
                  className={`py-3 px-1 border-b-2 text-sm font-medium transition-colors ${
                    activeTab === tab.key
                      ? 'border-brand-500 text-brand-600'
                      : 'border-transparent text-slate-400 hover:text-slate-600 hover:border-slate-300'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          {/* Tab Content */}
          {activeTab === 'session' && (
            <div className="flex-1 flex flex-col overflow-hidden">
              <ChatArea
                currentSession={currentSession}
                qaRecords={qaRecords}
                isLoading={isLoading}
                onQuickQuestion={handleQuickQuestion}
              />
              {currentSession && (
                <InputArea
                  inputValue={inputValue}
                  setInputValue={setInputValue}
                  onSend={handleSend}
                  isLoading={isLoading}
                />
              )}
            </div>
          )}

          {activeTab === 'report' && (
            <ReportList
              reports={reports}
              currentReport={currentReport}
              setCurrentReport={setCurrentReport}
              setReports={setReports}
              loadReports={loadReports}
            />
          )}

          {activeTab === 'compare' && (
            <CompareTab reports={reports} loadReports={loadReports} />
          )}
        </main>
      </div>
    </div>
  )
}

export default App
