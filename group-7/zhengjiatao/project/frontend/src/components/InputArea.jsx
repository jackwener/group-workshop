import { useState } from 'react';
import styles from './InputArea.module.css';

function InputArea({ onSend, loading, disabled }) {
  const [query, setQuery] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // 清除错误
    setError('');
    
    // 校验
    const trimmedQuery = query.trim();
    if (!trimmedQuery) {
      setError('请输入问题');
      return;
    }
    
    if (trimmedQuery.length > 500) {
      setError('问题过长，请控制在500字符以内');
      return;
    }
    
    // 发送
    onSend(trimmedQuery);
    setQuery('');
  };

  const handleClear = () => {
    setQuery('');
    setError('');
  };

  const handleKeyDown = (e) => {
    // Ctrl+Enter 或 Cmd+Enter 发送
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      handleSubmit(e);
    }
  };

  return (
    <div className={styles.container}>
      {error && <div className={styles.error}>{error}</div>}
      
      <form className={styles.form} onSubmit={handleSubmit}>
        <textarea
          className={styles.textarea}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="请输入您的问题..."
          rows={3}
          disabled={disabled || loading}
          maxLength={500}
        />
        
        <div className={styles.toolbar}>
          <span className={styles.charCount}>
            {query.length}/500
          </span>
          
          <div className={styles.buttons}>
            <button
              type="button"
              className={styles.clearBtn}
              onClick={handleClear}
              disabled={disabled || loading || !query}
            >
              清空
            </button>
            
            <button
              type="submit"
              className={styles.sendBtn}
              disabled={disabled || loading || !query.trim()}
            >
              {loading ? '发送中...' : '发送'}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}

export default InputArea;
