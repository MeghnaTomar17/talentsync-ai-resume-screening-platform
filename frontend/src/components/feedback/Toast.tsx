import { useCallback, useMemo, useState } from 'react';
import type { ReactNode } from 'react';
import { CheckCircle2, XCircle } from 'lucide-react';
import { ToastContext } from '@/store/toastContext';
import type { ToastType } from '@/store/toastContext';

type Toast = { id: number; title: string; type: ToastType };

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const showToast = useCallback((title: string, type: ToastType = 'success') => {
    const id = Date.now();
    setToasts((current) => [...current, { id, title, type }]);
    window.setTimeout(() => {
      setToasts((current) => current.filter((toast) => toast.id !== id));
    }, 3500);
  }, []);

  const value = useMemo(() => ({ showToast }), [showToast]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="toast-region" aria-live="polite">
        {toasts.map((toast) => (
          <div className={`toast toast-${toast.type}`} key={toast.id}>
            {toast.type === 'success' ? <CheckCircle2 size={18} /> : <XCircle size={18} />}
            <span>{toast.title}</span>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}
