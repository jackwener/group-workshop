import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import NebulaBg from '../components/ui/NebulaBg';
import TopNavBar from '../components/layout/TopNavBar';
import SideNavBar from '../components/layout/SideNavBar';
import BottomNavBar from '../components/layout/BottomNavBar';
import NeonButton from '../components/ui/NeonButton';

const diceResults = [
  { label: '1: 命定之虚无', rot: 'rotateX(0deg) rotateY(0deg)' },
  { label: '2: 二元对立', rot: 'rotateX(-90deg) rotateY(0deg)' },
  { label: '3: 三重真理', rot: 'rotateY(-90deg) rotateZ(0deg)' },
  { label: '4: 四大基本力', rot: 'rotateY(90deg) rotateZ(0deg)' },
  { label: '5: 五维震荡', rot: 'rotateX(90deg) rotateY(0deg)' },
  { label: '6: 命运超活跃', rot: 'rotateY(180deg) rotateZ(0deg)' },
];

// 装饰用的占位卡牌网格
const placeholderCards = Array.from({ length: 9 });

export default function DiceRitualPage({ onComplete, onSkip }) {
  const [isRolling, setIsRolling] = useState(false);
  const [diceTransform, setDiceTransform] = useState('rotateX(0deg) rotateY(0deg)');
  const [resultLabel, setResultLabel] = useState(null);
  const [overlayVisible, setOverlayVisible] = useState(true);
  const rollTimerRef = useRef(null);
  const resultTimerRef = useRef(null);
  const completeTimerRef = useRef(null);

  useEffect(() => {
    return () => {
      clearTimeout(rollTimerRef.current);
      clearTimeout(resultTimerRef.current);
      clearTimeout(completeTimerRef.current);
    };
  }, []);

  const handleRoll = () => {
    if (isRolling) return;
    setIsRolling(true);
    setResultLabel(null);
    // 滚动动画：疯转 2 秒
    setDiceTransform('rotateX(720deg) rotateY(720deg) rotateZ(360deg)');

    rollTimerRef.current = setTimeout(() => {
      // 停止，随机结果
      const idx = Math.floor(Math.random() * 6);
      const result = diceResults[idx];
      setDiceTransform(result.rot);
      setIsRolling(false);

      resultTimerRef.current = setTimeout(() => {
        setResultLabel(result.label);
        // 浮层淡出 → 1秒后 onComplete
        completeTimerRef.current = setTimeout(() => {
          setOverlayVisible(false);
          setTimeout(() => {
            onComplete?.();
          }, 1000);
        }, 1200);
      }, 600);
    }, 2000);
  };

  const handleSkip = () => {
    setOverlayVisible(false);
    setTimeout(() => {
      onSkip?.();
    }, 400);
  };

  return (
    <div className="relative min-h-screen bg-background">
      <NebulaBg showScanLines={true} />
      <TopNavBar />
      <SideNavBar activePage="dice" />

      {/* 主内容区：被禁用的卡牌矩阵背景 */}
      <main className="pt-20 pb-24 md:pl-72 min-h-screen flex items-center justify-center px-6">
        <div className="opacity-30 grayscale pointer-events-none select-none">
          <div className="grid grid-cols-3 gap-4">
            {placeholderCards.map((_, i) => (
              <div
                key={i}
                className="w-20 h-28 md:w-28 md:h-40 rounded-2xl border border-outline-variant/20 bg-surface-container-low/30 flex items-center justify-center"
              >
                <span className="material-symbols-outlined text-outline/20" style={{ fontSize: '28px' }}>
                  lock
                </span>
              </div>
            ))}
          </div>
        </div>
      </main>

      {/* 骰子浮层 */}
      <AnimatePresence>
        {overlayVisible && (
          <motion.div
            className="fixed inset-0 z-[60] flex items-center justify-center"
            style={{ backgroundColor: 'rgba(15,13,22,0.80)', backdropFilter: 'blur(12px)' }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.4 }}
          >
            <div className="flex flex-col items-center gap-8 px-6 text-center max-w-lg">
              {/* 文本区 */}
              <motion.div
                className="flex flex-col items-center gap-3"
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
              >
                <h1 className="font-headline text-3xl md:text-4xl font-bold text-on-surface">
                  混沌仪式：扰动量子场
                </h1>
                <p className="font-body text-on-surface-variant max-w-md">
                  在揭示命运之前，你必须通过混沌骰子打破因果的连续性。
                </p>
              </motion.div>

              {/* 3D 骰子 */}
              <motion.div
                className="dice-scene"
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.3, type: 'spring', stiffness: 200, damping: 18 }}
              >
                <div
                  className="dice"
                  style={{
                    transform: diceTransform,
                    transition: isRolling
                      ? 'transform 2s cubic-bezier(0.23, 1, 0.32, 1)'
                      : 'transform 0.8s cubic-bezier(0.23, 1, 0.32, 1)',
                  }}
                >
                  <div className="dice-face dice-face-1">1</div>
                  <div className="dice-face dice-face-2">2</div>
                  <div className="dice-face dice-face-3">3</div>
                  <div className="dice-face dice-face-4">4</div>
                  <div className="dice-face dice-face-5">5</div>
                  <div className="dice-face dice-face-6">6</div>
                </div>
              </motion.div>

              {/* 结果标签 */}
              <AnimatePresence>
                {resultLabel && (
                  <motion.div
                    className="font-headline text-xl font-bold text-primary"
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0 }}
                    style={{ filter: 'drop-shadow(0 0 8px rgba(223,142,255,0.6))' }}
                  >
                    {resultLabel}
                  </motion.div>
                )}
              </AnimatePresence>

              {/* 按钮区 */}
              <motion.div
                className="flex flex-col items-center gap-4"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
              >
                <NeonButton
                  variant="secondary"
                  onClick={handleRoll}
                  disabled={isRolling || resultLabel !== null}
                  icon="casino"
                >
                  投掷以扰动量子场
                </NeonButton>
                <button
                  onClick={handleSkip}
                  className="text-on-surface-variant text-sm hover:text-primary transition-colors cursor-pointer font-label"
                >
                  跳过仪式 →
                </button>
              </motion.div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <BottomNavBar activePage="draw" />
    </div>
  );
}
