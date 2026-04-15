import { useState } from 'react';
import styles from './ChatArea.module.css';
import RecordCard from './RecordCard';
import { exportSession } from '../services/api';

// 预设问题
const PRESET_QUESTIONS = [
  '分析新能源行业趋势',
  '对比半导体行业研报观点',
  '提取消费行业关键指标',
  '总结医药行业投资逻辑',
];

function ChatArea({ 
  session, 
  records, 
  onAsk, 
  loading, 
  inputArea: InputAreaComponent 
}) {
  const [exporting, setExporting] = useState(false);
  const [exportError, setExportError] = useState('');

  const handleQuestionClick = (question) => {
    onAsk(question);
  };

  const handleExport = async (format) => {
    if (!session || records.length === 0) return;
    
    try {
      setExporting(true);
      setExportError('');
      await exportSession(session.session_id, format);
    } catch (err) {
      setExportError(err.message || '导出失败');
    } finally {
      setExporting(false);
    }
  };

  // 空状态 - 没有选中会话
  if (!session) {
    return (
      <div className={styles.container}>
        <div className={styles.emptyState}>
          <div className={styles.emptyIcon}>💬</div>
          <div className={styles.emptyText}>
            请创建或选择一个会话开始
          </div>
        </div>
      </div>
    );
  }

  // 常见问题状态 - 有会话但没有记录
  if (records.length === 0) {
    return (
      <div className={styles.container}>
        <div className={styles.header}>
          <h2>{session.title}</h2>
          <span className={styles.messageCount}>0 条对话</span>
        </div>
        
        <div className={styles.presetArea}>
          <div className={styles.presetTitle}>你可以问我：</div>
          <div className={styles.presetGrid}>
            {PRESET_QUESTIONS.map((question, index) => (
              <button
                key={index}
                className={styles.presetBtn}
                onClick={() => handleQuestionClick(question)}
                disabled={loading}
              >
                {question}
              </button>
            ))}
          </div>
        </div>
        
        <div className={styles.inputWrapper}>
          <InputAreaComponent onSend={onAsk} loading={loading} disabled={false} />
        </div>
      </div>
    );
  }

  // 对话历史状态
  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2>{session.title}</h2>
        <div className={styles.headerActions}>
          <span className={styles.messageCount}>{records.length} 条对话</span>
          <div className={styles.exportDropdown}>
            <button 
              className={styles.exportBtn}
              disabled={exporting}
            >
              {exporting ? '导出中...' : '导出'}
            </button>
            <div className={styles.exportMenu}>
              <button onClick={() => handleExport('json')}>导出为 JSON</button>
              <button onClick={() => handleExport('txt')}>导出为 TXT</button>
            </div>
          </div>
        </div>
      </div>
      
      {exportError && (
        <div className={styles.exportError}>{exportError}</div>
      )}
      
      <div className={styles.recordsList}>
        {records.map((record) => (
          <RecordCard key={record.id} record={record} />
        ))}
      </div>
      
      <div className={styles.inputWrapper}>
        <InputAreaComponent onSend={onAsk} loading={loading} disabled={false} />
      </div>
    </div>
  );
}

export default ChatArea;
