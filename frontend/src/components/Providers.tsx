'use client';

import React, { useEffect, useState } from 'react';
import { usePathname } from 'next/navigation';
import { ToastProvider } from '@/components/ui';
import ChatbotWidget from '@/components/ChatbotWidget';
import AuthGate from '@/components/AuthGate';

import QueryProvider from '@/providers/QueryProvider';

export default function Providers({ children }: { children: React.ReactNode }) {
  const [showChatbot, setShowChatbot] = useState(false);
  const pathname = usePathname();

  useEffect(() => {
    if (typeof window === 'undefined') return;
    // Always show chatbot for all users (authenticated and non-authenticated)
    setShowChatbot(true);
  }, [pathname]);

  return (
    <QueryProvider>
      <ToastProvider>
        <AuthGate>
          {children}
          {showChatbot && <ChatbotWidget />}
        </AuthGate>
      </ToastProvider>
    </QueryProvider>
  );
}
