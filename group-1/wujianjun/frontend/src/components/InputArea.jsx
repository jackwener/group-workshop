import { useState } from 'react'

function InputArea({ onSend, isLoading, hasSession }) {
  const [input, setInput] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return
    
    onSend(input.trim())
    setInput('')
  }

  return (
    <form className="input-area" onSubmit={handleSubmit}>
      <div className="input-container">
        <input
          type="text"
          className="input-field"
          placeholder={hasSession ? "输入您的问题..." : "请先创建会话"}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={!hasSession || isLoading}
          maxLength={500}
        />
        <button 
          type="submit" 
          className="send-btn"
          disabled={!hasSession || isLoading || !input.trim()}
        >
          {isLoading ? '发送中...' : '发送'}
        </button>
      </div>
    </form>
  )
}

export default InputArea
