import TarotCard from './TarotCard';

export default function TarotGrid({ selectedCards = [], onCardSelect, maxSelections = 3, isLocked = false }) {
  const handleCardClick = (index) => {
    if (isLocked) return;

    const alreadySelected = selectedCards.includes(index);

    if (alreadySelected) {
      // 取消选择
      onCardSelect(selectedCards.filter((i) => i !== index));
    } else if (selectedCards.length < maxSelections) {
      // 选中新卡
      onCardSelect([...selectedCards, index]);
    }
    // 已达上限且未选中 → 不处理
  };

  return (
    <div className="grid grid-cols-3 gap-4 max-w-md mx-auto">
      {Array.from({ length: 9 }).map((_, index) => {
        const isSelected = selectedCards.includes(index);
        const isCardLocked =
          isLocked || (!isSelected && selectedCards.length >= maxSelections);

        return (
          <TarotCard
            key={index}
            index={index}
            isSelected={isSelected}
            isLocked={isCardLocked}
            onClick={handleCardClick}
          />
        );
      })}
    </div>
  );
}
