'use client';

import React, { createContext, useContext, useState, useCallback } from 'react';

type ToastItem = { id: number; message: string; duration?: number };

const ToastContext = createContext<{
  toasts: ToastItem[];
  addToast: (message: string, duration?: number) => void;
} | null>(null);

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used within ToastProvider');
  return ctx;
}

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const addToast = useCallback((message: string, duration = 4000) => {
    const id = Date.now();
    setToasts((prev) => [...prev, { id, message, duration }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, duration);
  }, []);

  return (
    <ToastContext.Provider value={{ toasts, addToast }}>
      {children}
      <div className="fixed bottom-4 left-4 right-4 sm:left-auto sm:right-6 sm:bottom-6 z-[100] flex flex-col gap-2 pointer-events-none max-w-[calc(100vw-2rem)] sm:max-w-sm">
        {toasts.map((t) => (
          <div
            key={t.id}
            className="pointer-events-auto bg-[var(--color-surface)] border border-[var(--color-border)] rounded-[var(--radius-lg)] shadow-[var(--shadow-soft-lg)] px-4 py-3 sm:px-6 sm:py-4"
          >
            <p className="font-medium text-[var(--color-foreground)] text-sm sm:text-base break-words">{t.message}</p>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}
