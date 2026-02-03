export const dynamic = 'force-dynamic';
import { Button, Card } from '@/components/ui';
import Link from 'next/link';

export default function AdminPage() {
  return (
    <Card.Root className="p-6">
      <p className="text-sm font-medium text-[var(--color-primary)] mb-1">Admin</p>
      <h1 className="text-2xl font-semibold text-[var(--color-foreground)] mb-2">관리자 대시보드</h1>
      <p className="text-base text-[var(--color-muted)] mb-4">
        시스템 상태, 프롬프트 로그, 저장소 메타데이터를 관리합니다.
      </p>
      <div className="flex flex-wrap gap-3">
        <Link href="/search/discovery"><Button variant="secondary">Discovery 검색 UI</Button></Link>
        <Link href="/admin/roles"><Button variant="secondary">Role / Team 관리</Button></Link>
        <Link href="/admin/audit-logs"><Button variant="default">감사 로그</Button></Link>
        <Link href="/admin/scheduler"><Button variant="default">스케줄러 관리</Button></Link>
      </div>
    </Card.Root>
  );
}

