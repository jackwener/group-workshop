/**
 * Toast 组件
 * 全局提示消息
 */
import React from 'react';

function Toast({ message, type = 'success', onClose }) {
  if (!message) return null;
  
  return (
    <div className={`toast toast-${type}`} onClick={onClose}>
      {message}
    </div>
  );
}

export default Toast;
