function Header({ capabilities }) {
  const { copaw_configured, bailian_configured, bailian_model } = capabilities || {}

  return (
    <header className="bg-gradient-to-r from-navy-900 to-navy-800 px-6 py-3.5 flex items-center justify-between">
      {/* 品牌区 */}
      <div className="flex items-center space-x-3">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-400 to-brand-600 flex items-center justify-center shadow-glow">
          <span className="text-white font-serif font-bold text-sm">M4</span>
        </div>
        <div>
          <h1 className="text-base font-semibold text-white tracking-tight">研报聚合分析助手</h1>
          <p className="text-[10px] text-slate-400 tracking-widest uppercase">M4-RA Intelligence Platform</p>
        </div>
      </div>

      {/* 状态指示器 */}
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2 bg-white/5 rounded-full px-3 py-1.5 border border-white/10">
          <span className={`status-dot ${copaw_configured ? 'bg-emerald-400' : 'bg-slate-500'}`} />
          <span className="text-xs text-slate-300 font-medium">CoPaw</span>
        </div>
        <div className="flex items-center space-x-2 bg-white/5 rounded-full px-3 py-1.5 border border-white/10">
          <span className={`status-dot ${bailian_configured ? 'bg-emerald-400' : 'bg-slate-500'}`} />
          <span className="text-xs text-slate-300 font-medium">百炼</span>
          {bailian_configured && bailian_model && (
            <span className="text-[10px] text-brand-400 font-mono">{bailian_model}</span>
          )}
        </div>
      </div>
    </header>
  )
}

export default Header
