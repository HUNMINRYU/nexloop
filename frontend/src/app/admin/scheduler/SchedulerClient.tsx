'use client';

import { useState, useEffect } from 'react';
import { fetchSchedules, deleteSchedule, toggleSchedule } from '@/lib/api';
import { Schedule } from '@/types/schedule';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import ScheduleForm from './ScheduleForm';

export default function SchedulerClient() {
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingSchedule, setEditingSchedule] = useState<Schedule | null>(null);

  useEffect(() => {
    loadSchedules();
  }, []);

  const loadSchedules = async () => {
    setIsLoading(true);
    try {
      const data = await fetchSchedules();
      setSchedules(data);
    } catch (error) {
      console.error('Failed to load schedules:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('이 스케줄을 삭제하시겠습니까?')) return;

    try {
      await deleteSchedule(id);
      await loadSchedules();
    } catch (error) {
      alert('스케줄 삭제에 실패했습니다.');
      console.error(error);
    }
  };

  const handleToggle = async (id: number, enabled: boolean) => {
    try {
      await toggleSchedule(id, enabled);
      await loadSchedules();
    } catch (error) {
      alert('스케줄 상태 변경에 실패했습니다.');
      console.error(error);
    }
  };

  const handleEdit = (schedule: Schedule) => {
    setEditingSchedule(schedule);
    setShowForm(true);
  };

  const handleFormClose = () => {
    setShowForm(false);
    setEditingSchedule(null);
    loadSchedules();
  };

  if (isLoading) {
    return <div className="text-center py-12">로딩 중...</div>;
  }

  return (
    <div>
      <div className="mb-6">
        <Button onClick={() => setShowForm(true)} variant="default">
          + 새 스케줄 추가
        </Button>
      </div>

      {showForm && (
        <ScheduleForm
          schedule={editingSchedule}
          onClose={handleFormClose}
        />
      )}

      {schedules.length === 0 ? (
        <Card className="p-8 text-center">
          <p className="text-[var(--color-muted)]">
            생성된 스케줄이 없습니다. 새 스케줄을 추가해 보세요.
          </p>
        </Card>
      ) : (
        <div className="grid gap-4">
          {schedules.map((schedule) => (
            <Card key={schedule.id} className="p-6">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-semibold">{schedule.name}</h3>
                    <span
                      className={`px-2 py-1 rounded text-xs font-medium ${
                        schedule.enabled
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-600'
                      }`}
                    >
                      {schedule.enabled ? '활성화' : '비활성화'}
                    </span>
                  </div>
                  {schedule.description && (
                    <p className="text-sm text-[var(--color-muted)] mb-3">
                      {schedule.description}
                    </p>
                  )}
                  <div className="space-y-1 text-sm">
                    <p>
                      <strong>제품:</strong> {schedule.product_name}
                    </p>
                    <p>
                      <strong>스케줄:</strong> {schedule.cron_expression}
                    </p>
                    <p>
                      <strong>타임존:</strong> {schedule.timezone}
                    </p>
                    {schedule.last_executed_at && (
                      <p>
                        <strong>마지막 실행:</strong>{' '}
                        {new Date(schedule.last_executed_at).toLocaleString('ko-KR')}
                      </p>
                    )}
                  </div>
                </div>

                <div className="flex gap-2 ml-4">
                  <Button
                    variant={schedule.enabled ? 'secondary' : 'default'}
                    onClick={() => handleToggle(schedule.id, !schedule.enabled)}
                  >
                    {schedule.enabled ? '비활성화' : '활성화'}
                  </Button>
                  <Button variant="outline" onClick={() => handleEdit(schedule)}>
                    수정
                  </Button>
                  <Button variant="destructive" onClick={() => handleDelete(schedule.id)}>
                    삭제
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
