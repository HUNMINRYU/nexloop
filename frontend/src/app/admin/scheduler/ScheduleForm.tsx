'use client';

import { useState } from 'react';
import { createSchedule, updateSchedule } from '@/lib/api';
import { Schedule, SchedulePayload } from '@/types/schedule';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Modal from '@/components/ui/Modal';

interface Props {
  schedule?: Schedule | null;
  onClose: () => void;
}

const DAYS_OF_WEEK = [
  { value: 0, label: '월' },
  { value: 1, label: '화' },
  { value: 2, label: '수' },
  { value: 3, label: '목' },
  { value: 4, label: '금' },
  { value: 5, label: '토' },
  { value: 6, label: '일' },
];

const PRODUCTS = [
  '벅스델타',
  '블루가드 바퀴벌레겔',
  '쥐싹킬',
  '바퀴벌레 트랩',
  '모기 트랩',
  '초파리 트랩',
  '개미 트랩',
  '진드기 스프레이',
  '쥐약',
  '바퀴벌레 약',
  '파리채',
  '모기향',
  '탈취제',
  '살균제',
  '해충 퇴치기',
];

const DEFAULT_PRODUCT = PRODUCTS[0] ?? "";

export default function ScheduleForm({ schedule, onClose }: Props) {
  const [name, setName] = useState(schedule?.name || '');
  const [description, setDescription] = useState(schedule?.description || '');
  const [frequency, setFrequency] = useState<'daily' | 'weekly' | 'custom'>('daily');
  const [selectedDays, setSelectedDays] = useState<number[]>([]);
  const [hour, setHour] = useState(16);
  const [minute, setMinute] = useState(0);
  const [productName, setProductName] = useState<string>(schedule?.product_name ?? DEFAULT_PRODUCT);

  const [isPending, setIsPending] = useState(false);
  const [message, setMessage] = useState('');

  const handleDayToggle = (day: number) => {
    setSelectedDays((prev) =>
      prev.includes(day)
        ? prev.filter((d) => d !== day)
        : [...prev, day].sort()
    );
  };

  const handleSubmit = async () => {
    // 검증
    if (!name.trim()) {
      setMessage('스케줄 이름을 입력해 주세요.');
      return;
    }

    if (frequency !== 'daily' && selectedDays.length === 0) {
      setMessage('요일을 최소 1개 이상 선택해 주세요.');
      return;
    }

    setMessage('');
    setIsPending(true);

    const payload: SchedulePayload = {
      name,
      description: description || undefined,
      frequency,
      days_of_week: frequency === 'daily' ? [] : selectedDays,
      hour,
      minute,
      timezone: 'Asia/Seoul',
      product_name: productName,
      pipeline_config: {
        youtube_count: 3,
        naver_count: 10,
        include_comments: true,
        generate_social: true,
        generate_video: true,
        generate_thumbnails: true,
        export_to_notion: true,
        thumbnail_count: 3,
        thumbnail_styles: ['vibrant', 'neobrutalism'],
      },
    };

    try {
      if (schedule) {
        await updateSchedule(schedule.id, payload);
        setMessage('스케줄이 수정되었습니다.');
      } else {
        await createSchedule(payload);
        setMessage('스케줄이 생성되었습니다.');
      }
      setTimeout(onClose, 1500);
    } catch (error: any) {
      setMessage(error.message || '오류가 발생했습니다.');
    } finally {
      setIsPending(false);
    }
  };

  return (
    <Modal open onClose={onClose}>
      <Card className="p-6 max-w-2xl max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl font-bold mb-4">
          {schedule ? '스케줄 수정' : '새 스케줄 추가'}
        </h2>

        <div className="space-y-4">
          {/* 기본 정보 */}
          <div>
            <label className="block text-sm font-medium mb-1">
              스케줄 이름 <span className="text-red-500">*</span>
            </label>
            <Input
              placeholder="예: 벅스델타 매일 오후 4시 자동 실행"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">설명 (선택)</label>
            <Input
              placeholder="스케줄에 대한 설명"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>

          {/* 제품 선택 */}
          <div>
            <label className="block text-sm font-medium mb-1">
              제품 선택 <span className="text-red-500">*</span>
            </label>
            <select
              className="w-full px-4 py-2 border rounded-[var(--radius-md)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              value={productName}
              onChange={(e) => setProductName(e.target.value)}
            >
              {PRODUCTS.map((product) => (
                <option key={product} value={product}>
                  {product}
                </option>
              ))}
            </select>
          </div>

          {/* 주기 선택 */}
          <div>
            <label className="block text-sm font-medium mb-1">
              실행 주기 <span className="text-red-500">*</span>
            </label>
            <div className="flex gap-2">
              {(['daily', 'weekly', 'custom'] as const).map((freq) => (
                <Button
                  key={freq}
                  type="button"
                  variant={frequency === freq ? 'default' : 'outline'}
                  onClick={() => setFrequency(freq)}
                >
                  {freq === 'daily' ? '매일' : freq === 'weekly' ? '매주' : '사용자 정의'}
                </Button>
              ))}
            </div>
          </div>

          {/* 요일 선택 (주간/사용자 정의) */}
          {(frequency === 'weekly' || frequency === 'custom') && (
            <div>
              <label className="block text-sm font-medium mb-1">
                실행 요일 <span className="text-red-500">*</span>
              </label>
              <div className="flex gap-2">
                {DAYS_OF_WEEK.map((day) => (
                  <Button
                    key={day.value}
                    type="button"
                    variant={selectedDays.includes(day.value) ? 'default' : 'outline'}
                    onClick={() => handleDayToggle(day.value)}
                  >
                    {day.label}
                  </Button>
                ))}
              </div>
            </div>
          )}

          {/* 시간 선택 */}
          <div>
            <label className="block text-sm font-medium mb-1">
              실행 시간 <span className="text-red-500">*</span>
            </label>
            <div className="flex gap-2 items-center">
              <select
                className="px-4 py-2 border rounded-[var(--radius-md)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                value={hour}
                onChange={(e) => setHour(Number(e.target.value))}
              >
                {Array.from({ length: 24 }, (_, i) => (
                  <option key={i} value={i}>
                    {i.toString().padStart(2, '0')}시
                  </option>
                ))}
              </select>
              <span className="text-lg">:</span>
              <select
                className="px-4 py-2 border rounded-[var(--radius-md)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                value={minute}
                onChange={(e) => setMinute(Number(e.target.value))}
              >
                {Array.from({ length: 60 }, (_, i) => (
                  <option key={i} value={i}>
                    {i.toString().padStart(2, '0')}분
                  </option>
                ))}
              </select>
            </div>
            <p className="text-xs text-[var(--color-muted)] mt-1">
              타임존: Asia/Seoul (한국 시간)
            </p>
          </div>

          {/* 버튼 */}
          <div className="flex items-center gap-3 pt-4 border-t">
            <Button
              type="button"
              onClick={handleSubmit}
              disabled={isPending || !name.trim()}
            >
              {isPending ? '저장 중...' : schedule ? '수정' : '생성'}
            </Button>
            <Button type="button" variant="outline" onClick={onClose}>
              취소
            </Button>
            {message && (
              <span
                className={`text-sm ${
                  message.includes('오류') || message.includes('실패')
                    ? 'text-[var(--color-destructive)]'
                    : 'text-[var(--color-primary)]'
                }`}
              >
                {message}
              </span>
            )}
          </div>
        </div>
      </Card>
    </Modal>
  );
}
