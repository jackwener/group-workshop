/**
 * Toast 提示 Hook
 */
import { useState, useCallback } from 'react';

export function useToast() {
  const [toast, setToast] = useState(null);
  
  const showToast = useCallback((message, type = 'success', duration = 3000) => {
    setToast({ message, type });
    
    setTimeout(() => {
      setToast(null);
    }, duration);
  }, []);
  
  const hideToast = useCallback(() => {
    setToast(null);
  }, []);
  
  return { toast, showToast, hideToast };
}
