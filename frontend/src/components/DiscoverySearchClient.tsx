'use client';

import { useState } from 'react';
import { Navbar } from '@/features/landing';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { searchDiscovery } from '@/lib/api';
import { DUMMY_DISCOVERY_RESULTS } from '@/lib/dummyData';

export default function DiscoverySearchClient() {
  const [query, setQuery] = useState('');
  const [maxResults, setMaxResults] = useState(5);
  const [results, setResults] = useState<Array<Record<string, any>>>(DUMMY_DISCOVERY_RESULTS);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    setError('');
    if (!query.trim()) {
      setError('검색어를 입력하세요.');
      return;
    }
    setLoading(true);
    try {
      const data = await searchDiscovery(query.trim(), maxResults);
      setResults((data.results && data.results.length > 0) ? data.results : DUMMY_DISCOVERY_RESULTS);
    } catch (err: any) {
      setError(err?.message || '검색 실패');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Navbar />
      <main className="min-h-screen bg-[var(--color-background)] p-8 pt-24">
        <Card className="max-w-5xl mx-auto space-y-6">
          <div>
            <p className="font-bold text-[var(--color-primary)] mb-2">Discovery Engine</p>
            <h1 className="text-4xl font-bold mb-2">검색 UI</h1>
            <p className="text-lg font-bold text-[var(--color-muted)]">
              Discovery Engine 인덱스에서 직접 검색하여 근거 자료를 확인합니다.
            </p>
          </div>

          <div className="grid gap-3 md:grid-cols-[1fr_auto_auto] items-center">
            <Input
              className="w-full"
              placeholder="검색어를 입력하세요"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <Input
              className="w-24"
              type="number"
              min={1}
              max={10}
              value={maxResults}
              onChange={(e) => setMaxResults(Number(e.target.value))}
            />
            <Button
              type="button"
              variant="default"
              onClick={handleSearch}
              disabled={loading}
            >
              {loading ? '검색 중...' : '검색'}
            </Button>
          </div>

          {error && <p className="text-sm text-[var(--color-destructive)]">{error}</p>}

          <div className="space-y-3">
            {results.length === 0 && !loading ? (
              <p className="text-sm text-[var(--color-muted)]">검색 결과가 없습니다.</p>
            ) : (
              <>
                {!loading && results === DUMMY_DISCOVERY_RESULTS && (
                  <p className="text-xs text-[var(--color-muted)]">(샘플 결과 · 검색 후 실제 결과로 대체됩니다)</p>
                )}
                {results.map((item, index) => (
                <div key={`${item.title}-${index}`} className="soft-section p-4 rounded-[var(--radius-md)]">
                  <h3 className="text-xl font-bold mb-2">{item.title || 'Untitled'}</h3>
                  <p className="text-sm font-bold text-[var(--color-muted)] mb-2">{item.snippet || '요약 없음'}</p>
                  {item.url && (
                    <a
                      href={item.url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-[var(--color-primary)] font-bold underline"
                    >
                      원문 보기
                    </a>
                  )}
                </div>
              ))}
              </>
            )}
          </div>
        </Card>
      </main>
    </>
  );
}
