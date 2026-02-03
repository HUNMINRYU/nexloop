import { TaskId, GcsPath, Email, asGcsPath } from '@/types/common';
import * as ApiTypes from '@/types/api';
import { Schedule, SchedulePayload } from '@/types/schedule';
import {
  DailyReportResponse,
  InsightFailuresResponse,
  InsightMetricsResponse,
  InsightSearchResponse,
  NaverIngestResponse,
} from '@/types/insights';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

type RequestOptions = Omit<RequestInit, 'body'> & { body?: string | FormData };

function getAuthHeaders(): Record<string, string> {
  if (typeof window === 'undefined') {
    return {};
  }
  const token = sessionStorage.getItem('auth_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
      ...(options.headers || {}),
    } as Record<string, string>,
  });

  if (!response.ok) {
    // Only redirect to login for authenticated endpoints (not /chat for guests)
    if (response.status === 401 && typeof window !== 'undefined' && path !== '/chat') {
      sessionStorage.removeItem('auth_token');
      if (!window.location.pathname.startsWith('/login')) {
        window.location.href = '/login';
      }
    }
    if (response.status === 403) {
      throw new Error('접근 권한이 없습니다.');
    }
    if (response.status === 429) {
      // Rate limit exceeded
      const message = await response.text();
      throw new Error(message || 'Too many requests. Please try again later.');
    }
    const message = await response.text();
    throw new Error(message || `Request failed: ${response.status}`);
  }

  const contentType = response.headers.get('content-type') || '';
  if (contentType.includes('application/json')) {
    return (await response.json()) as T;
  }
  return (await response.text()) as unknown as T;
}

export function fetchProducts() {
  return request<{ products: string[] }>('/products/');
}

