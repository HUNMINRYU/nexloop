'use client';

import Link from 'next/link';
import { Navbar } from '@/features/landing';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import usePipelineHistory from '@/hooks/usePipelineHistory';
import { GcsPath } from '@/types/common';
import { clearCache, deriveGcsPathFromUrl, fetchCacheStats, fetchPipelineResult, refreshUrl } from '@/lib/api';
import { DUMMY_PROMPT_LOGS } from '@/lib/dummyData';
import { useEffect, useMemo, useState } from 'react';

const slugs: Record<string, { title: string; subtitle: string }> = {
  'video-vault': { title: 'Video Vault', subtitle: 'Storage for completed short-form videos' },
  'asset-library': { title: 'Asset Library', subtitle: 'Storage for generated thumbnails and image sources' },
  'prompt-log': { title: 'Prompt Log', subtitle: 'Management of successful prompt history' },
};

type StorageSlugClientProps = {
  slug: string;
};

type MediaItem = { url: string; gcsPath: GcsPath | null; retries: number };

export default function StorageSlugClient({ slug }: StorageSlugClientProps) {
  const item = slugs[slug];
  const { tasks, error, isLoading, isDummy } = usePipelineHistory();
  const [results, setResults] = useState<Record<string, any>>({});
  const [cacheStats, setCacheStats] = useState<Record<string, any> | null>(null);
  const [cacheMessage, setCacheMessage] = useState('');
  const [videoItems, setVideoItems] = useState<MediaItem[]>([]);
  const [thumbnailItems, setThumbnailItems] = useState<MediaItem[]>([]);

  useEffect(() => {
    if (!slug || tasks.length === 0) {
      return;
    }
    if (slug === 'video-vault' || slug === 'asset-library' || slug === 'prompt-log') {
      const taskIds = tasks.map((task) => task.task_id).filter(Boolean);
      Promise.all(
        taskIds.map((taskId) =>
          fetchPipelineResult(taskId).then((data) => ({ taskId, data })).catch(() => null)
        )
      ).then((items) => {
        const mapped: Record<string, any> = {};
        items.forEach((entry) => {
          if (!entry) return;
          mapped[entry.taskId] = entry.data;
        });
        setResults(mapped);
      });
    }
  }, [slug, tasks]);

  useEffect(() => {
    if (slug !== 'prompt-log') {
      return;
    }
    fetchCacheStats()
      .then((data) => setCacheStats(data.stats))
      .catch(() => setCacheStats(null));
  }, [slug]);

  const videoUrls = useMemo(() => {
    if (slug !== 'video-vault') {
      return [];
    }
    return tasks
      .map((task) => results[task.task_id]?.result?.generated_content?.video_url)
      .filter(Boolean);
  }, [results, slug, tasks]);

  const thumbnailUrls = useMemo(() => {
    if (slug !== 'asset-library') {
      return [];
    }
    const items: string[] = [];
    tasks.forEach((task) => {
      const content = results[task.task_id]?.result?.generated_content;
      if (content?.thumbnail_url) {
        items.push(content.thumbnail_url);
      }
      if (Array.isArray(content?.multi_thumbnails)) {
        content.multi_thumbnails.forEach((thumb: any) => {
          const url = thumb.url || thumb.thumbnail_url || thumb.image_url;
          if (url) {
            items.push(url);
          }
        });
      }
    });
    return items;
  }, [results, slug, tasks]);

  useEffect(() => {
    if (slug !== 'video-vault') {
      return;
    }
    const items = videoUrls.map((url) => ({
      url,
      gcsPath: deriveGcsPathFromUrl(url),
      retries: 0,
    }));
    setVideoItems(items);
  }, [videoUrls, slug]);

  useEffect(() => {
    if (slug !== 'asset-library') {
      return;
    }
    const items = thumbnailUrls.map((url) => ({
      url,
      gcsPath: deriveGcsPathFromUrl(url),
      retries: 0,
    }));
    setThumbnailItems(items);
  }, [thumbnailUrls, slug]);

  const handleRefreshMedia = async (kind: 'video' | 'thumb', index: number, gcsPath: GcsPath | null) => {
    if (!gcsPath) {
      return;
    }
    try {
      const result = await refreshUrl(gcsPath);
      if (kind === 'video') {
        setVideoItems((prev) =>
          prev.map((item, idx) =>
            idx === index ? { ...item, url: result.url, retries: item.retries + 1 } : item
          )
        );
      } else {
        setThumbnailItems((prev) =>
          prev.map((item, idx) =>
            idx === index ? { ...item, url: result.url, retries: item.retries + 1 } : item
          )
        );
      }
    } catch {
      // silent
    }
  };

  const handleCacheClear = async () => {
    setCacheMessage('');
    try {
      const result = await clearCache();
      setCacheMessage(`캐시 ${result.cleared}개 삭제`);
      const updated = await fetchCacheStats();
      setCacheStats(updated.stats);
    } catch {
      setCacheMessage('캐시 삭제 실패');
    }
  };

  if (!item) {
    return (
      <>
        <Navbar />
        <main className="min-h-screen bg-[var(--color-background)] flex flex-col items-center justify-center p-8 pt-24">
          <Card className="max-w-2xl w-full text-center">
            <h1 className="text-4xl font-bold mb-4">Not Found</h1>
            <Button asChild variant="secondary"><Link href="/">Back to Home</Link></Button>
          </Card>
        </main>
      </>
    );
  }

  const renderVideoVault = () => {
    if (slug !== 'video-vault') {
      return null;
    }
    return (
      <div className="grid gap-4 md:grid-cols-2">
        {isDummy && <p className="text-xs text-[var(--color-muted)] col-span-full">(더미 데이터)</p>}
        {videoItems.length === 0 && !isDummy && (
          <p className="text-sm text-[var(--color-muted)]">표시할 비디오가 없습니다.</p>
        )}
        {videoItems.length > 0 && videoItems.map((item, idx) => (
          <div key={`${item.url}-${idx}`} className="soft-section p-2 rounded-[var(--radius-md)]">
            <video
              src={item.url}
              controls
              className="w-full"
              onError={() => {
                if (item.retries < 1) {
                  handleRefreshMedia('video', idx, item.gcsPath);
                }
              }}
            />
            <a
              href={item.url}
              download
              className="mt-2 inline-block text-xs font-bold underline"
            >
              다운로드
            </a>
          </div>
        ))}
      </div>
    );
  };

  const renderAssetLibrary = () => {
    if (slug !== 'asset-library') {
      return null;
    }
    return (
      <div className="grid gap-4 grid-cols-2 md:grid-cols-3">
        {thumbnailItems.length === 0 ? (
          <p className="text-sm text-[var(--color-muted)]">표시할 썸네일이 없습니다.</p>
        ) : (
          thumbnailItems.map((item, idx) => (
            <div key={`${item.url}-${idx}`} className="soft-section p-2 rounded-[var(--radius-md)]">
              <img
                src={item.url}
                alt={`thumb-${idx}`}
                className="w-full aspect-[9/16] object-cover"
                onError={() => {
                  if (item.retries < 1) {
                    handleRefreshMedia('thumb', idx, item.gcsPath);
                  }
                }}
              />
              <a
                href={item.url}
                download
                className="mt-2 inline-block text-xs font-bold underline"
              >
                다운로드
              </a>
            </div>
          ))
        )}
      </div>
    );
  };

  const renderPromptLog = () => {
    if (slug !== 'prompt-log') {
      return null;
    }
    return (
      <div className="space-y-4">
        <div className="soft-section p-4 space-y-2 rounded-[var(--radius-md)]">
          <p className="font-bold">캐시 상태</p>
          {cacheStats ? (
            <div className="text-sm text-[var(--color-muted)] space-y-1">
              <p>전체: {cacheStats.total_entries}</p>
              <p>활성: {cacheStats.active_entries}</p>
              <p>만료: {cacheStats.expired_entries}</p>
            </div>
          ) : (
            <p className="text-sm text-[var(--color-muted)]">캐시 정보를 불러오지 못했습니다.</p>
          )}
          <Button type="button" variant="default" className="px-4 py-2" onClick={handleCacheClear}>
            캐시 초기화
          </Button>
          {cacheMessage && <p className="text-xs text-[var(--color-muted)]">{cacheMessage}</p>}
        </div>
        {isDummy && <p className="text-xs text-[var(--color-muted)]">(더미 데이터)</p>}
        {tasks.length === 0 ? (
          <p className="text-sm text-[var(--color-muted)]">표시할 이력이 없습니다.</p>
        ) : (
          tasks.map((task, idx) => {
            const promptLog =
              results[task.task_id]?.result?.prompt_log ??
              (isDummy ? DUMMY_PROMPT_LOGS[idx % DUMMY_PROMPT_LOGS.length]?.prompt_log : null);
            return (
              <div key={task.task_id} className="soft-section p-4 rounded-[var(--radius-md)]">
                <p className="font-bold">Task: {task.task_id}</p>
                <p className="text-sm text-[var(--color-muted)]">Status: {task.status}</p>
                <p className="text-sm text-[var(--color-muted)]">Product: {task.product}</p>
                {promptLog && (
                  <details className="mt-3 soft-section p-2 rounded-[var(--radius-sm)]">
                    <summary className="text-xs font-bold cursor-pointer">프롬프트 로그</summary>
                    <pre className="mt-2 text-xs whitespace-pre-wrap">
                      {JSON.stringify(promptLog, null, 2)}
                    </pre>
                  </details>
                )}
              </div>
            );
          })
        )}
      </div>
    );
  };

  return (
    <>
      <Navbar />
      <main className="min-h-screen bg-[var(--color-background)] p-8 pt-24">
        <Card className="max-w-5xl mx-auto">
          <p className="font-bold text-[var(--color-primary)] mb-2">Storage</p>
          <h1 className="text-4xl font-bold mb-4">{item.title}</h1>
          <p className="text-xl font-bold text-[var(--color-muted)] mb-8">{item.subtitle}</p>

          {isLoading && <p className="text-sm text-[var(--color-muted)]">로딩 중...</p>}
          {error && <p className="text-sm text-[var(--color-destructive)]">{error}</p>}

          {renderVideoVault()}
          {renderAssetLibrary()}
          {renderPromptLog()}

          <div className="mt-8">
            <Button asChild variant="secondary"><Link href="/">Back to Home</Link></Button>
          </div>
        </Card>
      </main>
    </>
  );
}
