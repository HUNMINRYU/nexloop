import { useState, useEffect } from 'react';
import { updateApprovalStatus } from '@/lib/api';
import { asTaskId } from '@/types/common';

interface UsePipelineApprovalProps {
  taskId: string;
  role: string;
  initialApprovalStatus?: string | null;
}

export function usePipelineApproval({
  taskId,
  role,
  initialApprovalStatus = null,
}: UsePipelineApprovalProps) {
  const [approvalStatus, setApprovalStatus] = useState<string | null>(initialApprovalStatus);
  const [approvalMessage, setApprovalMessage] = useState('');
  const [isUpdatingApproval, setIsUpdatingApproval] = useState(false);

  const canApprove = role === 'admin' || role === 'approver';

  const handleApproval = async (status: 'approved' | 'rejected') => {
    if (!taskId || isUpdatingApproval) return;
    setApprovalMessage('');
    setIsUpdatingApproval(true);
    try {
      const response = await updateApprovalStatus(asTaskId(taskId), status);
      setApprovalStatus(response.status);
      setApprovalMessage(status === 'approved' ? '승인 완료' : '거부 완료');
    } catch (error: any) {
      setApprovalMessage(error?.message || '승인 상태 변경에 실패했습니다.');
    } finally {
      setIsUpdatingApproval(false);
    }
  };

  return {
    approvalStatus,
    setApprovalStatus,
    approvalMessage,
    isUpdatingApproval,
    canApprove,
    handleApproval,
  };
}
