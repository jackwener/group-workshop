import styles from './EmptyState.module.css';

export default function EmptyState({ onCreate }) {
  return (
    <div className={styles.container}>
      <button className={styles.btn} onClick={onCreate}>
        + 新建会话
      </button>
    </div>
  );
}
