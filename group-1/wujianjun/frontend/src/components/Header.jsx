function Header({ capabilities }) {
  const getModeText = () => {
    if (!capabilities) return '加载中...'
    switch (capabilities.mode) {
      case 'copaw':
        return 'CoPaw'
      case 'bailian':
        return '百炼'
      case 'demo':
        return '离线演示'
      default:
        return '未知'
    }
  }

  const getModeClass = () => {
    if (!capabilities) return ''
    return capabilities.mode
  }

  return (
    <header className="header">
      <div className="header-title">投研智能问答助手</div>
      <div className={`capability-chip ${getModeClass()}`}>
        {getModeText()}
      </div>
    </header>
  )
}

export default Header
