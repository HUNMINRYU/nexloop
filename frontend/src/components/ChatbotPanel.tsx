'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card } from '@/components/ui/Card';
import { sendChatMessage } from '@/lib/api';
import { useChatbotUsage } from '@/hooks/useChatbotUsage';

type MessageRole = 'ai' | 'user';
type ChatCard = {
  title: string;
  bullets: string[];
  cta?: string;
  action?: string;
  url?: string;
};
type Message = {
  id: string;
  role: MessageRole;
  content: string;
  card?: ChatCard;
};

const WELCOME: Message = {
  id: 'welcome',
  role: 'ai',
  content: '반가워요! NEXLOOP AI입니다. 궁금한 트렌드나 분석하고 싶은 데이터가 있으신가요?',
};

const toChatCard = (value: unknown): ChatCard | undefined => {
  if (!value || typeof value !== 'object') return undefined;
  const card = value as { title?: unknown; bullets?: unknown; cta?: unknown; action?: unknown; url?: unknown };
  if (typeof card.title !== 'string' || !Array.isArray(card.bullets)) return undefined;
  return {
    title: card.title,
    bullets: card.bullets.filter((item) => typeof item === 'string') as string[],
    cta: typeof card.cta === 'string' ? card.cta : undefined,
    action: typeof card.action === 'string' ? card.action : undefined,
    url: typeof card.url === 'string' ? card.url : undefined,
  };
};

function ChatBubble({ msg, onCta }: { msg: Message; onCta?: (card: ChatCard) => void }) {
  const isAi = msg.role === 'ai';
  if (msg.card) {
    const card = msg.card;
    const canAct = Boolean(onCta && (msg.card.action || msg.card.url));
    return (
      <Card className="w-full max-w-[90%] rounded-[var(--radius-lg)] p-4 text-left">
        <div className="font-bold text-[var(--color-foreground)] flex items-center gap-2 mb-2">
          <span>💡</span> {card.title}
        </div>
        <p className="text-sm font-semibold text-[var(--color-muted)] mb-2">{msg.content}</p>
        <ul className="list-disc list-inside text-sm font-medium text-[var(--color-muted)] space-y-1 mb-3">
          {card.bullets.map((b, i) => (
            <li key={i}>{b}</li>
          ))}
        </ul>
        {card.cta && (
          <Button
            type="button"
            variant="default"
            onClick={() => (onCta ? onCta(card) : undefined)}
            disabled={!canAct}
            className="text-sm px-4 py-2"
          >
            ◆ {card.cta}
          </Button>
        )}
      </Card>
    );
  }
  return (
    <div className={`flex ${isAi ? 'justify-start' : 'justify-end'} w-full`}>
      <div
        className={`max-w-[85%] rounded-[var(--radius-lg)] border border-[var(--color-border)] px-4 py-3 ${
          isAi ? 'bg-[var(--color-primary)]/10 text-left' : 'bg-[var(--color-primary)]/10 text-right'
        }`}
      >
        <p className="text-sm font-medium text-[var(--color-foreground)] break-words">{msg.content}</p>
      </div>
    </div>
  );
}

type ChatbotPanelProps = {
  onClose: () => void;
  isOpen: boolean;
  onLimitReached?: () => void;
};

