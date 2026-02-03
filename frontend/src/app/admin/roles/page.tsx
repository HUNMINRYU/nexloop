export const dynamic = 'force-dynamic';
import AdminRolesClient from '@/components/AdminRolesClient';
import { fetchRoles, fetchTeams } from '@/lib/api';

export default async function AdminRolesPage() {
  const [roleData, teamData] = await Promise.all([fetchRoles(), fetchTeams()]);
  
  return (
    <AdminRolesClient 
      initialRoles={roleData.roles || []} 
      initialTeams={teamData.teams || []} 
    />
  );
}

