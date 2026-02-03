export const dynamic = 'force-dynamic';
import AdminAuditLogsClient from '@/components/AdminAuditLogsClient';
import { fetchAuditLogs } from '@/lib/api';

export default async function AdminAuditLogsPage() {
  const data = await fetchAuditLogs(50);
  
  return <AdminAuditLogsClient initialLogs={data?.logs || []} />;
}

