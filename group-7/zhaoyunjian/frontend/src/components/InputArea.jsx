import React from 'react';
import './InputArea.css';

/**
 * InputArea组件
 * 问题输入区域：textarea + 发送按钮 + 清空按钮
 */
function InputArea({
  query,
  loading,
  onQueryChange,
  onSend,
  onClear,
  disabled,
}) {
  // 处理键盘事件
  const handleKeyDown = (e) => {
    // Ctrl/Cmd + Enter 发送
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      onSend();
    }
  };

  // 字符数限制
  const maxLength = 500;
  const charCount = query.length;
  const isOverLimit = charCount > maxLength;

  return (
    <div className="input-area">
      <div className="input-container">
        <textarea
          className={`query-input ${isOverLimit ? 'query-input-error' : ''}`}
          value={query}
          onChange={(e) => onQueryChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={disabled ? '请先创建或选择会话' : '请输入您的问题...'}
          rows={3}
          disabled={disabled || loading}
        />
        <div className="input-toolbar">
          <span className={`char-count ${isOverLimit ? 'char-count-error' : ''}`}>
            {charCount}/{maxLength}
          </span>
          <div className="input-actions">
            <button
              className="btn btn-default"
              onClick={onClear}
              disabled={loading || !query}
            >
              清空
            </button>
            <button
              className="btn btn-primary"
              onClick={onSend}
              disabled={disabled || loading || !query.trim() || isOverLimit}
            >
              {loading ? '发送中...' : '发送'}
            </button>
          </div>
        </div>
      </div>
      <div className="input-hint">
        <span>Ctrl + Enter 快速发送</span>
      </div>
    </div>
  );
}

export default InputArea;
