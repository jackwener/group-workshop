import { useState, useEffect } from 'react'
import Header from './components/Header'
import Sidebar from './components/Sidebar'
import MainContent from './components/MainContent'
import './App.css'

const API_BASE = '/api/v1'

function App() {
  const [sessions, setSessions] = useState([])
  const [currentSession, setCurrentSession] = useState(null)
  const [caps, setCaps] = useState({})
  const [loading, setLoading] = useState(false)

  // 获取系统能力状态
  useEffect(() => {
    fetch(`${API_BASE}/capabilities`)
      .then(res => res.json())
      .then(data => setCaps(data))
      .catch(console.error)
  }, [])

  // 获取会话列表
  useEffect(() => {
    fetchSessions()
  }, [])

  const fetchSessions = async () => {
    try {
      const res = await fetch(`${API_BASE}/sessions`)
      const data = await res.json()
      setSessions(data.sessions || [])
      // 默认选中第一个
      if (data.sessions?.length > 0 && !currentSession) {
        setCurrentSession(data.sessions[0])
      }
    } catch (err) {
      console.error('获取会话列表失败:', err)
    }
  }

  // 创建新会话
  const createSession = async () => {
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/sessions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: '新会话' })
      })
      const data = await res.json()
      if (data.session_id) {
        await fetchSessions()
        setCurrentSession(data)
      }
    } catch (err) {
      console.error('创建会话失败:', err)
    } finally {
      setLoading(false)
    }
  }

  // 删除会话
  const deleteSession = async (sessionId) => {
    if (!confirm('确定要删除这个会话吗？')) return
    
    try {
      await fetch(`${API_BASE}/sessions/${sessionId}`, {
        method: 'DELETE'
      })
      await fetchSessions()
      if (currentSession?.session_id === sessionId) {
        setCurrentSession(null)
      }
    } catch (err) {
      console.error('删除会话失败:', err)
    }
  }

  return (
    <div className="app">
      <Header caps={caps} />
      <div className="main-container">
        <Sidebar
          sessions={sessions}
          currentSession={currentSession}
          onSelectSession={setCurrentSession}
          onCreateSession={createSession}
          onDeleteSession={deleteSession}
          loading={loading}
        />
        <MainContent session={currentSession} apiBase={API_BASE} />
      </div>
    </div>
  )
}

export default App
