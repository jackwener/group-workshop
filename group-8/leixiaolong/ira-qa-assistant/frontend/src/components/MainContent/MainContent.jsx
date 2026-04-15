import CommonQuestions from './CommonQuestions';
import ChatHistory from './ChatHistory';
import styles from './MainContent.module.css';

export default function MainContent({
  currentSession,
  records,
  isLoading,
  onQuestionClick,
}) {
  const renderContent = () => {
    // State C: has records
    if (currentSession && (records.length > 0 || isLoading)) {
      return <ChatHistory records={records} isLoading={isLoading} />;
    }
    // State A (no session) / State B (session, no records): show common questions
    return <CommonQuestions onSelect={onQuestionClick} />;
  };

  return (
    <div className={styles.main}>
      <div className={styles.content}>
        {renderContent()}
      </div>
    </div>
  );
}
