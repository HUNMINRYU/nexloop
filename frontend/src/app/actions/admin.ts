'use server';

import { revalidateTag, revalidatePath } from 'next/cache';
import { clearCache, exportNotion } from '@/lib/api';
import { asTaskId } from '@/types/common';

export async function clearCacheAction() {
  try {
    const result = await clearCache();
    revalidatePath('/admin');
    return { success: true, cleared: result.cleared };
  } catch (error: any) {
    return { success: false, error: error.message || '캐시 삭제 실패' };
  }
}

export async function exportNotionAction(params: {
  task_id?: string;
  history_id?: string;
  parent_page_id?: string;
}) {
  try {
    const payload = {
      ...params,
      task_id: params.task_id ? asTaskId(params.task_id) : undefined,
    };
    const data = await exportNotion(payload);
    return { success: true, url: data.url };
  } catch (error: any) {
    return { success: false, error: error.message || 'Notion 내보내기 실패' };
  }
}
