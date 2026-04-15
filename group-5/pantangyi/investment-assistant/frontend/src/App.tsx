import { useState, useEffect } from 'react'
import { Layout, message as antMessage } from 'antd'
import SessionList from './components/SessionList'
import ChatWindow from './components/ChatWindow'
import { sessionApi, healthApi } from './services/api'

const { Header, Content } = Layout

interface Session {
  id: string
  title: string
  type: string
  status: string
  created_at: string
  updated_at: string
  message_count: number
}

function App() {
  const [sessions, setSessions] = useState<Session[]>([])
  const [currentSession, setCurrentSession] = useState<Session | null>(null)
  const [loading, setLoading] = useState(false)
  const [healthStatus, setHealthStatus] = useState<string>('checking')

  // Check health on mount
  useEffect(() => {
    checkHealth()
    loadSessions()
  }, [])

  const checkHealth = async () => {
    try {
      const response = await healthApi.checkHealth()
      setHealthStatus(response.data.data.status)
    } catch (error) {
      setHealthStatus('unhealthy')
    }
  }

  const loadSessions = async () => {
    try {
      setLoading(true)
      const response = await sessionApi.listSessions(20, 0)
      setSessions(response.data.data.items)
    } catch (error) {
      antMessage.error('加载会话列表失败')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateSession = async (title: string, type: string) => {
    try {
      const response = await sessionApi.createSession(title, type)
      const newSession = response.data.data
      setSessions([newSession, ...sessions])
      setCurrentSession(newSession)
      antMessage.success('会话创建成功')
    } catch (error) {
      antMessage.error('创建会话失败')
    }
  }

  const handleDeleteSession = async (sessionId: string) => {
    try {
      await sessionApi.deleteSession(sessionId)
      setSessions(sessions.filter(s => s.id !== sessionId))
      if (currentSession?.id === sessionId) {
        setCurrentSession(null)
      }
      antMessage.success('会话已删除')
    } catch (error) {
      antMessage.error('删除会话失败')
    }
  }

  const handleSelectSession = (session: Session) => {
    setCurrentSession(session)
  }

  return (
    <Layout className="app-container">
      <Header style={{ 
        background: '#fff', 
        borderBottom: '1px solid #e8e8e8',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 24px'
      }}>
        <div style={{ fontSize: '18px', fontWeight: 600 }}>
          投研问答助手
        </div>
        <div style={{ fontSize: '14px', color: '#666' }}>
          服务状态: 
          <span style={{ 
            color: healthStatus === 'healthy' ? '#52c41a' : 
                   healthStatus === 'degraded' ? '#faad14' : '#ff4d4f',
            marginLeft: '8px'
          }}>
            {healthStatus === 'healthy' ? '正常' : 
             healthStatus === 'degraded' ? '降级' : '异常'}
          </span>
        </div>
      </Header>
      
      <Content className="main-layout">
        <div className="sidebar">
          <SessionList
            sessions={sessions}
            currentSession={currentSession}
            onSelect={handleSelectSession}
            onDelete={handleDeleteSession}
            onCreate={handleCreateSession}
            loading={loading}
          />
        </div>
        
        <div className="chat-area">
          <ChatWindow
            session={currentSession}
            onSessionUpdate={loadSessions}
          />
        </div>
      </Content>
    </Layout>
  )
}

export default App
