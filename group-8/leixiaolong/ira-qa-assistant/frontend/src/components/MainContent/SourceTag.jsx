const SOURCE_CONFIG = {
  copaw: { label: 'CoPaw', color: '#1a73e8', bg: '#e8f0fe' },
  bailian: { label: '百炼', color: '#0d9d58', bg: '#e6f4ea' },
  demo: { label: '离线演示', color: '#9aa0a6', bg: '#f1f3f4' },
};

export default function SourceTag({ source }) {
  const config = SOURCE_CONFIG[source] || SOURCE_CONFIG.demo;
  return (
    <span
      style={{
        display: 'inline-block',
        padding: '2px 8px',
        borderRadius: '10px',
        fontSize: '11px',
        fontWeight: 500,
        color: config.color,
        background: config.bg,
      }}
    >
      {config.label}
    </span>
  );
}
