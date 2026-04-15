import { useState } from 'react';
import styles from './RecordCard.module.css';

function RecordCard({ record, onCopy }) {
  const [copied, setCopied] = useState(false);

  const getSourceStyle = (source) => {
    switch (source) {
      case 'copaw':
        return styles.sourceCopaw;
      case 'bailian':
        return styles.sourceBailian;
      case 'demo':
      default:
        return styles.sourceDemo;
    }
  };

  const getSourceLabel = (source) => {
    switch (source) {
      case 'copaw':
        return 'CoPaw';
      case 'bailian':
        return '百炼';
      case 'demo':
      default:
        return '离线演示';
    }
  };

  const handleCopy = () => {
    const text = `问题：${record.query}\n\n回答：${record.answer}`;
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      onCopy?.();
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <span className={`${styles.source} ${getSourceStyle(record.answer_source)}`}>
          {getSourceLabel(record.answer_source)}
        </span>
        <span className={styles.time}>{formatTime(record.timestamp)}</span>
        <button 
          className={`${styles.copyBtn} ${copied ? styles.copied : ''}`}
          onClick={handleCopy}
          title="复制"
        >
          {copied ? '已复制' : '复制'}
        </button>
      </div>
      
      <div className={styles.query}>
        <div className={styles.label}>问题</div>
        <div className={styles.content}>{record.query}</div>
      </div>
      
      <div className={styles.answer}>
        <div className={styles.label}>回答</div>
        <div className={styles.content}>{record.answer}</div>
      </div>
      
      <div className={styles.footer}>
        {record.model && <span className={styles.model}>模型: {record.model}</span>}
        <span className={styles.timeCost}>耗时: {record.response_time_ms}ms</span>
      </div>
    </div>
  );
}

export default RecordCard;
