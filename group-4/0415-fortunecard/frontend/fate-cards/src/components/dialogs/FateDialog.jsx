import { AnimatePresence, motion } from 'framer-motion';
import GlassPanel from '../ui/GlassPanel';
import NeonButton from '../ui/NeonButton';

export default function FateDialog({ isOpen, onChangeFate, onAcceptFate }) {
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className="fixed inset-0 z-50 flex items-center justify-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          style={{ background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)' }}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1, transition: { type: 'spring', damping: 20, stiffness: 300 } }}
            exit={{ scale: 0.9, opacity: 0 }}
            className="max-w-md w-full mx-4"
          >
            <GlassPanel className="p-8">
              <div className="flex flex-col items-center text-center">
                {/* 图标 */}
                <span className="material-symbols-outlined text-5xl text-primary mb-4 select-none">
                  psychology_alt
                </span>

                {/* 标题 */}
                <h2 className="font-headline text-2xl font-bold text-on-surface">
                  检测到业力波动...
                </h2>
                <h3 className="font-headline text-xl text-on-surface mt-1">
                  你要改命吗？
                </h3>

                {/* 副标题英文 */}
                <p className="font-label text-xs text-on-surface-variant uppercase tracking-[0.3em] mt-2">
                  DO YOU DARE TO CHANGE YOUR FATE?
                </p>

                {/* 按钮区 */}
                <div className="mt-8 space-y-3 w-full">
                  {/* 改命按钮 */}
                  <div className="relative flex justify-center">
                    <NeonButton variant="primary" onClick={onChangeFate} icon="autorenew">
                      逆天改命！
                    </NeonButton>
                    <span className="absolute bottom-0 right-4 text-xs text-tertiary font-label pointer-events-none">
                      发疯值 -50
                    </span>
                  </div>

                  {/* 认命按钮 */}
                  <NeonButton variant="outlined" onClick={onAcceptFate} className="w-full">
                    不改了，认命
                  </NeonButton>
                </div>

                {/* 底部警告 */}
                <div className="flex items-center gap-2 mt-4">
                  <span
                    className="w-2 h-2 rounded-full bg-error"
                    style={{ animation: 'pulse 1.5s infinite' }}
                  />
                  <span className="font-label text-xs text-error/60">
                    命运线极其不稳定
                  </span>
                </div>
              </div>
            </GlassPanel>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
