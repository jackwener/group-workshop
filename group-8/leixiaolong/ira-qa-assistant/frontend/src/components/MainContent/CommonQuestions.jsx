import styles from './CommonQuestions.module.css';

const QUESTIONS = [
  '半导体行业未来趋势如何？',
  '推荐几只值得关注的消费股',
  '最新新能源研报有什么观点？',
  '人工智能板块投资机会分析',
  '医药行业近期政策影响解读',
  '银行板块估值是否合理？',
];

export default function CommonQuestions({ onSelect }) {
  return (
    <div className={styles.grid}>
      <div className={styles.title}>常见问题，点击快速提问</div>
      {QUESTIONS.map((q, i) => (
        <div key={i} className={styles.card} onClick={() => onSelect(q)}>
          {q}
        </div>
      ))}
    </div>
  );
}
