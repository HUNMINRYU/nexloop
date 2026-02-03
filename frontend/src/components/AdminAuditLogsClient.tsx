'use client';

import { useEffect, useState } from 'react';
import { Navbar } from '@/features/landing';
import { Button, Card, Input } from '@/components/ui';
import { fetchAuditLogs } from '@/lib/api';
import { DUMMY_AUDIT_LOGS } from '@/lib/dummyData';

interface AdminAuditLogsClientProps {
  initialLogs: Array<Record<string, any>>;
}

export default function AdminAuditLogsClient({ initialLogs }: AdminAuditLogsClientProps) {
  const [logs, setLogs] = useState<Array<Record<string, any>>>(
    initialLogs.length > 0 ? initialLogs : DUMMY_AUDIT_LOGS
  );
  const [limit, setLimit] = useState(50);
  const [error, setError] = useState('');
  const [isDummy, setIsDummy] = useState(initialLogs.length === 0);

  const loadLogs = async () => {
    setError('');
    try {
      const data = await fetchAuditLogs(limit);
      const list = data?.logs || [];
      const useDummy = list.length === 0;
      setLogs(useDummy ? DUMMY_AUDIT_LOGS : list);
      setIsDummy(useDummy);
    } catch (err: any) {
      setLogs(DUMMY_AUDIT_LOGS);
      setIsDummy(true);
    }
  };

  return (
    <>
      <Navbar />
      <main className="min-h-screen bg-[var(--color-background)] p-8 pt-24">
        <div className="max-w-6xl mx-auto space-y-6">
          <Card.Root className="p-6">
            <p className="text-sm font-medium text-[var(--color-primary)] mb-1">Admin</p>
            <h1 className="text-2xl font-semibold text-[var(--color-foreground)] mb-2">감사 로그</h1>
            <p className="text-base text-[var(--color-muted)] mb-4">변경 이력을 확인합니다.</p>

            <div className="flex gap-3 items-center mb-4">
              <Input className="w-24" type="number" min={1} max={200} value={limit} onChange={(e) => setLimit(Number(e.target.value))} />
              <Button variant="default" onClick={loadLogs}>새로고침</Button>
            </div>

            {error && <p className="text-sm text-[var(--color-destructive)] mb-2">{error}</p>}
            {isDummy && logs.length > 0 && (
              <p className="text-xs text-[var(--color-muted)] mb-2">(더미 데이터 · API 연동 후 실제 로그로 대체됩니다)</p>
            )}

            <div className="space-y-3">
              {logs.length === 0 ? (
                <p className="text-sm text-[var(--color-muted)]">감사 로그가 없습니다.</p>
              ) : (
                logs.map((log) => (
                  <div key={log.id} className="border border-[var(--color-border)] rounded-[var(--radius-md)] p-3 text-sm">
                    <div className="font-semibold text-[var(--color-foreground)]">{log.action}</div>
                    <div className="text-[var(--color-muted)]">
                      {log.actor_email} ({log.actor_role}) · {log.created_at || '-'}
                    </div>
                    <div className="text-[var(--color-muted)]">{log.entity_type} {log.entity_id || ''}</div>
                    {log.metadata && (
                      <pre className="text-xs mt-2 bg-[var(--color-secondary)] p-2 rounded-[var(--radius-sm)] overflow-auto">{log.metadata}</pre>
                    )}
                  </div>
                ))
              )}
            </div>
          </Card.Root>
        </div>
      </main>
    </>
  );
}
