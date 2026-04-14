import React from 'react';
import './Header.css';

/**
 * Header组件
 * 显示应用标题和能力状态芯片
 */
function Header({ capabilities }) {
  // 获取能力状态显示
  const getCapabilityChip = () => {
    if (!capabilities) {
      return { text: '加载中...', className: 'chip-loading' };
    }

    if (capabilities.copaw_configured) {
      return { text: 'CoPaw', className: 'chip-copaw' };
    }

    if (capabilities.bailian_configured) {
      const model = capabilities.bailian_model || '百炼';
      return { text: `百炼 · ${model}`, className: 'chip-bailian' };
    }

    return { text: '离线演示', className: 'chip-demo' };
  };

  const chip = getCapabilityChip();

  return (
    <header className="header">
      <div className="header-left">
        <h1 className="header-title">投研问答助手</h1>
      </div>
      <div className="header-center">
        <span className={`capability-chip ${chip.className}`}>
          {chip.text}
        </span>
      </div>
      <div className="header-right">
        {/* 研报管理入口按钮 */}
        <button className="header-btn" title="研报管理">
          📄 研报
        </button>
      </div>
    </header>
  );
}

export default Header;
