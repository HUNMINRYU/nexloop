'use client';

import React from 'react';

type PersonWithBubbleProps = {
  /** 말풍선 안 텍스트 */
  text: string;
  /** 말풍선 위치: 'above' = 흰 박스 위(아이콘 아래), 'below' = 흰 박스 아래(아이콘 위) */
  position: 'above' | 'below';
  /** 아이콘·말풍선 정렬: 패널 내 왼쪽/오른쪽 */
  align?: 'left' | 'right';
};

/** 사람 모양 아이콘 (머리+어깨 실루엣) */
function PersonIcon({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 32"
      className={className ?? 'w-10 h-10'}
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
    >
      <circle cx="12" cy="8" r="5" />
      <path d="M4 30c0-5 4-8 8-8s8 3 8 8" />
    </svg>
  );
}

export default function PersonWithBubble({ text, position, align = 'left' }: PersonWithBubbleProps) {
  const isAbove = position === 'above';
  const isRight = align === 'right';

  return (
    <div className={`flex flex-col gap-2 ${isRight ? 'items-end' : 'items-start'}`}>
      {isAbove ? (
        <>
          <div className="relative rounded-[var(--radius-lg)] border border-[var(--color-border)] bg-[var(--color-surface)] px-4 py-3 shadow-[var(--shadow-soft-md)] w-full max-w-[220px] min-w-0 min-h-[96px] flex items-center">
            <p className="text-sm font-medium text-[var(--color-foreground)] break-words leading-snug">{text}</p>
            <div
              className="absolute left-1/2 -translate-x-1/2 -bottom-3 w-0 h-0 border-l-8 border-r-8 border-t-8 border-l-transparent border-r-transparent border-t-[var(--color-border)]"
              aria-hidden
            />
          </div>
          <PersonIcon className="w-10 h-10 text-[var(--color-foreground)]" />
        </>
      ) : (
        <>
          <PersonIcon className="w-10 h-10 text-[var(--color-foreground)]" />
          <div className="relative rounded-[var(--radius-lg)] border border-[var(--color-border)] bg-[var(--color-surface)] px-4 py-3 shadow-[var(--shadow-soft-md)] w-full max-w-[220px] min-w-0 min-h-[96px] flex items-center">
            <p className="text-sm font-medium text-[var(--color-foreground)] break-words leading-snug">{text}</p>
            <div
              className="absolute left-1/2 -translate-x-1/2 -top-3 w-0 h-0 border-l-8 border-r-8 border-b-8 border-l-transparent border-r-transparent border-b-[var(--color-border)]"
              aria-hidden
            />
          </div>
        </>
      )}
    </div>
  );
}
