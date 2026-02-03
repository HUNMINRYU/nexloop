'use client';

import React, { useState } from 'react';
import ChatbotPanel from './ChatbotPanel';
import { useChatbotUsage } from '@/hooks/useChatbotUsage';

function ChatbotIcon() {
  return (
    <svg width="48" height="48" viewBox="0 0 48 48" fill="none" className="w-full h-full" aria-hidden>
      {/* 말풍선: 둥근 사각 + 좌하단 꼬리 */}
      <path
        d="M12 8h24a4 4 0 0 1 4 4v16a4 4 0 0 1-4 4h-4l-4 6-4-6h-12a4 4 0 0 1-4-4V12a4 4 0 0 1 4-4z"
        fill="var(--color-primary)"
        stroke="black"
        strokeWidth="2.5"
        strokeLinejoin="round"
      />
      {/* 로봇 머리 (흰 원) */}
      <circle cx="24" cy="22" r="10" fill="white" stroke="black" strokeWidth="2" />
      {/* 눈: 큰 원 + 동공 + 하이라이트 */}
      <circle cx="19" cy="20" r="3.5" fill="white" stroke="black" strokeWidth="1.5" />
      <circle cx="19.5" cy="19.5" r="1.5" fill="black" />
      <circle cx="20.2" cy="18.8" r="0.4" fill="white" />
      <circle cx="29" cy="20" r="3.5" fill="white" stroke="black" strokeWidth="1.5" />
      <circle cx="29.5" cy="19.5" r="1.5" fill="black" />
      <circle cx="30.2" cy="18.8" r="0.4" fill="white" />
      {/* 미소 */}
      <path
        d="M18 26q3 2 6 0"
        stroke="black"
        strokeWidth="1.5"
        strokeLinecap="round"
        fill="none"
      />
      {/* 안테나 + 끝 구 */}
      <path d="M24 12v-5" stroke="black" strokeWidth="2" strokeLinecap="round" />
      <circle cx="24" cy="6" r="2.5" fill="white" stroke="black" strokeWidth="1.5" />
    </svg>
  );
}

export default function ChatbotWidget() {
  const [open, setOpen] = useState(false);
  const [showLeadCapture, setShowLeadCapture] = useState(false);
  const { isAuthenticated, remainingMessages } = useChatbotUsage();

  const handleLimitReached = () => {
    setShowLeadCapture(true);
  };

  return (
    <>
      <div className="fixed bottom-6 right-6 z-[60]">
        <button
          type="button"
          onClick={() => setOpen(true)}
          className="relative w-14 h-14 md:w-16 md:h-16 rounded-[var(--radius-xl)] border border-[var(--color-border)] bg-[var(--color-surface)] shadow-[var(--shadow-soft-lg)] flex items-center justify-center hover:translate-x-[-2px] hover:translate-y-[-2px] hover:shadow-[var(--shadow-soft-lg)] transition-all focus:outline-none focus:ring-2 focus:ring-[var(--color-ring)] focus:ring-offset-2"
          aria-label="AI 챗봇 열기"
        >
          <span className="w-10 h-10 md:w-12 md:h-12 block">
            <ChatbotIcon />
          </span>
          {!isAuthenticated && remainingMessages > 0 && (
            <span className="absolute -top-2 -right-2 bg-[var(--color-primary)] text-white text-xs font-bold px-2 py-1 rounded-full shadow-md">
              {remainingMessages}
            </span>
          )}
        </button>
      </div>
      <ChatbotPanel
        isOpen={open}
        onClose={() => setOpen(false)}
        onLimitReached={handleLimitReached}
      />
      {showLeadCapture && (
        <div className="fixed inset-0 z-[80] flex items-center justify-center">
          <div
            className="absolute inset-0 bg-black/40"
            onClick={() => setShowLeadCapture(false)}
          />
          <div className="relative z-10 bg-white rounded-2xl p-8 max-w-md mx-4 shadow-2xl">
            <h3 className="text-2xl font-bold mb-4">더 많은 질문이 필요하신가요?</h3>
            <p className="text-slate-600 mb-6">
              무료 체험이 종료되었습니다. 계속해서 AI 챗봇을 이용하시려면 회원가입하거나 이메일을 남겨주세요.
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => {
                  setShowLeadCapture(false);
                  window.location.href = '/signup';
                }}
                className="flex-1 bg-[var(--color-primary)] text-white font-bold py-3 px-6 rounded-xl hover:bg-[var(--color-primary)]/90 transition-colors"
              >
                회원가입
              </button>
              <button
                onClick={() => setShowLeadCapture(false)}
                className="flex-1 border border-slate-300 text-slate-700 font-bold py-3 px-6 rounded-xl hover:bg-slate-50 transition-colors"
              >
                닫기
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
