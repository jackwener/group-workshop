import { useEffect, useRef } from 'react';
import ChatBubble from './ChatBubble';
import LoadingDots from '../common/LoadingDots';
import styles from './ChatHistory.module.css';

export default function ChatHistory({ records, isLoading }) {
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [records, isLoading]);

  return (
    <div className={styles.container}>
      {records.map(record => (
        <ChatBubble key={record.record_id} record={record} />
      ))}
      {isLoading && (
        <div style={{ display: 'flex', justifyContent: 'flex-start', padding: '8px 0' }}>
          <LoadingDots />
        </div>
      )}
      <div ref={endRef} />
    </div>
  );
}
