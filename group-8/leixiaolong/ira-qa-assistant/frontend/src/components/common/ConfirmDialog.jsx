import styles from './ConfirmDialog.module.css';

export default function ConfirmDialog({ title, message, onConfirm, onCancel }) {
  return (
    <div className={styles.overlay} onClick={onCancel}>
      <div className={styles.dialog} onClick={e => e.stopPropagation()}>
        <div className={styles.title}>{title}</div>
        <div className={styles.message}>{message}</div>
        <div className={styles.actions}>
          <button className={styles.cancelBtn} onClick={onCancel}>取消</button>
          <button className={styles.confirmBtn} onClick={onConfirm}>确认</button>
        </div>
      </div>
    </div>
  );
}
