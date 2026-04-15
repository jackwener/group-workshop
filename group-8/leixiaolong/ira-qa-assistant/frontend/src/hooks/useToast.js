import { useState, useCallback, useRef } from 'react';

export function useToast() {
  const [toastMessage, setToastMessage] = useState(null);
  const timerRef = useRef(null);

  const showToast = useCallback((message) => {
    if (timerRef.current) clearTimeout(timerRef.current);
    setToastMessage(message);
    timerRef.current = setTimeout(() => {
      setToastMessage(null);
      timerRef.current = null;
    }, 3000);
  }, []);

  const hideToast = useCallback(() => {
    if (timerRef.current) clearTimeout(timerRef.current);
    setToastMessage(null);
  }, []);

  return { toastMessage, showToast, hideToast };
}
