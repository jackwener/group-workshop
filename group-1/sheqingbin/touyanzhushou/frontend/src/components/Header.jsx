/**
 * Header 组件
 * 显示标题和能力状态芯片
 */
import React from 'react';
import './Header.css';

function Header({ capabilities }) {
  const getCapabilityChips = () => {
    const chips = [];
    
    if (capabilities?.copaw_configured) {
      chips.push({
        label: 'CoPaw',
        className: 'chip-copaw',
      });
    }
    
    if (capabilities?.bailian_configured) {
      chips.push({
        label: `百炼 · ${capabilities.bailian_model || '在线'}`,
        className: 'chip-bailian',
      });
    }
    
    if (!capabilities?.copaw_configured && !capabilities?.bailian_configured) {
      chips.push({
        label: '离线演示',
        className: 'chip-demo',
      });
    }
    
    return chips;
  };
  
  const chips = getCapabilityChips();
  
  return (
    <header className="header">
      <div className="header-left">
        <h1 className="header-title">📊 投研问答助手</h1>
      </div>
      <div className="header-right">
        {chips.map((chip, index) => (
          <span key={index} className={`capability-chip ${chip.className}`}>
            {chip.label}
          </span>
        ))}
      </div>
    </header>
  );
}

export default Header;
