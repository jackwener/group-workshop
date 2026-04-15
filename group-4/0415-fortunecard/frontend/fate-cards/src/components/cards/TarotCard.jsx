import { useState } from 'react';

export default function TarotCard({ index, isSelected, isLocked, onClick }) {
  const [hovered, setHovered] = useState(false);

  const handleClick = () => {
    if (!isLocked) {
      onClick(index);
    }
  };

  const containerStyle = {
    transformStyle: 'preserve-3d',
    transition: 'transform 0.6s cubic-bezier(0.23, 1, 0.32, 1)',
    transform:
      !isLocked && hovered
        ? 'rotateY(10deg) rotateX(10deg) translateZ(20px)'
        : isSelected
        ? 'scale(0.95)'
        : 'none',
  };

  const textureStyle = {
    background: `
      repeating-linear-gradient(30deg, rgba(223,142,255,0.1) 0px, transparent 1px, transparent 40px),
      repeating-linear-gradient(150deg, rgba(0,238,252,0.05) 0px, transparent 1px, transparent 40px),
      repeating-linear-gradient(60deg, rgba(223,142,255,0.05) 0px, transparent 1px, transparent 70px)
    `,
    backgroundSize: '40px 70px',
  };

  return (
    <div
      className={[
        'aspect-[2/3] rounded-2xl overflow-hidden shadow-2xl',
        isLocked ? 'opacity-50 grayscale cursor-not-allowed' : 'cursor-pointer',
        isSelected
          ? 'border border-primary/40 shadow-[0_0_30px_rgba(223,142,255,0.4)]'
          : 'border border-white/10 bg-surface-container-highest',
      ].join(' ')}
      style={containerStyle}
      onClick={handleClick}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      {/* 卡背纹理 */}
      <div className="w-full h-full flex items-center justify-center relative" style={textureStyle}>
        {/* 中心装饰 */}
        <div
          className={[
            'w-16 h-16 rounded-full border-2 flex items-center justify-center transition-all duration-300',
            hovered && !isLocked ? 'border-primary/60' : 'border-white/20',
          ].join(' ')}
        >
          <div
            className={[
              'w-12 h-12 rounded-full border flex items-center justify-center transition-all duration-300',
              hovered && !isLocked ? 'border-primary/40' : 'border-white/10',
            ].join(' ')}
          >
            <span
              className={[
                'material-symbols-outlined text-2xl transition-transform duration-300 select-none',
                hovered && !isLocked ? 'scale-125 text-primary' : 'text-primary',
              ].join(' ')}
            >
              vertex_cluster
            </span>
          </div>
        </div>

        {/* 选中光晕 */}
        {isSelected && (
          <div className="absolute inset-0 bg-primary/5 pointer-events-none" />
        )}
      </div>
    </div>
  );
}
