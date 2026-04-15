const menuItems = [
  { icon: 'auto_stories', label: '命运之书', key: 'draw' },
  { icon: 'casino', label: '混沌祭坛', key: 'dice' },
  { icon: 'photo_library', label: '荒诞图鉴', key: 'gallery' },
  { icon: 'settings', label: '因果设置', key: 'settings' },
];

export default function SideNavBar({ activePage }) {
  return (
    <aside className="hidden md:flex flex-col fixed left-0 top-0 bottom-0 z-50 w-72 bg-slate-950/80 backdrop-blur-xl border-r border-white/10 shadow-[20px_0_50px_rgba(15,13,22,0.8)] pt-8 pb-6 px-6">
      {/* Logo 区 */}
      <div className="flex items-center gap-2 mb-2">
        <span className="material-symbols-outlined text-primary">auto_stories</span>
        <span className="font-headline text-xl font-bold text-primary">沙雕祭司</span>
      </div>

      {/* 业力指示 */}
      <p className="font-label text-xs text-on-surface-variant uppercase tracking-[0.2em] mb-8">
        当前业力：极高
      </p>

      {/* 菜单项 */}
      <nav className="flex flex-col gap-1">
        {menuItems.map((item) => {
          const isActive = activePage === item.key;
          return (
            <div
              key={item.key}
              className={
                'flex items-center gap-3 px-4 py-3 rounded-xl transition-all cursor-pointer ' +
                (isActive
                  ? 'bg-cyan-400/10 border-r-2 border-cyan-400 text-cyan-400'
                  : 'text-on-surface-variant hover:bg-white/5 hover:text-white')
              }
            >
              <span className="material-symbols-outlined text-[20px]">{item.icon}</span>
              <span className="font-label text-sm font-medium">{item.label}</span>
            </div>
          );
        })}
      </nav>

      {/* 底部按钮 */}
      <button className="mt-auto w-full py-3 rounded-full border border-outline-variant/30 text-on-surface-variant font-label text-sm hover:bg-white/5 hover:text-white transition-all cursor-pointer">
        查看改命记录
      </button>
    </aside>
  );
}
