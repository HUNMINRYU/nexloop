'use client';

import { useState } from 'react';
import { Button, Card, Input } from '@/components/ui';
import { exportNotionAction } from '@/app/actions/admin';

export default function NotionSlot() {
  const [taskId, setTaskId] = useState('');
  const [historyId, setHistoryId] = useState('');
  const [parentPageId, setParentPageId] = useState('');
  const [notionUrl, setNotionUrl] = useState('');
  const [notionError, setNotionError] = useState('');
  const [isPending, setIsPending] = useState(false);

  const handleNotionExport = async () => {
    setNotionError('');
    setNotionUrl('');
    setIsPending(true);
    const result = await exportNotionAction({
      task_id: taskId || undefined,
      history_id: historyId || undefined,
      parent_page_id: parentPageId || undefined,
    });
    
    if (result.success) {
      setNotionUrl(result.url || '');
    } else {
      setNotionError(result.error || 'Notion 내보내기 실패');
    }
    setIsPending(false);
  };

  return (
    <Card.Root className="p-6">
      <Card.Title className="mb-4">Notion 내보내기</Card.Title>
      <div className="grid gap-3 md:grid-cols-2 mb-4">
        <Input placeholder="task_id (선택)" value={taskId} onChange={(e) => setTaskId(e.target.value)} />
        <Input placeholder="history_id (선택)" value={historyId} onChange={(e) => setHistoryId(e.target.value)} />
        <Input className="md:col-span-2" placeholder="parent_page_id (선택)" value={parentPageId} onChange={(e) => setParentPageId(e.target.value)} />
      </div>
      <Button variant="default" onClick={handleNotionExport}>Notion 내보내기 실행</Button>
      {notionUrl && (
        <a href={notionUrl} target="_blank" rel="noreferrer" className="block font-medium text-[var(--color-primary)] underline mt-2">Notion 링크 열기</a>
      )}
      {notionError && <p className="text-sm text-[var(--color-destructive)] mt-2">{notionError}</p>}
    </Card.Root>
  );
}
