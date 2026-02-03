'use client';

import React, { useEffect } from 'react';

type ModalProps = {
  open: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
};

export default function Modal({ open, onClose, title, children }: ModalProps) {
  useEffect(() => {
    if (open) document.body.style.overflow = 'hidden';
    return () => { document.body.style.overflow = ''; };
  }, [open]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-[90] flex items-center justify-center p-4">
      <div
        className="absolute inset-0 bg-black/50"
        onClick={onClose}
        aria-hidden
      />
      <div
        className="relative bg-[var(--color-surface)] rounded-[var(--radius-lg)] shadow-[var(--shadow-soft-lg)] border border-[var(--color-border)] max-w-md w-full max-h-[90vh] overflow-auto"
        role="dialog"
        aria-modal
        aria-labelledby={title ? 'modal-title' : undefined}
      >
        {title && (
          <div className="flex items-center justify-between border-b border-[var(--color-border)] p-4">
            <h2 id="modal-title" className="text-xl font-semibold text-[var(--color-foreground)]">{title}</h2>
            <button
              type="button"
              onClick={onClose}
              className="w-10 h-10 rounded-[var(--radius-md)] border border-[var(--color-border)] bg-[var(--color-secondary)] font-semibold hover:bg-[var(--color-border)] transition-colors"
              aria-label="닫기"
            >
              ×
            </button>
          </div>
        )}
        <div className="p-6">{children}</div>
      </div>
    </div>
  );
}
