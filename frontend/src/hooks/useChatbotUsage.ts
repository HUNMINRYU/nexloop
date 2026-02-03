'use client';

import { useState, useEffect } from 'react';

const CHATBOT_USAGE_KEY = 'chatbot_usage';
const MAX_FREE_MESSAGES = 3;

export function useChatbotUsage() {
  const [usageCount, setUsageCount] = useState<number>(0);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    // Check authentication status
    const token = sessionStorage.getItem('auth_token');
    setIsAuthenticated(Boolean(token));

    // Load usage count for non-authenticated users
    if (!token) {
      const count = parseInt(localStorage.getItem(CHATBOT_USAGE_KEY) || '0', 10);
      setUsageCount(count);
    }
  }, []);

  const incrementUsage = () => {
    if (isAuthenticated) return; // No limit for authenticated users

    const newCount = usageCount + 1;
    setUsageCount(newCount);
    localStorage.setItem(CHATBOT_USAGE_KEY, String(newCount));
  };

  const resetUsage = () => {
    setUsageCount(0);
    localStorage.removeItem(CHATBOT_USAGE_KEY);
  };

  const hasReachedLimit = !isAuthenticated && usageCount >= MAX_FREE_MESSAGES;
  const remainingMessages = isAuthenticated ? Infinity : Math.max(0, MAX_FREE_MESSAGES - usageCount);

  return {
    usageCount,
    isAuthenticated,
    hasReachedLimit,
    remainingMessages,
    incrementUsage,
    resetUsage,
    MAX_FREE_MESSAGES,
  };
}
