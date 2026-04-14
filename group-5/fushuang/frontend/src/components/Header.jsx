function Header({ caps }) {
  const getChipClass = () => {
    if (caps.copaw_configured) return 'chip chip-green'
    if (caps.bailian_configured) return 'chip chip-blue'
    return 'chip chip-gray'
  }

  const getChipText = () => {
    if (caps.copaw_configured) return 'CoPaw 桥接'
    if (caps.bailian_configured) return `百炼 · ${caps.model || 'default'}`
    return '离线演示'
  }

  return (
    <header className="header">
      <div className="header-title">研报智能分析助手</div>
      <div className="header-chips">
        <span className={getChipClass()}>{getChipText()}</span>
      </div>
    </header>
  )
}

export default Header
