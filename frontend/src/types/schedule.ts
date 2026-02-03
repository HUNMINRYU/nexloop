/**
 * 스케줄 관련 타입 정의
 */

export interface Schedule {
  id: number;
  name: string;
  description?: string;

  gcp_job_id: string;
  cron_expression: string;
  timezone: string;

  product_name: string;
  enabled: boolean;

  last_executed_at?: string;
  next_execution_at?: string;

  created_at: string;
  updated_at: string;
}

export interface SchedulePayload {
  name: string;
  description?: string;

  frequency: 'daily' | 'weekly' | 'custom';
  days_of_week: number[];  // 0=월, 6=일
  hour: number;
  minute: number;
  timezone: string;

  product_name: string;
  pipeline_config: {
    youtube_count: number;
    naver_count: number;
    include_comments: boolean;
    generate_social: boolean;
    generate_video: boolean;
    generate_thumbnails: boolean;
    export_to_notion: boolean;
    thumbnail_count?: number;
    thumbnail_styles?: string[];
  };
}
