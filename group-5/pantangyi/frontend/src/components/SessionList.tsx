import { useState } from 'react'
import { Button, List, Modal, Form, Input, Select, Popconfirm, Spin, Empty } from 'antd'
import { PlusOutlined, DeleteOutlined, MessageOutlined } from '@ant-design/icons'

const { Option } = Select

interface Session {
  id: string
  title: string
  type: string
  status: string
  created_at: string
  updated_at: string
  message_count: number
}

interface SessionListProps {
  sessions: Session[]
  currentSession: Session | null
  onSelect: (session: Session) => void
  onDelete: (sessionId: string) => void
  onCreate: (title: string, type: string) => void
  loading: boolean
}

function SessionList({
  sessions,
  currentSession,
  onSelect,
  onDelete,
  onCreate,
  loading
}: SessionListProps) {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [form] = Form.useForm()

  const handleCreate = (values: { title: string; type: string }) => {
    onCreate(values.title || '新会话', values.type)
    setIsModalOpen(false)
    form.resetFields()
  }

  const formatTime = (timeStr: string) => {
    const date = new Date(timeStr)
    return date.toLocaleString('zh-CN', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: '16px' }}>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          block
          onClick={() => setIsModalOpen(true)}
        >
          新建会话
        </Button>
      </div>

      <div style={{ flex: 1, overflow: 'auto', padding: '8px' }}>
        {loading ? (
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <Spin />
          </div>
        ) : sessions.length === 0 ? (
          <Empty description="暂无会话" style={{ marginTop: '40px' }} />
        ) : (
          <List
            dataSource={sessions}
            renderItem={(session) => (
              <List.Item
                style={{
                  padding: '12px',
                  marginBottom: '8px',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  background: currentSession?.id === session.id ? '#0052cc' : 'transparent',
                  color: currentSession?.id === session.id ? '#fff' : 'inherit',
                  transition: 'all 0.2s'
                }}
                onClick={() => onSelect(session)}
                actions={[
                  <Popconfirm
                    title="确定要删除这个会话吗？"
                    onConfirm={(e) => {
                      e?.stopPropagation()
                      onDelete(session.id)
                    }}
                    okText="确定"
                    cancelText="取消"
                  >
                    <Button
                      type="text"
                      size="small"
                      danger
                      icon={<DeleteOutlined />}
                      onClick={(e) => e.stopPropagation()}
                      style={{
                        color: currentSession?.id === session.id ? '#fff' : undefined
                      }}
                    />
                  </Popconfirm>
                ]}
              >
                <List.Item.Meta
                  avatar={<MessageOutlined style={{ 
                    fontSize: '20px',
                    color: currentSession?.id === session.id ? '#fff' : '#0052cc'
                  }} />}
                  title={
                    <div style={{
                      fontWeight: 500,
                      color: currentSession?.id === session.id ? '#fff' : 'inherit'
                    }}>
                      {session.title}
                    </div>
                  }
                  description={
                    <div style={{
                      fontSize: '12px',
                      color: currentSession?.id === session.id ? 'rgba(255,255,255,0.7)' : '#999'
                    }}>
                      {formatTime(session.updated_at)} · {session.message_count} 条消息
                    </div>
                  }
                />
              </List.Item>
            )}
          />
        )}
      </div>

      <Modal
        title="新建会话"
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        footer={null}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreate}
          initialValues={{ type: 'general' }}
        >
          <Form.Item
            label="会话标题"
            name="title"
            rules={[{ max: 100, message: '标题最多100个字符' }]}
          >
            <Input placeholder="请输入会话标题（可选）" />
          </Form.Item>

          <Form.Item
            label="会话类型"
            name="type"
          >
            <Select>
              <Option value="general">通用</Option>
              <Option value="report">研报分析</Option>
              <Option value="stock">股票分析</Option>
            </Select>
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              创建
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default SessionList
