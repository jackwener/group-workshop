import { useState, useCallback } from 'react';

const STATES = {
  LOADING: 'loading',
  DICE: 'dice',
  DRAW: 'draw',
  REVEAL: 'reveal',
  REPORT: 'report',
};

export default function useRitualState() {
  const [currentState, setCurrentState] = useState(STATES.LOADING);
  const [selectedCards, setSelectedCards] = useState([]);
  const [diceResult, setDiceResult] = useState(null);
  const [fateChoice, setFateChoice] = useState(null); // 'change' | 'accept'

  const goToNextState = useCallback(() => {
    setCurrentState(prev => {
      switch (prev) {
        case STATES.LOADING: return STATES.DICE;
        case STATES.DICE: return STATES.DRAW;
        case STATES.DRAW: return STATES.REVEAL;
        case STATES.REVEAL: return STATES.REPORT;
        case STATES.REPORT: return STATES.LOADING; // 重新开始
        default: return prev;
      }
    });
  }, []);

  const skipDice = useCallback(() => {
    setCurrentState(STATES.DRAW);
  }, []);

  const selectCard = useCallback((cardIndex) => {
    setSelectedCards(prev => {
      if (prev.includes(cardIndex)) {
        return prev.filter(i => i !== cardIndex);
      }
      if (prev.length >= 3) return prev;
      return [...prev, cardIndex];
    });
  }, []);

  const changeFate = useCallback(() => {
    setFateChoice('change');
    setCurrentState(STATES.REPORT);
  }, []);

  const acceptFate = useCallback(() => {
    setFateChoice('accept');
    setCurrentState(STATES.REPORT);
  }, []);

  const restart = useCallback(() => {
    setCurrentState(STATES.LOADING);
    setSelectedCards([]);
    setDiceResult(null);
    setFateChoice(null);
  }, []);

  return {
    currentState,
    selectedCards,
    diceResult,
    fateChoice,
    goToNextState,
    skipDice,
    selectCard,
    changeFate,
    acceptFate,
    restart,
    setDiceResult,
    STATES,
  };
}
