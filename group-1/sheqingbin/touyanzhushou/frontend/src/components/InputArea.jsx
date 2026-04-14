/**
 * InputArea 组件
 * 问题输入区域
 */
import React, { useState, useRef, useEffect } from 'react';
import './InputArea.css';

function InputArea({
  onSend,
  loading,
  disabled,
}) {
  const [query, setQuery] = useState('');
  const textareaRef = useRef(null);
  
  // 自动调整 textarea 高度
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
    }
  }, [query]);
  
  const handleSubmit = () => {
    const trimmedQuery = query.trim();
    if (!trimmedQuery || loading || disabled) return;
    
    if (trimmedQuery.length > 500) {
      alert('问题过长，最多500字符');
      return;
    }
    
    onSend(trimmedQuery);
    setQuery('');
    
    // 重置高度
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };
  
  const handleKeyDown = (e) => {
    // Ctrl/Cmd + Enter 发送
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      handleSubmit();
    }
  };
  
  const handleClear = () => {
    setQuery('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.focus();
    }
  };
  
  const charCount = query.length;
  const isOverLimit = charCount > 500;
  
  return (
    <div className="input-area">
      <div className="input-container">
        <textarea
          ref={textareaRef}
          className="input query-input"
          placeholder={disabled ? "请先创建或选择一个会话" : "请输入您的问题...（Ctrl+Enter 发送）"}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled || loading}
          rows={1}
        />
        <div className="input-actions">
          <span className={`char-count ${isOverLimit ? 'over-limit' : ''}`}>
            {charCount}/500
          </span>
          <button
            className="btn btn-text"
            onClick={handleClear}
            disabled={!query || loading}
            title="清空"
          >
            清空
          </button>
          <button
            className="btn btn-primary send-btn"
            onClick={handleSubmit}
            disabled={!query.trim() || loading || disabled || isOverLimit}
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                发送中...
              </>
            ) : (
              <>
                <span>发送</span>
                <span className="shortcut">↵</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

export default InputArea;
