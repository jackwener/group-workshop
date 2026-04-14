/**
 * ChatArea 组件
 * 主内容区：空状态、常见问题网格、对话历史
 */
import React from 'react';
import './ChatArea.css';

// 常见问题列表
const COMMON_QUESTIONS = [
  { icon: '📈', title: '对比宁德时代Q3研报' },
  { icon: '🔋', title: '分析新能源行业趋势' },
  { icon: '🏦', title: '券商对茅台的评级对比' },
  { icon: '💹', title: '半导体行业投资机会' },
  { icon: '🌐', title: '中概股回归影响分析' },
  { icon: '📊', title: '消费板块配置建议' },
];

function ChatArea({
  currentSession,
  records,
  onSendQuestion,
  loading,
}) {
  // 确定当前显示的状态
  const getDisplayState = () => {
    if (!currentSession) {
      return 'empty'; // 空状态
    }
    if (records.length === 0) {
      return 'questions'; // 常见问题网格
    }
    return 'chat'; // 对话历史
  };
  
  const displayState = getDisplayState();
  
  const handleQuestionClick = (question) => {
    onSendQuestion(question);
  };
  
  const formatTime = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
  };
  
  const getSourceTag = (source) => {
    switch (source) {
      case 'copaw':
        return <span className="tag tag-copaw">CoPaw</span>;
      case 'bailian':
        return <span className="tag tag-bailian">百炼</span>;
      case 'demo':
        return <span className="tag tag-demo">离线演示</span>;
      default:
        return null;
    }
  };
  
  // 空状态
  if (displayState === 'empty') {
    return (
      <div className="chat-area">
        <div className="empty-state">
          <div className="empty-state-icon">💬</div>
          <h3>请创建或选择一个会话开始</h3>
          <p>点击左侧"新建会话"按钮创建新对话</p>
        </div>
      </div>
    );
  }
  
  // 常见问题网格
  if (displayState === 'questions') {
    return (
      <div className="chat-area">
        <div className="questions-grid-container">
          <h3 className="questions-title">💡 常见问题</h3>
          <div className="questions-grid">
            {COMMON_QUESTIONS.map((q, index) => (
              <div
                key={index}
                className="question-card"
                onClick={() => handleQuestionClick(q.title)}
              >
                <span className="question-icon">{q.icon}</span>
                <span className="question-title">{q.title}</span>
              </div>
            ))}
          </div>
          <p className="questions-hint">点击上方问题快速开始，或在下方输入框输入您的问题</p>
        </div>
      </div>
    );
  }
  
  // 对话历史
  return (
    <div className="chat-area">
      <div className="chat-messages">
        {records.map((record) => (
          <div key={record.id} className="message-group">
            {/* 用户问题 */}
            <div className="message user-message">
              <div className="message-avatar">👤</div>
              <div className="message-content">
                <div className="message-text">{record.query}</div>
                <div className="message-time">{formatTime(record.timestamp)}</div>
              </div>
            </div>
            
            {/* AI 回答 */}
            <div className="message ai-message">
              <div className="message-avatar">🤖</div>
              <div className="message-content">
                <div className="message-header">
                  {getSourceTag(record.answer_source)}
                  {record.model && (
                    <span className="model-info">{record.model}</span>
                  )}
                </div>
                <div className="message-text">
                  {record.answer.split('\n').map((line, i) => (
                    <p key={i}>{line || <br />}</p>
                  ))}
                </div>
                <div className="message-footer">
                  <span className="response-time">{record.response_time_ms}ms</span>
                </div>
              </div>
            </div>
          </div>
        ))}
        
        {loading && (
          <div className="message ai-message loading">
            <div className="message-avatar">🤖</div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default ChatArea;
