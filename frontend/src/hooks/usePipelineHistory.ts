'use client';

import { useQuery } from '@tanstack/react-query';
import { fetchPipelineHistory } from '@/lib/api';
import { DUMMY_PIPELINE_TASKS } from '@/lib/dummyData';

export default function usePipelineHistory() {
  const isDev = process.env.NODE_ENV === 'development';

  const { data, isError, isLoading } = useQuery({
    queryKey: ['pipeline', 'history'],
    queryFn: async () => {
      try {
        const response = await fetchPipelineHistory();
        return response?.tasks || [];
      } catch (error) {
        if (isDev) {
          console.warn('API fetch failed, returning dummy data in dev mode.');
          return DUMMY_PIPELINE_TASKS;
        }
        throw error;
      }
    },
  });

  // Dev mode fallback logic is handled within queryFn, but explicit check for tasks
  const tasks = data || [];
  const isDummy = isDev && (isError || (tasks === DUMMY_PIPELINE_TASKS));

  return { 
    tasks, 
    error: isError ? '파이프라인 이력을 불러오지 못했습니다.' : '', 
    isLoading, 
    isDummy 
  };
}
