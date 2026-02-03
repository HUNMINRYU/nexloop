'use client';

import { useEffect, useState } from 'react';
import { Navbar } from '@/features/landing';
import { Button, Card, Input } from '@/components/ui';
import { createRole, createTeam, fetchRoles, fetchTeams } from '@/lib/api';

interface AdminRolesClientProps {
  initialRoles: Array<{ id: number; name: string; description?: string | null }>;
  initialTeams: Array<{ id: number; name: string }>;
}

export default function AdminRolesClient({ initialRoles, initialTeams }: AdminRolesClientProps) {
  const [roles, setRoles] = useState(initialRoles);
  const [teams, setTeams] = useState(initialTeams);
  const [roleName, setRoleName] = useState('');
  const [roleDesc, setRoleDesc] = useState('');
  const [teamName, setTeamName] = useState('');
  const [message, setMessage] = useState('');

  const loadData = async () => {
    try {
      const [roleData, teamData] = await Promise.all([fetchRoles(), fetchTeams()]);
      setRoles(roleData.roles || []);
      setTeams(teamData.teams || []);
    } catch {
      setMessage('데이터 갱신 실패');
    }
  };

  const handleCreateRole = async () => {
    setMessage('');
    if (!roleName.trim()) {
      setMessage('역할 이름을 입력하세요.');
      return;
    }
    await createRole({ name: roleName.trim(), description: roleDesc.trim() || undefined });
    setRoleName('');
    setRoleDesc('');
    await loadData();
  };

  const handleCreateTeam = async () => {
    setMessage('');
    if (!teamName.trim()) {
      setMessage('팀 이름을 입력하세요.');
      return;
    }
    await createTeam({ name: teamName.trim() });
    setTeamName('');
    await loadData();
  };

  return (
    <>
      <Navbar />
      <main className="min-h-screen bg-[var(--color-background)] p-8 pt-24">
        <div className="max-w-5xl mx-auto space-y-8">
          <Card.Root className="p-6">
            <p className="text-sm font-medium text-[var(--color-primary)] mb-1">Admin</p>
            <h1 className="text-2xl font-semibold text-[var(--color-foreground)] mb-2">Role / Team 관리</h1>
            <p className="text-base text-[var(--color-muted)] mb-4">역할과 팀 정보를 관리합니다.</p>

            {message && <p className="text-sm text-[var(--color-destructive)] mb-4">{message}</p>}

            <Card.Root className="p-6 mb-6">
              <Card.Title className="mb-4">역할 생성</Card.Title>
              <div className="grid gap-3 md:grid-cols-2 mb-4">
                <Input placeholder="role name" value={roleName} onChange={(e) => setRoleName(e.target.value)} />
                <Input placeholder="description (optional)" value={roleDesc} onChange={(e) => setRoleDesc(e.target.value)} />
              </div>
              <Button variant="secondary" onClick={handleCreateRole}>역할 추가</Button>
              <div className="space-y-2 mt-4">
                {roles.map((role) => (
                  <div key={role.id} className="border border-[var(--color-border)] rounded-[var(--radius-md)] p-3 text-sm font-medium text-[var(--color-foreground)]">
                    {role.name} {role.description ? `- ${role.description}` : ''}
                  </div>
                ))}
              </div>
            </Card.Root>

            <Card.Root className="p-6">
              <Card.Title className="mb-4">팀 생성</Card.Title>
              <div className="flex gap-3 mb-4">
                <Input className="flex-1" placeholder="team name" value={teamName} onChange={(e) => setTeamName(e.target.value)} />
                <Button variant="secondary" onClick={handleCreateTeam}>팀 추가</Button>
              </div>
              <div className="space-y-2">
                {teams.map((team) => (
                  <div key={team.id} className="border border-[var(--color-border)] rounded-[var(--radius-md)] p-3 text-sm font-medium text-[var(--color-foreground)]">
                    {team.name}
                  </div>
                ))}
              </div>
            </Card.Root>
          </Card.Root>
        </div>
      </main>
    </>
  );
}
