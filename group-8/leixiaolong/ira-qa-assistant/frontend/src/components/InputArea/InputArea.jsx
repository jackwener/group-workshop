import styles from './InputArea.module.css';

export default function InputArea({ query, setQuery, onSend, onClear, isLoading, disabled }) {
  const isOver = query.length > 500;
  const canSend = query.trim().length > 0 && !isOver && !isLoading && !disabled;

  const handleKeyDown = (e) => {
    if (e.ctrlKey && e.key === 'Enter' && canSend) {
      e.preventDefault();
      onSend();
    }
  };

  return (
    <div className={styles.container}>
      <textarea
        className={styles.textarea}
        rows={3}
        placeholder={disabled ? '请先创建或选择一个会话' : '请输入您的问题...'}
        value={query}
        onChange={e => setQuery(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled || isLoading}
      />
      <span className={`${styles.charCount} ${isOver ? styles.charCountOver : ''}`}>
        {query.length}/500
      </span>
      <button
        className={styles.sendBtn}
        onClick={onSend}
        disabled={!canSend}
      >
        {isLoading ? '发送中...' : '发送'}
      </button>
      <button className={styles.clearBtn} onClick={onClear}>
        清空
      </button>
    </div>
  );
}
