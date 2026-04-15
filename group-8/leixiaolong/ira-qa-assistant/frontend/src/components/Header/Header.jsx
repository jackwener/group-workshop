import styles from './Header.module.css';

export default function Header({ capabilities }) {
  const getChipInfo = () => {
    if (!capabilities) return { label: '离线演示模式', className: styles.chipDemo };
    if (capabilities.copaw) return { label: 'CoPaw 已连接', className: styles.chipCopaw };
    if (capabilities.bailian) return { label: `百炼 · ${capabilities.model || 'qwen-max'}`, className: styles.chipBailian };
    return { label: '离线演示模式', className: styles.chipDemo };
  };

  const chip = getChipInfo();

  return (
    <header className={styles.header}>
      <div className={styles.title}>投研问答助手</div>
      <div className={styles.chips}>
        <span className={`${styles.chip} ${chip.className}`}>{chip.label}</span>
      </div>
    </header>
  );
}
