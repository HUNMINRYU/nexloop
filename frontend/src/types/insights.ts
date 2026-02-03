export type InsightMetrics = {
  impressions?: number;
  clicks?: number;
  ctr?: number;
  cvr?: number;
  spend?: number;
  roi?: number;
};

export type InsightDoc = {
  title?: string;
  content?: string;
  snippet?: string;
  url?: string;
  doc_type?: string;
  source?: string;
  campaign_name?: string;
  channel?: string;
  region?: string;
  period_start?: string;
  period_end?: string;
  metrics?: InsightMetrics;
  tags?: string[];
  created_at?: string;
};

export type InsightSearchResponse = {
  query: string;
  results: InsightDoc[];
  count: number;
};

export type DailyReportResponse = {
  ingested: number;
  report: InsightDoc | null;
  items: number;
};

export type NaverIngestResponse = {
  ingested: number;
  items: number;
  products: number;
  blogs: number;
  news: number;
};

export type InsightMetricsByAction = {
  action: string;
  count: number;
  last_seen?: string | null;
};

export type InsightMetricsResponse = {
  window_days: number;
  total: number;
  by_action: InsightMetricsByAction[];
};

export type InsightFailureEvent = {
  id: number;
  action: string;
  actor_email: string;
  actor_role: string;
  entity_id?: string | null;
  actor_team?: { id: number; name: string } | null;
  metadata?: Record<string, any> | null;
  created_at: string;
};

export type InsightFailuresResponse = {
  window_days: number;
  items: InsightFailureEvent[];
};
