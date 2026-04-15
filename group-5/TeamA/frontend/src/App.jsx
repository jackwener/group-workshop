/**
 * M5-RA 研报智能分析助手 — 主应用组件
 * 对齐 Spec 06 功能规格：Header + Sidebar + Main + InputArea
 * 对齐 Spec 08 §3：React Hooks + useState + useEffect
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import {
  Layout, Button, Input, Card, Tag, Spin, Empty, Modal, Select,
  Typography, Space, Tooltip, Badge, Upload, Progress, theme, ConfigProvider, App as AntApp,
} from 'antd';
import {
  PlusOutlined, DeleteOutlined, SendOutlined, RobotOutlined,
  UserOutlined, MessageOutlined, QuestionCircleOutlined,
  ExperimentOutlined, CloudOutlined, DesktopOutlined,
  UploadOutlined, ThunderboltOutlined, SwapOutlined,
} from '@ant-design/icons';
import zhCN from 'antd/locale/zh_CN';
import './App.css';
import {
  getCapabilities, getSessions, createSession, deleteSession,
  getSessionRecords, ask, getProviders, uploadFile, getFileStatus,
  triggerAnalyze, getAnalyzeStatus,
} from './api';

const { Header, Sider, Content } = Layout;
const { TextArea } = Input;
const { Title, Text, Paragraph } = Typography;

function M5RAApp() {
  const { token } = theme.useToken();
  const { message: messageApi, modal } = AntApp.useApp();
  const chatEndRef = useRef(null);

  // ==================== React State（对齐 Spec 06 §8） ====================
  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [records, setRecords] = useState([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [capabilities, setCapabilities] = useState({
    copaw_configured: false, bailian_configured: false, model: null,
  });
  const [providers, setProviders] = useState([]);
  const [currentProvider, setCurrentProvider] = useState(null);
  // TODO: 文件上传状态（FE-Dev Task 2）
  // TODO: 深度分析状态（FE-Dev Task 5）

  // ==================== 初始化 ====================
  useEffect(() => {
    loadCapabilities();
    loadSessions();
    loadProviders();
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [records, loading]);

  // ==================== 数据加载 ====================
  const loadCapabilities = async () => {
    try {
      const data = await getCapabilities();
      setCapabilities(data);
    } catch (err) {
      console.error('加载能力状态失败:', err);
    }
  };

  const loadSessions = async () => {
    try {
      const data = await getSessions();
      setSessions(data.sessions || []);
      if (data.sessions?.length > 0 && !currentSession) {
        setCurrentSession(data.sessions[0]);
      }
    } catch (err) {
      messageApi.error('加载会话列表失败');
    }
  };

  const loadRecords = useCallback(async (sessionId) => {
    if (!sessionId) return;
    try {
      const data = await getSessionRecords(sessionId);
      setRecords(data.records || []);
    } catch (err) {
      messageApi.error('加载历史记录失败');
    }
  }, [messageApi]);

  const loadProviders = async () => {
    try {
      const data = await getProviders();
      setProviders(data.providers || []);
      setCurrentProvider(data.default);
    } catch (err) {
      console.error('加载模型列表失败:', err);
    }
  };

  useEffect(() => {
    if (currentSession) {
      loadRecords(currentSession.session_id);
    }
  }, [currentSession, loadRecords]);

  // ==================== 事件处理 ====================
  const handleCreateSession = async () => {
    try {
      const data = await createSession();
      setSessions([data, ...sessions]);
      setCurrentSession(data);
      setRecords([]);
      messageApi.success('新会话已创建');
    } catch (err) {
      messageApi.error('创建会话失败');
    }
  };

  const handleDeleteSession = (sessionId, e) => {
    e.stopPropagation();
    modal.confirm({
      title: '确认删除',
      content: '删除后无法恢复，确定要删除这个会话吗？',
      okText: '删除', okType: 'danger', cancelText: '取消',
      onOk: async () => {
        try {
          await deleteSession(sessionId);
          const newSessions = sessions.filter(s => s.session_id !== sessionId);
          setSessions(newSessions);
          if (currentSession?.session_id === sessionId) {
            setCurrentSession(newSessions.length > 0 ? newSessions[0] : null);
            setRecords([]);
          }
          messageApi.success('会话已删除');
        } catch (err) {
          messageApi.error('删除会话失败');
        }
      },
    });
  };

  const handleSend = async () => {
    if (!query.trim()) { messageApi.warning('请输入问题'); return; }
    if (!currentSession) { messageApi.warning('请先创建或选择一个会话'); return; }
    if (query.length > 500) { messageApi.warning('问题过长，最多500字符'); return; }

    setLoading(true);
    try {
      const data = await ask(query, currentSession.session_id, null, currentProvider);
      const newRecord = {
        id: Date.now().toString(), query,
        answer: data.answer, llm_used: data.llm_used, model: data.model,
        answer_source: data.answer_source, response_time_ms: data.response_time_ms,
        timestamp: new Date().toISOString(),
      };
      setRecords(prev => [...prev, newRecord]);
      setQuery('');
      loadSessions();
    } catch (err) {
      messageApi.error(err.message || '发送失败');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }
  };

  // ==================== 辅助函数 ====================
  const getSourceTag = (source) => {
    switch (source) {
      case 'copaw': return <Tag icon={<CloudOutlined />} color="blue">CoPaw</Tag>;
      case 'bailian': return <Tag icon={<ExperimentOutlined />} color="green">百炼</Tag>;
      case 'demo': return <Tag icon={<DesktopOutlined />} color="default">离线演示</Tag>;
      default: return <Tag color="default">{source}</Tag>;
    }
  };

  const getCapabilityTag = () => {
    if (capabilities.copaw_configured) return <Tag color="blue">CoPaw 已连接</Tag>;
    if (capabilities.bailian_configured) return <Tag color="green">百炼 已连接</Tag>;
    return <Tag color="default">离线演示</Tag>;
  };

  const faqQuestions = [
    { icon: '📊', text: '如何分析财报' },
    { icon: '⭐', text: '评级说明什么' },
    { icon: '🎯', text: '目标价怎么看' },
    { icon: '📈', text: '行业对比方法' },
    { icon: '💰', text: '估值指标解读' },
    { icon: '⚠️', text: '风险提示' },
  ];

  // ==================== 渲染 ====================
  return (
    <Layout style={{ height: '100vh' }}>
      {/* Header — 对齐 Spec 06 §2 */}
      <Header className="ira-header">
        <Space align="center">
          <RobotOutlined style={{ fontSize: 22, color: token.colorPrimary }} />
          <Title level={4} style={{ margin: 0, color: '#fff' }}>M5-RA · 研报智能分析助手</Title>
        </Space>
        <Space>
          {/* 模型切换 — 对齐 Spec 06 §7 大模型切换组件 */}
          <Select
            value={currentProvider}
            onChange={setCurrentProvider}
            style={{ minWidth: 140 }}
            size="small"
            options={providers.map(p => ({
              value: p.id, label: p.name, disabled: !p.available,
            }))}
            placeholder="选择模型"
          />
          {getCapabilityTag()}
        </Space>
      </Header>

      <Layout>
        {/* Sidebar — 对齐 Spec 06 §3 会话管理 */}
        <Sider width={280} className="ira-sider" theme="light">
          <div style={{ padding: 16 }}>
            <Button type="primary" icon={<PlusOutlined />} block size="large" onClick={handleCreateSession}>
              新建会话
            </Button>
          </div>
          <div className="session-list">
            {sessions.length === 0 ? (
              <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无会话" />
            ) : (
              sessions.map(session => (
                <div
                  key={session.session_id}
                  className={`session-item ${currentSession?.session_id === session.session_id ? 'active' : ''}`}
                  onClick={() => setCurrentSession(session)}
                >
                  <div className="session-item-content">
                    <MessageOutlined style={{ color: token.colorPrimary, marginRight: 8, flexShrink: 0 }} />
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <Text ellipsis strong style={{ display: 'block', fontSize: 13 }}>{session.title}</Text>
                      <Text type="secondary" style={{ fontSize: 12 }}>{session.query_count} 条对话</Text>
                    </div>
                    <Tooltip title="删除会话">
                      <Button type="text" size="small" danger icon={<DeleteOutlined />} className="delete-btn"
                        onClick={(e) => handleDeleteSession(session.session_id, e)} />
                    </Tooltip>
                  </div>
                </div>
              ))
            )}
          </div>
        </Sider>

        {/* Main Content — 对齐 Spec 06 §4 内容区三态 */}
        <Content className="ira-content">
          {!currentSession ? (
            /* 空状态 */
            <div className="center-placeholder">
              <Empty
                image={<RobotOutlined style={{ fontSize: 64, color: token.colorPrimary }} />}
                description={
                  <Space direction="vertical" size={4}>
                    <Text type="secondary" style={{ fontSize: 16 }}>欢迎使用研报智能分析助手</Text>
                    <Text type="secondary">请创建或选择一个会话开始</Text>
                  </Space>
                }
              >
                <Button type="primary" icon={<PlusOutlined />} onClick={handleCreateSession}>创建新会话</Button>
              </Empty>
            </div>
          ) : records.length === 0 && !loading ? (
            /* FAQ 常见问题 — 对齐 Spec 06 §4.3 */
            <div className="faq-container">
              <div className="faq-header">
                <QuestionCircleOutlined style={{ fontSize: 20, color: token.colorPrimary }} />
                <Title level={5} style={{ margin: 0 }}>试试问我这些问题</Title>
              </div>
              <div className="faq-grid">
                {faqQuestions.map((q, i) => (
                  <Card key={i} hoverable size="small" className="faq-card" onClick={() => setQuery(q.text)}>
                    <Space><span style={{ fontSize: 20 }}>{q.icon}</span><Text>{q.text}</Text></Space>
                  </Card>
                ))}
              </div>
            </div>
          ) : (
            /* 对话历史 */
            <div className="chat-history">
              {records.map(record => (
                <div key={record.id} className="message-group">
                  <div className="message user-message">
                    <div className="user-bubble"><Text style={{ color: '#fff' }}>{record.query}</Text></div>
                    <div className="avatar user-avatar"><UserOutlined /></div>
                  </div>
                  <div className="message ai-message">
                    <div className="avatar ai-avatar"><RobotOutlined /></div>
                    <div className="ai-bubble">
                      <div className="ai-meta">
                        {getSourceTag(record.answer_source)}
                        <Text type="secondary" style={{ fontSize: 12 }}>
                          {new Date(record.timestamp).toLocaleTimeString()}
                          {record.response_time_ms && ` · ${record.response_time_ms}ms`}
                        </Text>
                      </div>
                      <div className="ai-answer">
                        {record.answer.split('\n').map((line, i) => (
                          <Paragraph key={i} style={{ marginBottom: 4 }}>{line}</Paragraph>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              {loading && (
                <div className="message ai-message">
                  <div className="avatar ai-avatar"><RobotOutlined /></div>
                  <div className="ai-bubble loading-bubble">
                    <Spin size="small" /><Text type="secondary" style={{ marginLeft: 8 }}>思考中...</Text>
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>
          )}

          {/* 输入区域 — 对齐 Spec 06 §5 */}
          {currentSession && (
            <div className="input-area">
              <div className="input-wrapper">
                {/* TODO: 文件上传按钮（FE-Dev Task 2） */}
                <TextArea
                  value={query} onChange={(e) => setQuery(e.target.value)} onKeyDown={handleKeyDown}
                  placeholder="请输入您的投研问题，按 Enter 发送，Shift+Enter 换行..."
                  autoSize={{ minRows: 2, maxRows: 5 }} maxLength={500} showCount
                  disabled={loading} style={{ resize: 'none' }}
                />
                <Button type="primary" icon={<SendOutlined />} size="large" loading={loading}
                  disabled={!query.trim()} onClick={handleSend} className="send-btn">
                  发送
                </Button>
                {/* TODO: 深度分析按钮（FE-Dev Task 5） */}
              </div>
            </div>
          )}
        </Content>
      </Layout>
    </Layout>
  );
}

export default function App() {
  return (
    <ConfigProvider locale={zhCN} theme={{ token: { colorPrimary: '#1677ff', borderRadius: 8 } }}>
      <AntApp>
        <M5RAApp />
      </AntApp>
    </ConfigProvider>
  );
}
