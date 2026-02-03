'use client';

import React, { useEffect } from 'react';

type DrawerProps = {
  open: boolean;
  onClose: () => void;
  side?: 'left' | 'right';
  title?: string;
  children: React.ReactNode;
};

export default function Drawer({ open, onClose, side = 'right', title, children }: DrawerProps) {
  useEffect(() => {
    if (open) document.body.style.overflow = 'hidden';
    return () => { document.body.style.overflow = ''; };
  }, [open]);

  const isLeft = side === 'left';

  return (
    <>
      {open && (
        <div
          className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-[110]"
          onClick={onClose}
          aria-hidden
        />
      )}
      <div
        className={`fixed top-0 ${isLeft ? 'left-0' : 'right-0'} h-[100dvh] w-[280px] bg-white z-[999] shadow-2xl transition-transform duration-300 ease-in-out border-l border-slate-100 flex flex-col ${
          open ? 'translate-x-0' : isLeft ? '-translate-x-full' : 'translate-x-full'
        }`}
        role="dialog"
        aria-modal
      >
        <div className="flex-none flex items-center justify-between border-b border-slate-100 p-5">
          {title && (
            <div className="text-xl font-black tracking-tighter text-slate-900">
                NEX<span className="text-[#0ca678]">LOOP</span>
            </div>
          )}
          <button
            type="button"
            onClick={onClose}
            className="p-2 -mr-2 text-slate-500 hover:text-slate-900 transition-colors"
            aria-label="닫기"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-6">{children}</div>
      </div>
    </>
  );
}
