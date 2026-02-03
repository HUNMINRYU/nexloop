'use client';

import { useState, useEffect } from 'react';
import { Button, Card } from '@/components/ui';
import { fetchCacheStats } from '@/lib/api';
import { clearCacheAction } from '@/app/actions/admin';

export default function CacheSlot() {
  const [cacheStats, setCacheStats] = useState<Record<string, any> | null>(null);
  const [cacheMessage, setCacheMessage] = useState('');
  const [isPending, setIsPending] = useState(false);

  const refreshCacheStats = async () => {
    try {
      const data = await fetchCacheStats();
      setCacheStats(data.stats);
    } catch {
      setCacheStats(null);
    }
  };

  useEffect(() => {
    refreshCacheStats();
  }, []);

  const handleCacheClear = async () => {
    setCacheMessage('');
    setIsPending(true);
    const result = await clearCacheAction();
    if (result.success) {
      setCacheMessage(`캐시 ${result.cleared}개 삭제`);
      await refreshCacheStats();
    } else {
      setCacheMessage(result.error || '캐시 삭제 실패');
    }
    setIsPending(false);
  };

  return (
    <Card.Root className="p-6">
      <Card.Title className="mb-4">캐시 관리</Card.Title>
      {cacheStats ? (
        <div className="grid gap-2 text-sm text-[var(--color-foreground)] mb-4">
          <span>Entries: {cacheStats.entries}</span>
          <span>Hits: {cacheStats.hits}</span>
          <span>Misses: {cacheStats.misses}</span>
          <span>Hit Rate: {cacheStats.hit_rate}%</span>
        </div>
      ) : (
        <p className="text-sm text-[var(--color-muted)] mb-4">캐시 통계를 불러오지 못했습니다.</p>
      )}
      <div className="flex items-center gap-3">
        <Button variant="default" onClick={handleCacheClear}>캐시 초기화</Button>
        {cacheMessage && <span className="text-sm text-[var(--color-muted)]">{cacheMessage}</span>}
      </div>
    </Card.Root>
  );
}
