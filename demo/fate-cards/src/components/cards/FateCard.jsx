import { useState } from 'react';

const phaseConfig = {
  past: {
    label: '过去 / PAST',
    labelColor: 'text-on-surface-variant',
    borderClass: 'border-white/5',
    extraClass: 'rotate-[-8deg]',
    gradientFrom: 'from-slate-800',
    gradientTo: 'to-slate-700',
  },
  present: {
    label: '现在 / PRESENT',
    labelColor: 'text-secondary',
    borderClass: 'border-secondary/20',
    extraClass: 'scale-105 z-10',
    shadowStyle: '0 0 30px rgba(0,238,252,0.15)',
    gradientFrom: 'from-cyan-900/50',
    gradientTo: 'to-slate-800',
  },
  future: {
    label: '未来 / FUTURE',
    labelColor: 'text-primary',
    borderClass: 'border-primary/20',
    extraClass: 'rotate-[8deg]',
    shadowStyle: '0 0 40px rgba(223,142,255,0.2)',
    gradientFrom: 'from-purple-900/50',
    gradientTo: 'to-slate-800',
  },
};

const rarityConfig = {
  普通: {
    className: 'bg-slate-700 text-slate-200',
    label: '普通',
  },
  稀有: {
    className: 'bg-secondary/20 text-secondary border border-secondary/40',
    label: '稀有',
  },
  传说: {
    className: 'bg-primary/20 text-primary border border-primary/40',
    label: '传说',
  },
};

export default function FateCard({ phase, name, description, rarity = '普通', imageIndex }) {
  const [hovered, setHovered] = useState(false);
  const config = phaseConfig[phase] || phaseConfig.past;
  const rarityStyle = rarityConfig[rarity] || rarityConfig['普通'];

  const cardStyle = {
    transformStyle: 'preserve-3d',
    transition: 'transform 0.4s ease',
    transform: hovered ? 'rotateY(5deg) rotateX(-5deg)' : 'none',
    boxShadow: config.shadowStyle || undefined,
  };

  return (
    <div
      className={[
        'w-48 h-72 md:w-56 md:h-80 rounded-2xl overflow-hidden relative',
        'bg-surface-container-high border',
        config.borderClass,
        config.extraClass,
      ].join(' ')}
      style={cardStyle}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      {/* 上半部分 - 图像区域 */}
      <div
        className={[
          'h-1/2 w-full bg-gradient-to-br relative',
          config.gradientFrom,
          config.gradientTo,
        ].join(' ')}
      >
        {/* 稀有度徽章 */}
        <div className="absolute top-2 right-2">
          <span
            className={[
              'text-xs font-label px-2 py-0.5 rounded-full',
              rarityStyle.className,
            ].join(' ')}
          >
            {rarityStyle.label}
          </span>
        </div>

        {/* 装饰图案 */}
        <div className="absolute inset-0 flex items-center justify-center opacity-20">
          <span className="material-symbols-outlined text-6xl text-white select-none">
            auto_awesome
          </span>
        </div>
      </div>

      {/* 下半部分 - 文字区域 */}
      <div className="p-4 h-1/2 flex flex-col justify-start">
        {/* 阶段标签 */}
        <span
          className={[
            'font-label text-xs uppercase tracking-[0.15em]',
            config.labelColor,
          ].join(' ')}
        >
          {config.label}
        </span>

        {/* 卡牌名称 */}
        <h3 className="font-headline text-lg font-bold text-on-surface mt-1 leading-tight">
          {name}
        </h3>

        {/* 描述 */}
        <p className="font-body text-xs text-on-surface-variant mt-2 line-clamp-2 leading-relaxed">
          {description}
        </p>
      </div>
    </div>
  );
}
