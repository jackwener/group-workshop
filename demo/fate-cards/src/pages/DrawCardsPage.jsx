import NebulaBg from '../components/ui/NebulaBg';
import TopNavBar from '../components/layout/TopNavBar';
import SideNavBar from '../components/layout/SideNavBar';
import BottomNavBar from '../components/layout/BottomNavBar';
import TarotGrid from '../components/cards/TarotGrid';
import NeonButton from '../components/ui/NeonButton';

export default function DrawCardsPage({ onComplete, selectedCards = [], onCardSelect }) {
  return (
    <div className="relative min-h-screen pb-24 md:pb-0">
      <NebulaBg />
      <TopNavBar />
      <SideNavBar activePage="draw" />

      {/* 主内容 */}
      <main className="md:ml-72 pt-24 px-6">
        {/* 阶段指示徽章 */}
        <div className="inline-block">
          <span className="bg-secondary/10 text-secondary border border-secondary/20 rounded-full px-4 py-1 font-label text-xs uppercase tracking-[0.15em]">
            第一步：揭示过去
          </span>
        </div>

        {/* 主标题 */}
        <h1 className="font-headline text-3xl md:text-4xl font-bold text-on-surface mt-4 mb-8">
          触碰"以太"，提取你的"荒诞记忆"
        </h1>

        {/* 进度指标区 */}
        <div className="flex justify-between items-center mb-6">
          {/* 圆点进度 */}
          <div className="flex items-center gap-2">
            {Array.from({ length: 3 }).map((_, i) => (
              <div
                key={i}
                className={[
                  'w-3 h-3 rounded-full transition-all duration-300',
                  i < selectedCards.length
                    ? 'bg-primary'
                    : 'border border-outline-variant',
                ].join(' ')}
              />
            ))}
          </div>

          {/* 抽卡状态 */}
          <span className="font-label text-tertiary text-sm">
            {selectedCards.length} / 3
          </span>
        </div>

        {/* 卡牌网格 */}
        <TarotGrid
          selectedCards={selectedCards}
          onCardSelect={onCardSelect}
          maxSelections={3}
        />

        {/* 操作按钮区 */}
        <div className="mt-8 text-center">
          <NeonButton
            variant="primary"
            disabled={selectedCards.length < 3}
            onClick={onComplete}
          >
            开启灵觉
          </NeonButton>

          <p className="mt-4 text-on-surface-variant text-sm font-body italic">
            当你凝视卡牌时，卡牌也在凝视你的余额。
          </p>
        </div>
      </main>

      <BottomNavBar activePage="draw" />
    </div>
  );
}
