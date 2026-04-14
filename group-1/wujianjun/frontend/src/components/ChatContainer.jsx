import { useEffect, useRef } from 'react'

const FAQS = [
  '这份研报的核心观点是什么？',
  '公司的目标价和评级是多少？',
  '2025年一季报业绩如何？',
  '主要风险因素有哪些？'
]

function ChatContainer({ messages, isLoading, hasSession, onSendMessage }) {
  const messagesEndRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  if (!hasSession) {
    return (
      <div className="chat-container">
        <div className="empty-state">
          <h3>欢迎使用投研智能问答助手</h3>
          <p>请先创建或选择一个会话开始提问</p>
        </div>
      </div>
    )
  }

  if (messages.length === 0) {
    return (
      <div className="chat-container">
        <div className="empty-state">
          <h3>开始提问</h3>
          <p>您可以尝试以下常见问题：</p>
          <div className="faq-grid">
            {FAQS.map((faq, index) => (
              <div 
                key={index} 
                className="faq-item"
                onClick={() => onSendMessage(faq)}
              >
                {faq}
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="chat-container">
      {messages.map((msg) => (
        <div key={msg.id} className={`message ${msg.role}`}>
          <div className="message-content">
            {msg.content}
            {msg.role === 'assistant' && (
              <div className="message-meta">
                <span className={`source-tag ${msg.answerSource}`}>
                  {msg.answerSource === 'copaw' ? 'CoPaw' : 
                   msg.answerSource === 'bailian' ? '百炼' : '演示'}
                </span>
                {msg.responseTime && (
                  <span>{msg.responseTime}ms</span>
                )}
              </div>
            )}
          </div>
        </div>
      ))}
      {isLoading && (
        <div className="message assistant">
          <div className="message-content">
            思考中...
          </div>
        </div>
      )}
      <div ref={messagesEndRef} />
    </div>
  )
}

export default ChatContainer
