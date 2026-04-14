import { useState, useEffect } from 'react'
import { Layout, message as antMessage, Card, Button, Upload, Input, Row, Col } from 'antd'
import { FilePdfOutlined, StockOutlined, UploadOutlined, SearchOutlined, MessageOutlined } from '@ant-design/icons'
import SessionList from './components/SessionList'
import ChatWindow from './components/ChatWindow'
import { sessionApi, healthApi, analysisApi } from './services/api'

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

  // 快速创建研报分析会话
  const handleQuickReportAnalysis = async (file: File) => {
    try {
      const response = await sessionApi.createSession(`研报分析: ${file.name}`, 'report')
      const newSession = response.data.data
      setSessions([newSession, ...sessions])
      setCurrentSession(newSession)
      
      // 自动上传分析
      const analysisResponse = await analysisApi.analyzeReport(newSession.id, [file], true, false)
      antMessage.success('研报分析完成')
      loadSessions()
    } catch (error) {
      antMessage.error('研报分析失败')
    }
    return false
  }

  // 快速创建股票分析会话
  const [quickStockCode, setQuickStockCode] = useState('')
  const handleQuickStockAnalysis = async () => {
    if (!quickStockCode.trim() || quickStockCode.length !== 6) {
      antMessage.warning('请输入6位股票代码')
      return
    }
    try {
      const response = await sessionApi.createSession(`股票分析: ${quickStockCode}`, 'stock')
      const newSession = response.data.data
      setSessions([newSession, ...sessions])
      setCurrentSession(newSession)
      
      // 自动分析
      await analysisApi.analyzeStock(newSession.id, quickStockCode, undefined, 'full')
      antMessage.success('股票分析完成')
      setQuickStockCode('')
      loadSessions()
    } catch (error) {
      antMessage.error('股票分析失败')
    }
  }

  return (
    <Layout className="app-container">
      <Header style={{ 
        background: 'linear-gradient(135deg, #0052cc 0%, #003d8f 100%)', 
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 24px',
        boxShadow: '0 2px 8px rgba(0, 82, 204, 0.3)'
      }}>
        <div style={{ 
          fontSize: '20px', 
          fontWeight: 600, 
          color: '#fff',
          display: 'flex',
          alignItems: 'center',
          gap: '12px'
        }}>
          <span style={{
            width: '32px',
            height: '32px',
            background: 'rgba(255,255,255,0.2)',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '16px'
          }}>📊</span>
          投研问答助手
        </div>
        <div style={{ fontSize: '14px', color: 'rgba(255,255,255,0.9)' }}>
          服务状态: 
          <span style={{ 
            color: healthStatus === 'healthy' ? '#52c41a' : 
                   healthStatus === 'degraded' ? '#faad14' : '#ff4d4f',
            marginLeft: '8px',
            fontWeight: 500,
            background: 'rgba(255,255,255,0.95)',
            padding: '2px 10px',
            borderRadius: '12px'
          }}>
            {healthStatus === 'healthy' ? '● 正常' : 
             healthStatus === 'degraded' ? '● 降级' : '● 异常'}
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
          {!currentSession ? (
            // 主页 - 快捷功能入口
            <div style={{ padding: '40px', height: '100%', overflow: 'auto' }}>
              <div style={{ maxWidth: '800px', margin: '0 auto' }}>
                <h2 style={{ 
                  marginBottom: '32px', 
                  color: '#1a1a1a',
                  fontSize: '24px',
                  fontWeight: 600 
                }}>
                  欢迎使用投研问答助手
                </h2>
                <p style={{ marginBottom: '40px', color: '#666', fontSize: '16px' }}>
                  选择下方快捷功能开始分析，或从左侧创建新会话
                </p>
                
                <Row gutter={[24, 24]}>
                  {/* 研报阅读 */}
                  <Col span={12}>
                    <Card
                      hoverable
                      style={{ 
                        borderRadius: '12px',
                        border: '1px solid #e8ecf1',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.04)'
                      }}
                      cover={
                        <div style={{ 
                          height: '120px', 
                          background: 'linear-gradient(135deg, #0052cc 0%, #003d8f 100%)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center'
                        }}>
                          <FilePdfOutlined style={{ fontSize: '48px', color: '#fff' }} />
                        </div>
                      }
                    >
                      <Card.Meta
                        title={<span style={{ fontSize: '18px', fontWeight: 600 }}>研报阅读</span>}
                        description="上传PDF研报，AI自动提取核心观点、风险提示和投资建议"
                      />
                      <Upload
                        beforeUpload={handleQuickReportAnalysis}
                        accept=".pdf"
                        showUploadList={false}
                      >
                        <Button 
                          type="primary" 
                          icon={<UploadOutlined />}
                          block
                          style={{ marginTop: '16px' }}
                        >
                          上传研报
                        </Button>
                      </Upload>
                    </Card>
                  </Col>

                  {/* 股票分析 */}
                  <Col span={12}>
                    <Card
                      hoverable
                      style={{ 
                        borderRadius: '12px',
                        border: '1px solid #e8ecf1',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.04)'
                      }}
                      cover={
                        <div style={{ 
                          height: '120px', 
                          background: 'linear-gradient(135deg, #00a8e6 0%, #0052cc 100%)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center'
                        }}>
                          <StockOutlined style={{ fontSize: '48px', color: '#fff' }} />
                        </div>
                      }
                    >
                      <Card.Meta
                        title={<span style={{ fontSize: '18px', fontWeight: 600 }}>股票分析</span>}
                        description="输入股票代码，获取财务指标、研报摘要和综合评分"
                      />
                      <div style={{ display: 'flex', gap: '8px', marginTop: '16px' }}>
                        <Input
                          placeholder="输入6位股票代码，如：000001"
                          value={quickStockCode}
                          onChange={(e) => setQuickStockCode(e.target.value)}
                          maxLength={6}
                          style={{ flex: 1 }}
                          onPressEnter={handleQuickStockAnalysis}
                        />
                        <Button 
                          type="primary" 
                          icon={<SearchOutlined />}
                          onClick={handleQuickStockAnalysis}
                          disabled={!quickStockCode.trim() || quickStockCode.length !== 6}
                        >
                          股票分析
                        </Button>
                      </div>
                    </Card>
                  </Col>
                </Row>

                {/* 通用对话入口 */}
                <Card
                  style={{ 
                    marginTop: '24px',
                    borderRadius: '12px',
                    border: '1px solid #e8ecf1',
                    cursor: 'pointer'
                  }}
                  onClick={() => handleCreateSession('新对话', 'general')}
                  hoverable
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                    <div style={{
                      width: '48px',
                      height: '48px',
                      borderRadius: '12px',
                      background: 'linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}>
                      <MessageOutlined style={{ fontSize: '24px', color: '#0052cc' }} />
                    </div>
                    <div>
                      <div style={{ fontSize: '16px', fontWeight: 600, color: '#1a1a1a' }}>
                        通用对话
                      </div>
                      <div style={{ fontSize: '14px', color: '#666' }}>
                        自由提问，与AI助手进行投研相关交流
                      </div>
                    </div>
                  </div>
                </Card>
              </div>
            </div>
          ) : (
            <ChatWindow
              session={currentSession}
              onSessionUpdate={loadSessions}
            />
          )}
        </div>
      </Content>
    </Layout>
  )
}

export default App
