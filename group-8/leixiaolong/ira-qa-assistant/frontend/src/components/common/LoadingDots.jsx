import styles from './LoadingDots.module.css';

export default function LoadingDots() {
  return (
    <span className={styles.dots}>
      <span>.</span><span>.</span><span>.</span>
    </span>
  );
}
