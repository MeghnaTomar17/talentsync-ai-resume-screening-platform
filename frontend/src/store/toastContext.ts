import { createContext } from 'react';

export type ToastType = 'success' | 'error';

export type ToastContextValue = {
  showToast: (title: string, type?: ToastType) => void;
};

export const ToastContext = createContext<ToastContextValue | undefined>(undefined);
