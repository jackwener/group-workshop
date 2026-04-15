import SourceTag from './SourceTag';
import { formatTime } from '../../utils/formatTime';
import styles from './ChatBubble.module.css';

export default function ChatBubble({ record }) {
  return (
    <div className={styles.pair}>
      <div className={styles.userRow}>
        <div className={`${styles.bubble} ${styles.userBubble}`}>
          {record.query}
        </div>
      </div>
      <div className={styles.aiRow}>
        <div>
          <div className={`${styles.bubble} ${styles.aiBubble}`}>
            {record.answer}
          </div>
          <div className={styles.meta}>
            <SourceTag source={record.answer_source} />
            <span>{record.response_time_ms}ms</span>
            <span>{formatTime(record.timestamp)}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
