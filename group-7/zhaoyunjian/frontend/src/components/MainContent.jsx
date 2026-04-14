import React from 'react';
import './MainContent.css';

// 快捷问题配置
const QUICK_QUESTIONS = [
  {
    icon: '📊',
    title: '分析财报',
    subtitle: '宁德时代最新',
    query: '分析宁德时代最新财报的关键指标',
  },
  {
    icon: '📈',
    title: '对比研报',
    subtitle: '比亚迪vs特斯拉',
    query: '对比比亚迪和特斯拉的最新研报',
  },
  {
    icon: '🔍',
    title: '提取指标',
    subtitle: '关键指标提取',
    query: '提取研报中的营收、净利润、毛利率等关键指标',
  },
  {
    icon: '📋',
    title: '总结趋势',
    subtitle: '行业趋势总结',
    query: '总结新能源行业的最新发展趋势',
  },
];

/**
 * MainContent组件
 * 三态渲染：空状态 / 常见问题网格 / 对话历史列表
 */
function MainContent({ currentSession, records, loading, error, onClearError }) {
  // 格式化时间
  const formatTime = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // 格式化响应时间
  const formatResponseTime = (ms) => {
    if (!ms) return '';
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  // 获取来源标签样式
  const getSourceClass = (source) => {
    switch (source) {
      case 'copaw':
        return 'source-copaw';
      case 'bailian':
        return 'source-bailian';
      default:
        return 'source-demo';
    }
  };

  // 获取来源显示文本
  const getSourceText = (source) => {
    switch (source) {
      case 'copaw':
        return 'CoPaw';
      case 'bailian':
        return '百炼';
      default:
        return '离线演示';
    }
  };

  // 渲染空状态
  const renderEmptyState = () => (
    <div className="empty-state">
      <div className="empty-icon">💬</div>
      <p className="empty-title">请创建或选择一个会话开始</p>
      <p className="empty-hint">点击左侧"+ 新建"按钮创建新会话</p>
    </div>
  );

  // 渲染常见问题网格
  const renderQuickQuestions = () => (
    <div className="quick-questions">
      <div className="quick-questions-header">
        <h3 className="quick-questions-title">欢迎使用投研问答助手</h3>
        <p className="quick-questions-subtitle">
          选择一个常见问题快速开始，或在下方输入您的问题
        </p>
      </div>
      <div className="quick-questions-grid">
        {QUICK_QUESTIONS.map((item, index) => (
          <div
            key={index}
            className="quick-question-card"
            onClick={() => {
              // TODO: 填充到输入框并触发发送
              console.log('Selected:', item.query);
            }}
          >
            <div className="quick-question-icon">{item.icon}</div>
            <div className="quick-question-title">{item.title}</div>
            <div className="quick-question-subtitle">{item.subtitle}</div>
          </div>
        ))}
      </div>
    </div>
  );

  // 渲染对话历史
  const renderChatHistory = () => (
    <div className="chat-history">
      {records.map((record) => (
        <div key={record.record_id} className="chat-record">
          {/* 用户问题气泡 */}
          <div className="chat-bubble chat-bubble-user">
            <div className="chat-bubble-content">{record.query}</div>
          </div>

          {/* 助手回答气泡 */}
          <div className="chat-bubble chat-bubble-assistant">
            <div className="chat-bubble-content">{record.answer}</div>
            <div className="chat-bubble-meta">
              <span className={`source-tag ${getSourceClass(record.answer_source)}`}>
                {getSourceText(record.answer_source)}
              </span>
              <span className="meta-time">{formatTime(record.timestamp)}</span>
              {record.model && (
                <span className="meta-model">{record.model}</span>
              )}
              {record.response_time_ms > 0 && (
                <span className="meta-time-cost">
                  {formatResponseTime(record.response_time_ms)}
                </span>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );

  // 确定当前状态
  const getCurrentState = () => {
    if (!currentSession) return 'empty';
    if (records.length === 0) return 'quick-questions';
    return 'chat-history';
  };

  const currentState = getCurrentState();

  return (
    <main className="main-content">
      {/* 错误提示 */}
      {error && (
        <div className="error-banner">
          <span className="error-message">{error}</span>
          <button className="error-close" onClick={onClearError}>
            ×
          </button>
        </div>
      )}

      {/* 加载中 */}
      {loading && (
        <div className="loading-indicator">
          <div className="loading-spinner"></div>
          <span>思考中...</span>
        </div>
      )}

      {/* 内容区域 */}
      <div className="content-area">
        {currentState === 'empty' && renderEmptyState()}
        {currentState === 'quick-questions' && renderQuickQuestions()}
        {currentState === 'chat-history' && renderChatHistory()}
      </div>
    </main>
  );
}

export default MainContent;
