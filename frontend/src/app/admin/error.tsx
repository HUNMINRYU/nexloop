'use client';

import { Button, Card } from '@/components/ui';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <Card.Root className="p-6 border-red-200 bg-red-50">
      <h2 className="text-lg font-bold text-red-800 mb-2">섹션 로드 실패</h2>
      <p className="text-sm text-red-600 mb-4">{error.message || '데이터를 불러오는 중 오류가 발생했습니다.'}</p>
      <Button variant="outline" onClick={() => reset()}>다시 시도</Button>
    </Card.Root>
  );
}
