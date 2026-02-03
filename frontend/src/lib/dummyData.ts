/**
 * 미구현/API 미연동 시 UI 제작용 더미 데이터
 */

export const DUMMY_PRODUCTS = ['벅스델타', '글로우 세럼', '아쿠아 텀블러'];

export const DUMMY_PIPELINE_TASKS: Array<Record<string, any>> = [
  {
    task_id: 'dummy-task-1',
    product: '벅스델타',
    status: 'success',
    executed_at: new Date().toISOString(),
  },
  {
    task_id: 'dummy-task-2',
    product: '글로우 세럼',
    status: 'success',
    executed_at: new Date(Date.now() - 86400000).toISOString(),
  },
  {
    task_id: 'dummy-task-3',
    product: '아쿠아 텀블러',
    status: 'success',
    executed_at: new Date(Date.now() - 172800000).toISOString(),
  },
];

/** placeholder 이미지 (9:16 썸네일용) */
export const DUMMY_THUMBNAIL_PLACEHOLDER = 'https://placehold.co/360x640/e5e5e5/737373?text=Thumbnail';
/** placeholder 비디오용 이미지 (재생 아이콘 오버레이용) */
export const DUMMY_VIDEO_PLACEHOLDER = 'https://placehold.co/360x640/171717/ffffff?text=Video';

export const DUMMY_THUMBNAILS = [
  DUMMY_THUMBNAIL_PLACEHOLDER,
  'https://placehold.co/360x640/f4f4f5/71717a?text=Sample+1',
  'https://placehold.co/360x640/e4e4e7/71717a?text=Sample+2',
];

export const DUMMY_VIDEO_URLS = [DUMMY_VIDEO_PLACEHOLDER];

export const DUMMY_AUDIT_LOGS: Array<Record<string, any>> = [
  {
    id: 'dummy-log-1',
    action: 'pipeline.run',
    actor_email: 'admin@example.com',
    actor_role: 'admin',
    entity_type: 'pipeline',
    entity_id: 'task-001',
    created_at: new Date().toISOString(),
    metadata: JSON.stringify({ product: '벅스델타', status: 'success' }, null, 2),
  },
  {
    id: 'dummy-log-2',
    action: 'thumbnail.compare',
    actor_email: 'user@example.com',
    actor_role: 'user',
    entity_type: 'thumbnail',
    entity_id: 'compare-001',
    created_at: new Date(Date.now() - 3600000).toISOString(),
    metadata: null,
  },
  {
    id: 'dummy-log-3',
    action: 'video.generate',
    actor_email: 'user@example.com',
    actor_role: 'user',
    entity_type: 'video',
    entity_id: 'video-001',
    created_at: new Date(Date.now() - 7200000).toISOString(),
    metadata: JSON.stringify({ duration: 15, resolution: '720p' }, null, 2),
  },
];

export const DUMMY_DISCOVERY_RESULTS: Array<Record<string, any>> = [
  {
    title: '샘플 문서: AI 파이프라인 개요',
    snippet: 'Gemini 기반 자동화 파이프라인으로 썸네일·숏폼 비디오를 생성하고 분석합니다.',
    url: 'https://example.com/doc1',
  },
  {
    title: '샘플 문서: 썸네일 스타일 가이드',
    snippet: '9종 스타일 비교 및 훅 테스트를 통한 전환율 개선 사례.',
    url: 'https://example.com/doc2',
  },
  {
    title: '샘플 문서: VEO 3.1 비디오 생성',
    snippet: '프롬프트 프리셋과 카메라/구도/조명 옵션으로 일관된 톤의 영상을 제작합니다.',
    url: 'https://example.com/doc3',
  },
];

export const DUMMY_PROMPT_LOGS: Array<Record<string, any>> = [
  {
    history_id: 'dummy-history-1',
    product_name: '벅스델타',
    executed_at: new Date().toISOString(),
    prompt_log: { step: 'thumbnail', style: 'neobrutalism', hook_text: '벌레 컷.' },
  },
  {
    history_id: 'dummy-history-2',
    product_name: '글로우 세럼',
    executed_at: new Date(Date.now() - 86400000).toISOString(),
    prompt_log: { step: 'video', duration: 15, resolution: '720p' },
  },
];

export const DUMMY_ANALYTICS = {
  visibility: 12,
  ctrPrecision: 4.2,
  sentiment: '긍정',
};