export default function ChatbotPanel({ onClose, isOpen, onLimitReached }: ChatbotPanelProps) {
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([WELCOME]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState<string>('');
  const [isSending, setIsSending] = useState(false);
  const listRef = useRef<HTMLDivElement>(null);
  const { hasReachedLimit, incrementUsage, isAuthenticated, remainingMessages } = useChatbotUsage();

  useEffect(() => {
    if (listRef.current) listRef.current.scrollTop = listRef.current.scrollHeight;
  }, [messages]);

  const handleCta = (card: ChatCard) => {
    const actionMap: Record<string, string> = {
      run_pipeline: '/pipeline',
      view_analytics: '/analytics',
      view_storage: '/storage',
    };

    const target = card.action ? actionMap[card.action] : undefined;
    if (target) {
      router.push(target);
      return;
    }

    if (card.url) {
      if (card.url.startsWith('http://') || card.url.startsWith('https://')) {
        window.open(card.url, '_blank', 'noopener,noreferrer');
      } else {
        router.push(card.url);
      }
    }
  };

  const send = async () => {
    const text = input.trim();
    if (!text || isSending) return;

    // Check if non-authenticated user has reached limit
    if (hasReachedLimit) {
      if (onLimitReached) {
        onLimitReached();
      }
      return;
    }

    setInput('');
    const userMsg: Message = { id: `u-${Date.now()}`, role: 'user', content: text };
    setMessages((prev) => [...prev, userMsg]);
    setIsSending(true);

    try {
      const data = await sendChatMessage({ message: text, session_id: sessionId || "" });
      if (data?.session_id && typeof data.session_id === 'string') {
        setSessionId(data.session_id);
      }

      const aiReply: Message = {
        id: `a-${Date.now()}`,
        role: 'ai',
        content: data?.message || '응답을 생성하지 못했습니다.',
        card: toChatCard(data?.card),
      };
      setMessages((prev) => [...prev, aiReply]);

      // Increment usage count for non-authenticated users after successful response
      if (!isAuthenticated) {
        incrementUsage();
      }
    } catch (error) {
      const aiReply: Message = {
        id: `a-${Date.now()}`,
        role: 'ai',
        content: '현재 응답을 가져올 수 없습니다. 잠시 후 다시 시도해 주세요.',
      };
      setMessages((prev) => [...prev, aiReply]);
    } finally {
      setIsSending(false);
    }
  };

  if (!isOpen) return null;

  return (
    <>
      <div
        className="fixed inset-0 bg-black/40 z-[70] md:block"
        onClick={onClose}
        aria-hidden
      />
      <div
        className="fixed z-[71] bg-[var(--color-surface)] border border-[var(--color-border)] shadow-[var(--shadow-soft-lg)] flex flex-col
          right-0 top-20 bottom-4 md:top-24 md:bottom-6 w-full max-w-full md:max-w-[380px] md:right-4 rounded-[var(--radius-xl)]
          transition-transform duration-300 ease-out translate-x-0"
        role="dialog"
        aria-modal
        aria-label="AI 챗봇"
      >
        <header className="flex items-center justify-between border-b border-[var(--color-border)] p-4 bg-[var(--color-foreground)] text-[var(--color-primary-foreground)] shrink-0">
          <div className="flex flex-col">
            <h2 className="text-lg font-bold">AI 챗봇</h2>
            {!isAuthenticated && (
              <p className="text-xs opacity-80">
                {remainingMessages > 0 ? `${remainingMessages}개 질문 남음` : '무료 사용 완료'}
              </p>
            )}
          </div>
          <button
            type="button"
            onClick={onClose}
            className="w-10 h-10 rounded-[var(--radius-sm)] border border-[var(--color-border)] font-bold hover:bg-[var(--color-surface)] hover:text-[var(--color-foreground)] transition-colors flex items-center justify-center"
            aria-label="닫기"
          >
            ×
          </button>
        </header>

        <div
          ref={listRef}
          className="flex-1 overflow-y-auto p-4 space-y-4 min-h-0 bg-white"
        >
          {messages.map((msg) => (
            <ChatBubble key={msg.id} msg={msg} onCta={handleCta} />
          ))}
        </div>

        <div className="p-4 border-t border-[var(--color-border)] bg-[var(--color-surface)] shrink-0">
          <div className="flex gap-2 items-center">
            <button
              type="button"
              className="w-10 h-10 rounded-[var(--radius-md)] border border-[var(--color-border)] flex items-center justify-center shrink-0 hover:bg-[var(--color-secondary)] transition-colors"
              aria-label="첨부"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
              </svg>
            </button>
            <Input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && send()}
              placeholder="메시지를 입력하세요..."
              className="flex-1 min-w-0"
            />
            <Button
              type="button"
              variant="default"
              onClick={send}
              disabled={isSending}
              className="w-10 h-10 shrink-0 p-0"
              aria-label="전송"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="22" y1="2" x2="11" y2="13" />
                <polygon points="22 2 15 22 11 13 2 9 22 2" />
              </svg>
            </Button>
          </div>
        </div>
      </div>
    </>
  );
}
