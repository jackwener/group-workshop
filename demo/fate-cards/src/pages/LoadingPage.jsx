import { useEffect } from 'react';
import { motion } from 'framer-motion';

export default function LoadingPage({ onComplete }) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onComplete?.();
    }, 5000);
    return () => clearTimeout(timer);
  }, [onComplete]);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center relative overflow-hidden bg-background">
      {/* 背景层：星场 */}
      <div
        className="absolute inset-0 opacity-40 pointer-events-none"
        style={{
          backgroundImage:
            'radial-gradient(circle at 2px 2px, rgba(255,255,255,0.05) 1px, transparent 0)',
          backgroundSize: '40px 40px',
        }}
      />
      {/* 背景层：放射状紫色发光 */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background:
            'radial-gradient(circle at 50% 50%, rgba(223,142,255,0.12) 0%, rgba(0,238,252,0.04) 35%, transparent 70%)',
        }}
      />

      {/* 主内容 */}
      <div className="relative z-10 text-center flex flex-col items-center px-6">
        {/* 中心涡旋 */}
        <motion.div
          className="relative flex items-center justify-center w-64 h-64 md:w-80 md:h-80 mb-10"
          initial={{ scale: 0.5, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.8, ease: [0.23, 1, 0.32, 1] }}
        >
          {/* 外层脉冲环 */}
          <div className="absolute inset-0 rounded-full bg-primary/10 animate-ping opacity-20" />

          {/* 外边框容器 */}
          <div
            className="relative w-full h-full rounded-full bg-surface-container-lowest border border-primary/20 flex items-center justify-center overflow-hidden"
            style={{
              boxShadow:
                '0 0 40px rgba(223,142,255,0.25), 0 0 80px rgba(0,238,252,0.1), inset 0 0 40px rgba(223,142,255,0.05)',
            }}
          >
            {/* 内旋转环1 */}
            <div className="absolute inset-4 rounded-full border-t-4 border-l-4 border-primary animate-spin" />
            {/* 内旋转环2（反向）*/}
            <div
              className="absolute inset-8 rounded-full border-b-4 border-r-4 border-secondary"
              style={{ animation: 'spin-reverse 1.5s linear infinite' }}
            />
            {/* 中心图标 */}
            <span
              className="material-symbols-outlined select-none"
              style={{
                fontSize: '56px',
                color: '#df8eff',
                filter: 'drop-shadow(0 0 12px rgba(223,142,255,0.8)) drop-shadow(0 0 24px rgba(223,142,255,0.4))',
              }}
            >
              auto_fix_high
            </span>
          </div>
        </motion.div>

        {/* 浮动饰物 */}
        {/* 左上：超维吐司机 */}
        <motion.div
          className="absolute left-[5%] top-[15%] md:left-[8%] md:top-[10%]"
          style={{ rotate: '-12deg' }}
          animate={{ y: [0, -15, 0] }}
          transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
        >
          <div className="bg-surface-container-low/40 border border-outline-variant/20 rounded-xl px-3 py-2 flex items-center gap-2 text-xs text-on-surface-variant backdrop-blur-sm">
            <span className="material-symbols-outlined" style={{ fontSize: '16px' }}>kitchen</span>
            <span className="font-label">超维吐司机</span>
          </div>
        </motion.div>

        {/* 右下：巡航咸鱼 */}
        <motion.div
          className="absolute right-[5%] bottom-[18%] md:right-[8%] md:bottom-[15%]"
          style={{ rotate: '15deg' }}
          animate={{ y: [0, -15, 0] }}
          transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut', delay: 1 }}
        >
          <div className="bg-surface-container-low/40 border border-outline-variant/20 rounded-xl px-3 py-2 flex items-center gap-2 text-xs text-on-surface-variant backdrop-blur-sm">
            <span className="material-symbols-outlined" style={{ fontSize: '16px' }}>set_meal</span>
            <span className="font-label">巡航咸鱼</span>
          </div>
        </motion.div>

        {/* 右上：casino 图标 */}
        <motion.div
          className="absolute right-[12%] top-[10%] md:right-[15%] md:top-[8%] opacity-40"
          animate={{ y: [0, -15, 0] }}
          transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut', delay: 2 }}
        >
          <span className="material-symbols-outlined" style={{ fontSize: '32px', color: '#00eefc' }}>casino</span>
        </motion.div>

        {/* 文本区 */}
        <motion.div
          className="flex flex-col items-center gap-4"
          initial="hidden"
          animate="visible"
          variants={{
            hidden: {},
            visible: { transition: { staggerChildren: 0.15, delayChildren: 0.5 } },
          }}
        >
          {/* 主标题 */}
          <motion.h1
            className="font-headline text-4xl md:text-5xl font-bold text-on-surface"
            variants={{ hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }}
            style={{
              textShadow: '2px 0 #00eefc, -2px 0 #df8eff',
            }}
          >
            正在连接宇宙服务器...
          </motion.h1>

          {/* 分隔线 */}
          <motion.div
            className="h-[2px] w-12 bg-gradient-to-r from-primary to-secondary mx-auto"
            variants={{ hidden: { opacity: 0, scaleX: 0 }, visible: { opacity: 1, scaleX: 1 } }}
          />

          {/* 副标题 */}
          <motion.p
            className="font-label text-secondary uppercase tracking-[0.2em]"
            variants={{ hidden: { opacity: 0, y: 10 }, visible: { opacity: 1, y: 0 } }}
          >
            命运加载中...
          </motion.p>

          {/* 引言气泡 */}
          <motion.div
            className="bg-surface-container-low/40 border border-outline-variant/20 rounded-full px-6 py-3 font-body text-sm italic text-on-surface-variant backdrop-blur-sm"
            variants={{ hidden: { opacity: 0, y: 10 }, visible: { opacity: 1, y: 0 } }}
          >
            请勿呼吸，以免干扰量子概率场的分散...
          </motion.div>
        </motion.div>

        {/* 进度指标网格 */}
        <motion.div
          className="grid grid-cols-3 gap-8 border-t border-outline-variant/10 pt-8 mt-12 w-full max-w-md"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.2, duration: 0.6 }}
        >
          {/* 业力消耗 */}
          <div className="flex flex-col items-center gap-1">
            <span className="font-label text-xs text-on-surface-variant uppercase tracking-wider">业力消耗</span>
            <span className="font-headline text-lg font-bold text-primary">88.4%</span>
          </div>

          {/* 因果链路 */}
          <div className="flex flex-col items-center gap-1">
            <span className="font-label text-xs text-on-surface-variant uppercase tracking-wider">因果链路</span>
            <div className="flex gap-1 items-center mt-1">
              <span className="w-2 h-2 rounded-full bg-secondary" />
              <span className="w-2 h-2 rounded-full bg-secondary" />
              <span className="w-2 h-2 rounded-full bg-secondary/30 animate-pulse" />
            </div>
          </div>

          {/* 咸鱼饱和度 */}
          <div className="flex flex-col items-center gap-1">
            <span className="font-label text-xs text-on-surface-variant uppercase tracking-wider">咸鱼饱和度</span>
            <span className="font-headline text-lg font-bold text-tertiary">MAX</span>
          </div>
        </motion.div>
      </div>

      {/* 装饰文本：左下角 */}
      <div className="fixed bottom-8 left-8 opacity-5 text-4xl font-headline text-on-surface pointer-events-none select-none">
        FATE.EXE
      </div>

      {/* 装饰文本：右上角 */}
      <div className="fixed top-8 right-8 border border-primary/20 bg-primary/5 rounded-full px-4 py-2 flex items-center gap-2 text-xs font-label text-on-surface-variant backdrop-blur-sm">
        <span className="w-1.5 h-1.5 rounded-full bg-secondary animate-pulse" />
        Ritual in progress
      </div>
    </div>
  );
}
