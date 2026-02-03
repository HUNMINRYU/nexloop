'use client';

import { useState } from 'react';
import { Button, Card, Input } from '@/components/ui';
import { fetchGcsMetadata } from '@/lib/api';
import { asGcsPath } from '@/types/common';

export default function GcsSlot() {
  const [gcsPath, setGcsPath] = useState('');
  const [prefix, setPrefix] = useState('');
  const [limit, setLimit] = useState(30);
  const [metadataItems, setMetadataItems] = useState<Array<Record<string, any>>>([]);
  const [metadataError, setMetadataError] = useState('');

  const handleFetchMetadata = async () => {
    setMetadataError('');
    setMetadataItems([]);
    try {
      const data = await fetchGcsMetadata({
        gcs_path: gcsPath ? asGcsPath(gcsPath) : undefined,
        prefix: prefix || undefined,
        limit,
      });
      setMetadataItems(data.items || []);
    } catch (error: any) {
      setMetadataError(error?.message || '메타데이터 조회 실패');
    }
  };

  return (
    <Card.Root className="p-6">
      <Card.Title className="mb-4">GCS 메타데이터</Card.Title>
      <div className="grid gap-3 md:grid-cols-2 mb-4">
        <Input
          placeholder="gs://bucket/path 또는 object path"
          value={gcsPath}
          onChange={(e) => setGcsPath(e.target.value)}
        />
        <Input
          placeholder="prefix (선택)"
          value={prefix}
          onChange={(e) => setPrefix(e.target.value)}
        />
      </div>
      <div className="flex items-center gap-3 mb-4">
        <Input
          className="w-24"
          type="number"
          min={1}
          max={200}
          value={limit}
          onChange={(e) => setLimit(Number(e.target.value))}
        />
        <Button variant="secondary" onClick={handleFetchMetadata}>메타데이터 조회</Button>
        {metadataError && <span className="text-sm text-[var(--color-destructive)]">{metadataError}</span>}
      </div>
      {metadataItems.length > 0 ? (
        <div className="space-y-3">
          {metadataItems.map((item, index) => (
            <div key={`${item.name}-${index}`} className="border border-[var(--color-border)] rounded-[var(--radius-md)] p-3 text-sm">
              <div className="font-semibold text-[var(--color-foreground)]">{item.name}</div>
              <div className="text-[var(--color-muted)]">
                Size: {item.size ?? '-'} · Updated: {item.updated ?? '-'} · Type: {item.content_type ?? '-'}
              </div>
              {item.signed_url && (
                <a href={item.signed_url} className="text-[var(--color-primary)] font-medium underline" target="_blank" rel="noreferrer">
                  Signed URL 열기
                </a>
              )}
            </div>
          ))}
        </div>
      ) : (
        <p className="text-sm text-[var(--color-muted)]">표시할 메타데이터가 없습니다.</p>
      )}
    </Card.Root>
  );
}
