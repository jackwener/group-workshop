import styles from './Header.module.css';
import SystemMonitor from './SystemMonitor';

function Header({ capabilities }) {
  return (
    <header className={styles.header}>
      <div className={styles.title}>投研问答助手</div>
      <div className={styles.headerRight}>
        <div className={styles.chips}>
        {capabilities && (
          <>
            {capabilities.copaw_configured && (
              <span className={`${styles.chip} ${styles.chipCopaw}`}>
                CoPaw 桥接
              </span>
            )}
            {capabilities.bailian_configured && (
              <span className={`${styles.chip} ${styles.chipBailian}`}>
                百炼 · {capabilities.bailian_model || '默认'}
              </span>
            )}
            {!capabilities.copaw_configured && !capabilities.bailian_configured && (
              <span className={`${styles.chip} ${styles.chipDemo}`}>
                离线演示
              </span>
            )}
          </>
        )}
        </div>
        <SystemMonitor />
      </div>
    </header>
  );
}

export default Header;
