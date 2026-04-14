import { useState, useEffect, useRef } from 'react'
import {
  Input,
  Button,
  Upload,
  message as antMessage,
  Card,
  Tag,
  Space,
  Spin,
  Empty,
  Tabs,
  Tooltip
} from 'antd'
import {
  SendOutlined,
  UploadOutlined,
  FilePdfOutlined,
  StockOutlined,
  DownloadOutlined,
  InfoCircleOutlined
} from '@ant-design/icons'
import { sessionApi, analysisApi, reportApi } from '../services/api'

const { TextArea } = Input
const { TabPane } = Tabs

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  type: string
  timestamp: string
  attachments?: any[]
}

interface Session {
  id: string
  title: string
  type: string
}

interface ChatWindowProps {
  session: Session | null
  onSessionUpdate: () => void
}

function ChatWindow({ session, onSessionUpdate }: ChatWindowProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [analyzing, setAnalyzing] = useState(false)
  const [stockCode, setStockCode] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (session) {
      loadMessages()
    } else {
      setMessages([])
    }
  }, [session])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const loadMessages = async () => {
    if (!session) return
    
    try {
      const response = await sessionApi.getSession(session.id)
      setMessages(response.data.data.messages || [])
    } catch (error) {
      antMessage.error('加载消息失败')
    }
  }

  const handleSendMessage = async () => {
    if (!session || !inputValue.trim()) return

    const content = inputValue.trim()
    setInputValue('')
    setLoading(true)

    try {
      const response = await sessionApi.sendMessage(session.id, content, 'text')
      const assistantMessage = response.data.data
      
      setMessages(prev => [
        ...prev,
        {
          id: 'temp-user',
          role: 'user',
          content,
          type: 'text',
          timestamp: new Date().toISOString()
        },
        {
          id: assistantMessage.message_id,
          role: 'assistant',
          content: assistantMessage.content,
          type: 'text',
          timestamp: assistantMessage.timestamp
        }
      ])
      
      onSessionUpdate()
    } catch (error) {
      antMessage.error('发送消息失败')
    } finally {
      setLoading(false)
    }
  }

  const handleUpload = async (file: File) => {
    if (!session) {
      antMessage.error('请先选择或创建一个会话')
      return false
    }

    setUploading(true)

    try {
      const response = await analysisApi.analyzeReport(session.id, [file], true, false)
      const result = response.data.data
      
      // Add analysis result as a message
      const reports = result.reports || []
      let content = '研报分析结果：\n\n'
      
      reports.forEach((report: any, index: number) => {
        content += `【研报${index + 1}】${report.filename}\n`
        content += `标题：${report.title}\n`
        content += `摘要：${report.summary}\n`
        content += `评级：${report.rating}\n\n`
      })

      setMessages(prev => [
        ...prev,
        {
          id: 'temp-upload',
          role: 'user',
          content: `上传文件: ${file.name}`,
          type: 'file',
          timestamp: new Date().toISOString()
        },
        {
          id: result.analysis_id,
          role: 'assistant',
          content,
          type: 'analysis',
          timestamp: new Date().toISOString(),
          attachments: [{ analysis_id: result.analysis_id }]
        }
      ])

      if (result.llm_status !== 'primary') {
        antMessage.warning('当前使用降级模式，分析结果仅供参考')
      }

      onSessionUpdate()
    } catch (error) {
      antMessage.error('研报分析失败')
    } finally {
      setUploading(false)
    }

    return false
  }

  const handleAnalyzeStock = async () => {
    if (!session || !stockCode.trim()) return

    const code = stockCode.trim()
    setStockCode('')
    setAnalyzing(true)

    try {
      const response = await analysisApi.analyzeStock(session.id, code, undefined, 'full')
      const result = response.data.data

      const content = `股票分析报告：\n\n` +
        `股票代码：${result.stock_code}\n` +
        `股票名称：${result.stock_name}\n` +
        `综合评分：${result.comprehensive_score}\n` +
        `风险等级：${result.risk_level}\n` +
        `投资建议：${result.recommendation}\n\n` +
        `财务指标：\n` +
        `- 营收：${result.financial_indicators?.revenue || 'N/A'}\n` +
        `- 净利润：${result.financial_indicators?.profit || 'N/A'}\n` +
        `- ROE：${result.financial_indicators?.roe || 'N/A'}%\n\n` +
        `研报摘要：${result.report_summary || '无'}`

      setMessages(prev => [
        ...prev,
        {
          id: 'temp-stock-user',
          role: 'user',
          content: `查询股票: ${code}`,
          type: 'text',
          timestamp: new Date().toISOString()
        },
        {
          id: result.analysis_id,
          role: 'assistant',
          content,
          type: 'analysis',
          timestamp: new Date().toISOString(),
          attachments: [{ analysis_id: result.analysis_id }]
        }
      ])

      onSessionUpdate()
    } catch (error) {
      antMessage.error('股票分析失败')
    } finally {
      setAnalyzing(false)
    }
  }

  const handleDownloadReport = async (analysisId: string) => {
    try {
      // First generate report
      const genResponse = await reportApi.generateReport(analysisId)
      const reportId = genResponse.data.data.id

      // Then download
      const response = await reportApi.downloadReport(reportId, 'pdf')
      const blob = new Blob([response.data], { type: 'application/pdf' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `report_${reportId}.pdf`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      antMessage.success('报告下载成功')
    } catch (error) {
      antMessage.error('报告下载失败')
    }
  }

  const formatTime = (timeStr: string) => {
    const date = new Date(timeStr)
    return date.toLocaleString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (!session) {
    return (
      <div style={{
        height: '100%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <Empty description="请选择一个会话或创建新会话" />
      </div>
    )
  }

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <div style={{
        padding: '16px 24px',
        borderBottom: '1px solid #e8e8e8',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div>
          <h3 style={{ margin: 0 }}>{session.title}</h3>
          <Tag color="blue">{session.type === 'stock' ? '股票分析' : session.type === 'report' ? '研报分析' : '通用'}</Tag>
        </div>
      </div>

      {/* Messages */}
      <div style={{ flex: 1, overflow: 'auto', padding: '24px' }}>
        {messages.length === 0 ? (
          <Empty description="开始对话吧" style={{ marginTop: '100px' }} />
        ) : (
          messages.map((msg, index) => (
            <div
              key={index}
              style={{
                display: 'flex',
                gap: '12px',
                marginBottom: '16px',
                flexDirection: msg.role === 'user' ? 'row-reverse' : 'row'
              }}
            >
              <div style={{
                width: '36px',
                height: '36px',
                borderRadius: '50%',
                background: msg.role === 'user' ? '#52c41a' : '#1890ff',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#fff',
                fontSize: '14px',
                flexShrink: 0
              }}>
                {msg.role === 'user' ? '我' : 'AI'}
              </div>
              <div style={{ maxWidth: '70%' }}>
                <div style={{
                  padding: '12px 16px',
                  borderRadius: '12px',
                  background: msg.role === 'user' ? '#1890ff' : '#f5f5f5',
                  color: msg.role === 'user' ? '#fff' : 'inherit',
                  whiteSpace: 'pre-wrap'
                }}>
                  {msg.content}
                </div>
                <div style={{
                  fontSize: '12px',
                  color: '#999',
                  marginTop: '4px',
                  textAlign: msg.role === 'user' ? 'right' : 'left'
                }}>
                  {formatTime(msg.timestamp)}
                </div>
                
                {/* Download button for analysis messages */}
                {msg.type === 'analysis' && msg.attachments?.[0]?.analysis_id && (
                  <Button
                    type="link"
                    size="small"
                    icon={<DownloadOutlined />}
                    onClick={() => handleDownloadReport(msg.attachments![0].analysis_id)}
                    style={{ padding: 0 }}
                  >
                    下载报告
                  </Button>
                )}
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div style={{ padding: '16px 24px', borderTop: '1px solid #e8e8e8', background: '#fafafa' }}>
        <Tabs defaultActiveKey="chat">
          <TabPane tab="对话" key="chat">
            <Space direction="vertical" style={{ width: '100%' }}>
              <TextArea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="输入消息..."
                autoSize={{ minRows: 2, maxRows: 4 }}
                onPressEnter={(e) => {
                  if (!e.shiftKey) {
                    e.preventDefault()
                    handleSendMessage()
                  }
                }}
              />
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Upload
                  beforeUpload={handleUpload}
                  accept=".pdf,.doc,.docx"
                  showUploadList={false}
                >
                  <Button icon={<UploadOutlined />} loading={uploading}>
                    上传研报
                  </Button>
                </Upload>
                <Button
                  type="primary"
                  icon={<SendOutlined />}
                  onClick={handleSendMessage}
                  loading={loading}
                  disabled={!inputValue.trim()}
                >
                  发送
                </Button>
              </div>
            </Space>
          </TabPane>
          
          <TabPane tab="股票查询" key="stock">
            <Space direction="vertical" style={{ width: '100%' }}>
              <Input
                placeholder="输入股票代码（6位数字）"
                value={stockCode}
                onChange={(e) => setStockCode(e.target.value)}
                maxLength={6}
                prefix={<StockOutlined />}
              />
              <Button
                type="primary"
                icon={<SearchOutlined />}
                onClick={handleAnalyzeStock}
                loading={analyzing}
                disabled={!stockCode.trim() || stockCode.length !== 6}
                block
              >
                分析股票
              </Button>
            </Space>
          </TabPane>
        </Tabs>
      </div>
    </div>
  )
}

// Missing import
import { SearchOutlined } from '@ant-design/icons'

export default ChatWindow
