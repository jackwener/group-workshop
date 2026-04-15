import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import NebulaBg from '../components/ui/NebulaBg';
import TopNavBar from '../components/layout/TopNavBar';
import SideNavBar from '../components/layout/SideNavBar';
import BottomNavBar from '../components/layout/BottomNavBar';
import FateCard from '../components/cards/FateCard';
import FateDialog from '../components/dialogs/FateDialog';

const fateCards = [
  {
    phase: 'past',
    name: '咸鱼翻身失败',
    description: '翻了个身，还是咸鱼。',
    rarity: '普通',
  },
  {
    phase: 'present',
    name: '疯狂摸鱼中',
    description: '鱼没摸到，水被搅浑了。',
    rarity: '稀有',
  },
  {
    phase: 'future',
    name: '宇宙级摆烂',
    description: '万物归寂，我亦不动。',
    rarity: '传说',
  },
];

const containerVariants = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: 0.3,
    },
  },
};

const cardVariants = {
  hidden: { y: 100, opacity: 0, rotateY: 180 },
  visible: {
    y: 0,
    opacity: 1,
    rotateY: 0,
    transition: {
      type: 'spring',
      damping: 20,
      stiffness: 100,
      duration: 0.8,
    },
  },
};

export default function RevealPage({ selectedCards, onChangeFate, onAcceptFate }) {
  const [showDialog, setShowDialog] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setShowDialog(true);
    }, 2000);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="relative min-h-screen">
      <NebulaBg />
      <TopNavBar />
      <SideNavBar activePage="draw" />

      {/* 主内容 */}
      <main className="md:ml-72 flex items-center justify-center min-h-screen">
        {/* 三卡展示区 */}
        <motion.div
          className="flex items-center justify-center gap-4 md:gap-8 px-6"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          style={{ perspective: '1000px' }}
        >
          {fateCards.map((card) => (
            <motion.div key={card.phase} variants={cardVariants} style={{ transformStyle: 'preserve-3d' }}>
              <FateCard
                phase={card.phase}
                name={card.name}
                description={card.description}
                rarity={card.rarity}
              />
            </motion.div>
          ))}
        </motion.div>
      </main>

      {/* 改命对话框 */}
      <FateDialog
        isOpen={showDialog}
        onChangeFate={onChangeFate}
        onAcceptFate={onAcceptFate}
      />

      <BottomNavBar activePage="draw" />
    </div>
  );
}