export function runPipeline(payload: {
  product_name: string;
  youtube_count: number;
  naver_count: number;
  include_comments: boolean;
  generate_social: boolean;
  generate_video: boolean;
  generate_thumbnails: boolean;
  export_to_notion: boolean;
}) {
  return request<{ task_id: TaskId }>('/pipeline/run', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function fetchPipelineStatus(taskId: TaskId) {
  return request<ApiTypes.PipelineStatus>(`/pipeline/status/${taskId}`);
}

export function fetchPipelineResult(taskId: TaskId) {
  return request<ApiTypes.PipelineResult>(`/pipeline/result/${taskId}`);
}

export function updateApprovalStatus(
  taskId: TaskId,
  status: 'approved' | 'rejected',
) {
  return request<{ status: string }>(`/pipeline/result/${taskId}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status }),
  });
}

export function fetchPipelineHistory() {
  return request<{ tasks: Array<ApiTypes.PipelineResult> }>('/pipeline/history');
}

export function refreshUrl(gcsPath: GcsPath) {
  return request<{ url: string }>('/refresh-url', {
    method: 'POST',
    body: JSON.stringify({ gcs_path: gcsPath }),
  });
}

export function deriveGcsPathFromUrl(url: string | null | undefined): GcsPath | null {
  if (!url) return null;
  if (url.startsWith('gs://')) {
    return asGcsPath(url);
  }
  try {
    const parsed = new URL(url);
    const host = parsed.hostname;
    const pathname = parsed.pathname || '';

    // Format: https://storage.googleapis.com/<bucket>/<object>
    if (host === 'storage.googleapis.com') {
      const parts = pathname.split('/').filter(Boolean);
      if (parts.length >= 2) {
        const bucket = parts[0];
        const objectPath = parts.slice(1).join('/');
        return asGcsPath(`gs://${bucket}/${decodeURIComponent(objectPath)}`);
      }
    }

    // Format: https://<bucket>.storage.googleapis.com/<object>
    if (host.endsWith('.storage.googleapis.com')) {
      const bucket = host.replace('.storage.googleapis.com', '');
      const objectPath = pathname.replace(/^\//, '');
      if (bucket && objectPath) {
        return asGcsPath(`gs://${bucket}/${decodeURIComponent(objectPath)}`);
      }
    }

    // Format: https://storage.googleapis.com/<bucket>/o/<object>
    const oIndex = pathname.indexOf('/o/');
    if (host === 'storage.googleapis.com' && oIndex >= 0) {
      const parts = pathname.split('/').filter(Boolean);
      const bucket = parts[0];
      const objectPath = pathname.slice(oIndex + 3);
      if (bucket && objectPath) {
        return asGcsPath(`gs://${bucket}/${decodeURIComponent(objectPath)}`);
      }
    }
  } catch {
    // fall through
  }
  return null;
}

export function fetchCacheStats() {
  return request<{ stats: Record<string, any> }>('/admin/cache/stats');
}

export function clearCache() {
  return request<{ cleared: number }>('/admin/cache/clear', {
    method: 'POST',
  });
}

export function fetchGcsMetadata(params: { gcs_path?: GcsPath; prefix?: string; limit?: number }) {
  const search = new URLSearchParams();
  if (params.gcs_path) {
    search.set('gcs_path', params.gcs_path);
  }
  if (params.prefix) {
    search.set('prefix', params.prefix);
  }
  if (params.limit) {
    search.set('limit', String(params.limit));
  }
  const query = search.toString();
  return request<{ items: Array<Record<string, any>> }>(`/admin/gcs/metadata${query ? `?${query}` : ''}`);
}

export function fetchPromptLogs(limit = 20) {
  return request<{ logs: Array<Record<string, any>> }>(`/admin/prompt-logs?limit=${limit}`);
}

export function exportNotion(payload: { task_id?: TaskId; history_id?: string; parent_page_id?: string }) {
  return request<{ url: string }>('/pipeline/export/notion', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function searchDiscovery(query: string, maxResults = 5) {
  const params = new URLSearchParams();
  params.set('q', query);
  params.set('max_results', String(maxResults));
  return request<{ results: Array<Record<string, any>> }>(`/search/discovery?${params.toString()}`);
}

export function searchInsights(params: {
  query: string;
  max_results?: number;
  doc_type?: string;
  campaign_name?: string;
  channel?: string;
  region?: string;
  period_start?: string;
  period_end?: string;
}) {
  const search = new URLSearchParams();
  search.set('q', params.query);
  if (params.max_results) search.set('max_results', String(params.max_results));
  if (params.doc_type) search.set('doc_type', params.doc_type);
  if (params.campaign_name) search.set('campaign_name', params.campaign_name);
  if (params.channel) search.set('channel', params.channel);
  if (params.region) search.set('region', params.region);
  if (params.period_start) search.set('period_start', params.period_start);
  if (params.period_end) search.set('period_end', params.period_end);
  return request<InsightSearchResponse>(`/insights/search?${search.toString()}`);
}

export function generateDailyReport(payload: {
  query: string;
  max_results?: number;
  doc_type?: string | null;
  campaign_name?: string | null;
  channel?: string | null;
  region?: string | null;
  period_start?: string | null;
  period_end?: string | null;
  title?: string | null;
}) {
  return request<DailyReportResponse>('/insights/reports/daily', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function ingestNaverInsights(payload: {
  query: string;
  max_results?: number;
  include_products?: boolean;
  include_blogs?: boolean;
  include_news?: boolean;
  campaign_name?: string | null;
  channel?: string | null;
  region?: string | null;
  period_start?: string | null;
  period_end?: string | null;
}) {
  return request<NaverIngestResponse>('/insights/external/naver', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function fetchInsightMetrics(days = 7, actorRole?: string, teamId?: number) {
  const params = new URLSearchParams();
  params.set('days', String(days));
  if (actorRole) params.set('actor_role', actorRole);
  if (teamId) params.set('team_id', String(teamId));
  return request<InsightMetricsResponse>(`/insights/metrics?${params.toString()}`);
}

export function fetchInsightFailures(
  params: { days?: number; limit?: number; actor_role?: string; team_id?: number } = {},
) {
  const search = new URLSearchParams();
  if (params.days) search.set('days', String(params.days));
  if (params.limit) search.set('limit', String(params.limit));
  if (params.actor_role) search.set('actor_role', params.actor_role);
  if (params.team_id) search.set('team_id', String(params.team_id));
  const suffix = search.toString();
  return request<InsightFailuresResponse>(`/insights/failures${suffix ? `?${suffix}` : ''}`);
}

export function fetchInsightTeams() {
  return request<{ teams: ApiTypes.Team[] }>('/insights/teams');
}

export function fetchRoles() {
  return request<{ roles: ApiTypes.Role[] }>('/admin/roles');
}

export function createRole(payload: { name: string; description?: string | null }) {
  return request<ApiTypes.Role>('/admin/roles', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function fetchTeams() {
  return request<{ teams: ApiTypes.Team[] }>('/admin/teams');
}

export function createTeam(payload: { name: string }) {
  return request<ApiTypes.Team>('/admin/teams', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function fetchAuditLogs(limit = 50) {
  return request<{ logs: ApiTypes.AuditLog[] }>(`/admin/audit-logs?limit=${limit}`);
}

export function fetchThumbnailStyles() {
  return request<{ styles: ApiTypes.ThumbnailStyle[] }>('/thumbnail/styles');
}

export function generateHooks(payload: { product_name: string; style: string; count?: number }) {
  return request<{ hooks: string[] }>('/hooks/generate', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function generateThumbnailCompare(payload: {
  product_name: string;
  hook_text?: string;
  styles?: string[] | null;
  include_text_overlay?: boolean;
  max_styles?: number;
  auto_hook_per_style?: boolean;
}) {
  return request<{
    items: Array<{ style: string; name: string; url: string; gcs_path: GcsPath; hook_text: string }>;
    hook_text: string;
  }>('/thumbnail/compare-styles', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function fetchHookStyles() {
  return request<{
    styles: ApiTypes.HookStrategy[];
  }>('/hooks/styles');
}

export function fetchVideoPresets() {
  return request<ApiTypes.VideoPresets>('/video/presets');
}

export function generateVideo(payload: {
  product_name: string;
  hook_text: string;
  duration_seconds: number;
  resolution: string;
  camera_movement?: string;
  composition?: string;
  lighting_mood?: string;
  audio_preset?: string;
  sfx?: string[];
  ambient?: string | null;
}) {
  return request<{ url: string; gcs_path?: GcsPath; prompt: string }>('/video/generate', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function analyzeStrategy(taskId: TaskId) {
  return request<{ strategy: Record<string, any> }>('/pipeline/analysis/strategy', {
    method: 'POST',
    body: JSON.stringify({ task_id: taskId }),
  });
}

export function analyzeCommentsBasic(taskId: TaskId) {
  return request<{ analysis: Record<string, any> }>('/pipeline/analysis/comments/basic', {
    method: 'POST',
    body: JSON.stringify({ task_id: taskId }),
  });
}

export function analyzeCommentsDeep(taskId: TaskId) {
  return request<{ analysis: Record<string, any> }>('/pipeline/analysis/comments/deep', {
    method: 'POST',
    body: JSON.stringify({ task_id: taskId }),
  });
}

export function predictCtr(payload: {
  task_id: TaskId;
  title: string;
  thumbnail_description?: string;
  competitor_titles?: string[];
}) {
  return request<{ prediction: Record<string, any> }>('/pipeline/analysis/ctr-predict', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function login(payload: { email: Email; password: string }) {
  return request<{ token: string }>('/auth/login', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function signup(payload: any) {
    return request<{ token: string }>('/auth/signup', {
        method: 'POST',
        body: JSON.stringify(payload),
    });
}

export function sendChatMessage(payload: { message: string, session_id: string }) {
  return request<{ message: string; session_id?: string; card?: Record<string, any> }>('/chat', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function createLead(payload: { email: string }) {
    return request<{ status: string }>('/leads', {
        method: 'POST',
        body: JSON.stringify(payload),
    });
}

// ===== 스케줄 관리 API =====

/**
 * 스케줄 목록 조회
 */
export function fetchSchedules() {
  return request<Schedule[]>('/admin/schedules');
}

/**
 * 스케줄 생성
 */
export function createSchedule(payload: SchedulePayload) {
  return request<Schedule>('/admin/schedules', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

/**
 * 스케줄 수정
 */
export function updateSchedule(id: number, payload: SchedulePayload) {
  return request<Schedule>(`/admin/schedules/${id}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  });
}

/**
 * 스케줄 삭제
 */
export function deleteSchedule(id: number) {
  return request<{ message: string }>(`/admin/schedules/${id}`, {
    method: 'DELETE',
  });
}

/**
 * 스케줄 활성화/비활성화
 */
export function toggleSchedule(id: number, enabled: boolean) {
  return request<{ message: string }>(`/admin/schedules/${id}/toggle`, {
    method: 'PATCH',
    body: JSON.stringify({ enabled }),
  });
}
