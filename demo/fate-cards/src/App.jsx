import { AnimatePresence, motion } from 'framer-motion';
import useRitualState from './hooks/useRitualState';
import LoadingPage from './pages/LoadingPage';
import DiceRitualPage from './pages/DiceRitualPage';
import DrawCardsPage from './pages/DrawCardsPage';
import RevealPage from './pages/RevealPage';
import ReportPage from './pages/ReportPage';

const pageTransition = { initial: { opacity: 0 }, animate: { opacity: 1 }, exit: { opacity: 0 } };

export default function App() {
  const {
    currentState,
    selectedCards,
    fateChoice,
    goToNextState,
    skipDice,
    selectCard,
    changeFate,
    acceptFate,
    restart,
    STATES,
  } = useRitualState();

  return (
    <div className="bg-background text-on-surface min-h-screen">
      <AnimatePresence mode="wait">
        {currentState === STATES.LOADING && (
          <motion.div key="loading" {...pageTransition}>
            <LoadingPage onComplete={goToNextState} />
          </motion.div>
        )}
        {currentState === STATES.DICE && (
          <motion.div key="dice" {...pageTransition}>
            <DiceRitualPage onComplete={goToNextState} onSkip={skipDice} />
          </motion.div>
        )}
        {currentState === STATES.DRAW && (
          <motion.div key="draw" {...pageTransition}>
            <DrawCardsPage
              onComplete={goToNextState}
              selectedCards={selectedCards}
              onCardSelect={selectCard}
            />
          </motion.div>
        )}
        {currentState === STATES.REVEAL && (
          <motion.div key="reveal" {...pageTransition}>
            <RevealPage
              selectedCards={selectedCards}
              onChangeFate={changeFate}
              onAcceptFate={acceptFate}
            />
          </motion.div>
        )}
        {currentState === STATES.REPORT && (
          <motion.div key="report" {...pageTransition}>
            <ReportPage
              selectedCards={selectedCards}
              fateChoice={fateChoice}
              onRestart={restart}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
