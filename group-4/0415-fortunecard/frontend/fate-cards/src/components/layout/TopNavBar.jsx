export default function TopNavBar() {
  return (
    <nav className="fixed top-0 left-0 w-full z-50 bg-slate-950/80 backdrop-blur-xl border-b border-white/5">
      <div className="flex justify-between items-center px-6 py-4 md:pl-80">
        {/* Logo */}
        <span
          className="text-2xl font-bold tracking-tighter text-purple-400 font-headline"
          style={{ filter: 'drop-shadow(0 0 8px rgba(223,142,255,0.6))' }}
        >
          沙雕塔罗
        </span>

        {/* 右侧图标区 */}
        <div className="flex items-center gap-4">
          <span className="material-symbols-outlined text-on-surface-variant hover:text-primary hover:scale-110 transition-transform cursor-pointer select-none">
            auto_fix_high
          </span>
          <span className="material-symbols-outlined text-on-surface-variant hover:text-primary hover:scale-110 transition-transform cursor-pointer select-none">
            settings
          </span>
        </div>
      </div>
    </nav>
  );
}
