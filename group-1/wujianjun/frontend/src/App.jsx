import { useState, useEffect, useCallback } from 'react'
import Header from './components/Header'
import Sidebar from './components/Sidebar'
import ChatContainer from './components/ChatContainer'
import InputArea from './components/InputArea'
import Toast from './components/Toast'

const API_BASE = '/api/v1/agent'

function App() {
  // 状态管理
  const [sessions, setSessions] = useState([])
  const [currentSessionId, setCurrentSessionId] = useState(null)
  const [messages, setMessages] = useState([])
  const [capabilities, setCapabilities] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [toast, setToast] = useState(null)

  // 获取能力状态
  useEffect(() => {
    fetchCapabilities()
    fetchSessions()
  }, [])

  // 获取当前会话的消息
  useEffect(() => {
    if (currentSessionId) {
      fetchMessages(currentSessionId)
    } else {
      setMessages([])
    }
  }, [currentSessionId])

  const showToast = (message) => {
    setToast(message)
    setTimeout(() => setToast(null), 3000)
  }

  // API 调用
  const fetchCapabilities = async () => {
    try {
      const res = await fetch(`${API_BASE}/capabilities`)
      const data = await res.json()
      setCapabilities(data.data)
    } catch (err) {
      console.error('获取能力状态失败:', err)
    }
  }

  const fetchSessions = async () => {
    try {
      const res = await fetch(`${API_BASE}/sessions`)
      const data = await res.json()
      setSessions(data.data.sessions)
    } catch (err) {
      console.error('获取会话列表失败:', err)
    }
  }

  const fetchMessages = async (sessionId) => {
    try {
      const res = await fetch(`${API_BASE}/sessions/${sessionId}/records`)
      const data = await res.json()
      // 转换记录为消息格式
      const msgs = data.data.records.flatMap(record => [
        { role: 'user', content: record.query, id: `${record.record_id}_q` },
        { 
          role: 'assistant', 
          content: record.answer, 
          id: `${record.record_id}_a`,
          answerSource: record.answer_source,
          responseTime: record.response_time_ms
        }
      ])
      setMessages(msgs)
    } catch (err) {
      console.error('获取消息失败:', err)
    }
  }

  const createSession = async () => {
    try {
      const res = await fetch(`${API_BASE}/sessions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: '新会话' })
      })
      const data = await res.json()
      const newSession = data.data
      setSessions(prev => [newSession, ...prev])
      setCurrentSessionId(newSession.session_id)
    } catch (err) {
      showToast('创建会话失败')
    }
  }

  const deleteSession = async (sessionId) => {
    try {
      const res = await fetch(`${API_BASE}/sessions/${sessionId}`, {
        method: 'DELETE'
      })
      if (res.ok) {
        setSessions(prev => prev.filter(s => s.session_id !== sessionId))
        if (currentSessionId === sessionId) {
          setCurrentSessionId(null)
          setMessages([])
        }
      }
    } catch (err) {
      showToast('删除会话失败')
    }
  }

  const sendMessage = async (query) => {
    if (!currentSessionId) {
      showToast('请先创建会话')
      return
    }

    if (!query.trim()) {
      showToast('请输入问题')
      return
    }

    if (query.length > 500) {
      showToast('问题长度超过500字符限制')
      return
    }

    // 添加用户消息
    const userMsg = { role: 'user', content: query, id: Date.now().toString() }
    setMessages(prev => [...prev, userMsg])
    setIsLoading(true)

    try {
      const res = await fetch(`${API_BASE}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, session_id: currentSessionId })
      })

      const data = await res.json()

      if (!res.ok) {
        showToast(data.error?.message || '请求失败')
        setIsLoading(false)
        return
      }

      // 添加助手回复
      const assistantMsg = {
        role: 'assistant',
        content: data.data.answer,
        id: data.data.record_id,
        answerSource: data.data.answer_source,
        responseTime: data.data.response_time_ms
      }
      setMessages(prev => [...prev, assistantMsg])

      // 刷新会话列表（更新标题和计数）
      fetchSessions()
    } catch (err) {
      showToast('发送消息失败')
    } finally {
      setIsLoading(false)
    }
  }

  const selectSession = (sessionId) => {
    setCurrentSessionId(sessionId)
  }

  const currentSession = sessions.find(s => s.session_id === currentSessionId)

  return (
    <div className="app">
      <Header capabilities={capabilities} />
      <Sidebar
        sessions={sessions}
        currentSessionId={currentSessionId}
        onSelectSession={selectSession}
        onCreateSession={createSession}
        onDeleteSession={deleteSession}
      />
      <main className="main">
        <ChatContainer
          messages={messages}
          isLoading={isLoading}
          hasSession={!!currentSessionId}
          onSendMessage={sendMessage}
        />
        <InputArea
          onSend={sendMessage}
          isLoading={isLoading}
          hasSession={!!currentSessionId}
        />
      </main>
      {toast && <Toast message={toast} />}
    </div>
  )
}

export default App
