'use client';

import { useEffect, useMemo, useState } from 'react';
import { Navbar } from '@/features/landing';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import {
  fetchInsightFailures,
  fetchInsightMetrics,
  fetchInsightTeams,
  generateDailyReport,
  ingestNaverInsights,
  searchInsights,
} from '@/lib/api';
import type {
  DailyReportResponse,
  InsightDoc,
  InsightFailureEvent,
  InsightMetricsResponse,
  NaverIngestResponse,
} from '@/types/insights';
import type { Team } from '@/types/api';

const docTypeOptions = [
  { value: '', label: 'All Types' },
  { value: 'internal_upload', label: 'Internal Upload' },
  { value: 'trend_search', label: 'Trend Search' },
  { value: 'social_trend', label: 'Social Trend' },
  { value: 'news_summary', label: 'News Summary' },
  { value: 'daily_report', label: 'Daily Report' },
];

const roleOptions = [
  { value: '', label: 'All Roles' },
  { value: 'admin', label: 'admin' },
  { value: 'editor', label: 'editor' },
  { value: 'viewer', label: 'viewer' },
];

export default function InsightsDashboardClient() {
  const [searchQuery, setSearchQuery] = useState('');
  const [maxResults, setMaxResults] = useState(20);
  const [docType, setDocType] = useState('');
  const [campaignName, setCampaignName] = useState('');
  const [channel, setChannel] = useState('');
  const [region, setRegion] = useState('');
  const [periodStart, setPeriodStart] = useState('');
  const [periodEnd, setPeriodEnd] = useState('');
  const [results, setResults] = useState<InsightDoc[]>([]);
  const [searchError, setSearchError] = useState('');
  const [searching, setSearching] = useState(false);

  const [reportQuery, setReportQuery] = useState('');
  const [reportTitle, setReportTitle] = useState('');
  const [reportResult, setReportResult] = useState<DailyReportResponse | null>(null);
  const [reporting, setReporting] = useState(false);
  const [reportError, setReportError] = useState('');

  const [naverQuery, setNaverQuery] = useState('');
  const [naverResult, setNaverResult] = useState<NaverIngestResponse | null>(null);
  const [naverError, setNaverError] = useState('');
  const [naverLoading, setNaverLoading] = useState(false);
  const [includeProducts, setIncludeProducts] = useState(true);
  const [includeBlogs, setIncludeBlogs] = useState(true);
  const [includeNews, setIncludeNews] = useState(true);

  const [metricsDays, setMetricsDays] = useState(7);
  const [metricsRole, setMetricsRole] = useState('');
  const [metricsTeamId, setMetricsTeamId] = useState('');
  const [metrics, setMetrics] = useState<InsightMetricsResponse | null>(null);
  const [metricsError, setMetricsError] = useState('');
  const [metricsLoading, setMetricsLoading] = useState(false);

  const [failureDays, setFailureDays] = useState(7);
  const [failureLimit, setFailureLimit] = useState(25);
  const [failureRole, setFailureRole] = useState('');
  const [failureTeamId, setFailureTeamId] = useState('');
  const [failures, setFailures] = useState<InsightFailureEvent[]>([]);
  const [failureError, setFailureError] = useState('');
  const [failureLoading, setFailureLoading] = useState(false);

  const [teams, setTeams] = useState<Team[]>([]);
  const [teamsError, setTeamsError] = useState('');

  const loadMetrics = async () => {
    setMetricsError('');
    setMetricsLoading(true);
    try {
      const teamId = metricsTeamId ? Number(metricsTeamId) : undefined;
      const data = await fetchInsightMetrics(
        metricsDays,
        metricsRole || undefined,
        teamId,
      );
      setMetrics(data);
    } catch (err: any) {
      setMetricsError(err?.message || 'Metrics fetch failed.');
    } finally {
      setMetricsLoading(false);
    }
  };

  const loadFailures = async () => {
    setFailureError('');
    setFailureLoading(true);
    try {
      const teamId = failureTeamId ? Number(failureTeamId) : undefined;
      const data = await fetchInsightFailures({
        days: failureDays,
        limit: failureLimit,
        actor_role: failureRole || undefined,
        team_id: teamId,
      });
      setFailures(data.items || []);
    } catch (err: any) {
      setFailureError(err?.message || 'Failure fetch failed.');
    } finally {
      setFailureLoading(false);
    }
  };

  useEffect(() => {
    void loadMetrics();
    void loadFailures();
    fetchInsightTeams()
      .then((data) => {
        setTeams(data.teams || []);
      })
      .catch((err: any) => {
        setTeamsError(err?.message || 'Team fetch failed.');
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const topFailureReasons = useMemo(() => {
    const counts = new Map<string, number>();
    for (const item of failures) {
      const metadata = item.metadata || {};
      let reason = '';
      if (typeof metadata.reason === 'string' && metadata.reason.trim()) {
        reason = metadata.reason.trim();
      } else if (typeof metadata.error === 'string' && metadata.error.trim()) {
        reason = metadata.error.trim().split('\n')[0];
      } else {
        reason = 'unknown';
      }
      counts.set(reason, (counts.get(reason) || 0) + 1);
    }
    return Array.from(counts.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3)
      .map(([reason, count]) => ({ reason, count }));
  }, [failures]);

  const retryRecommendations = useMemo(() => {
    const mapReason = (reason: string) => {
      const normalized = reason.toLowerCase();
      if (normalized.includes('ingested_zero')) {
        return '업서트 결과 0건. 데이터스토어/권한/필터 확인 후 지수 백오프 재시도.';
      }
      if (normalized.includes('permission') || normalized.includes('403')) {
        return '권한/서비스 계정 확인. 재시도는 제한하고 관리자 확인 후 진행.';
      }
      if (normalized.includes('quota') || normalized.includes('429')) {
        return '쿼터/레이트리밋. 재시도 간격 확대 및 야간 배치 권장.';
      }
      if (normalized.includes('timeout') || normalized.includes('deadline')) {
        return '타임아웃. 백오프 + 최대 재시도 횟수 상향 고려.';
      }
      if (normalized.includes('network') || normalized.includes('connection')) {
        return '네트워크 오류. 짧은 백오프 재시도 후 실패 시 큐 적재.';
      }
      return '기본: 1~3회 지수 백오프 후 다음 배치 재시도.';
    };
    return topFailureReasons.map((item) => ({
      reason: item.reason,
      recommendation: mapReason(item.reason),
    }));
  }, [topFailureReasons]);

  const handleSearch = async () => {
    setSearchError('');
    if (!searchQuery.trim()) {
      setSearchError('Search query is required.');
      return;
    }
    setSearching(true);
    try {
      const data = await searchInsights({
        query: searchQuery.trim(),
        max_results: maxResults,
        doc_type: docType || undefined,
        campaign_name: campaignName || undefined,
        channel: channel || undefined,
        region: region || undefined,
        period_start: periodStart || undefined,
        period_end: periodEnd || undefined,
      });
      setResults(data.results || []);
    } catch (err: any) {
      setSearchError(err?.message || 'Search failed.');
    } finally {
      setSearching(false);
    }
  };

  const handleReport = async () => {
    setReportError('');
    const query = reportQuery.trim() || searchQuery.trim();
    if (!query) {
      setReportError('Report query is required.');
      return;
    }
    setReporting(true);
    try {
      const data = await generateDailyReport({
        query,
        max_results: maxResults,
        doc_type: docType || null,
        campaign_name: campaignName || null,
        channel: channel || null,
        region: region || null,
        period_start: periodStart || null,
        period_end: periodEnd || null,
        title: reportTitle || null,
      });
      setReportResult(data);
    } catch (err: any) {
      setReportError(err?.message || 'Report generation failed.');
    } finally {
      setReporting(false);
    }
  };

  const handleNaverIngest = async () => {
    setNaverError('');
    if (!naverQuery.trim()) {
      setNaverError('Naver query is required.');
      return;
    }
    setNaverLoading(true);
    try {
      const data = await ingestNaverInsights({
        query: naverQuery.trim(),
        max_results: Math.min(maxResults, 50),
        include_products: includeProducts,
        include_blogs: includeBlogs,
        include_news: includeNews,
        campaign_name: campaignName || null,
        channel: channel || null,
        region: region || null,
        period_start: periodStart || null,
        period_end: periodEnd || null,
      });
      setNaverResult(data);
    } catch (err: any) {
      setNaverError(err?.message || 'Naver ingest failed.');
    } finally {
      setNaverLoading(false);
    }
  };

  return (
    <>
      <Navbar />
      <main className="min-h-screen bg-[var(--color-background)] p-6 pt-24">
        <div className="max-w-6xl mx-auto space-y-6">
          <div className="grid gap-6 lg:grid-cols-2">
            <Card className="p-6 space-y-4">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <p className="text-sm text-[var(--color-muted)]">Insights Metrics</p>
                  <h2 className="text-xl font-bold">Activity Summary</h2>
                </div>
                <div className="flex flex-wrap items-center gap-2">
                  <Input
                    type="number"
                    min={1}
                    max={90}
                    value={metricsDays}
                    onChange={(e) => setMetricsDays(Number(e.target.value))}
                  />
                  <select
                    className="h-12 rounded-[var(--radius-md)] border border-[var(--color-border)] bg-white px-3 text-sm"
                    value={metricsRole}
                    onChange={(e) => setMetricsRole(e.target.value)}
                  >
                    {roleOptions.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                  <select
                    className="h-12 rounded-[var(--radius-md)] border border-[var(--color-border)] bg-white px-3 text-sm"
                    value={metricsTeamId}
                    onChange={(e) => setMetricsTeamId(e.target.value)}
                  >
                    <option value="">All Teams</option>
                    {teams.map((team) => (
                      <option key={team.id} value={String(team.id)}>
                        {team.name}
                      </option>
                    ))}
                  </select>
                  <Button type="button" onClick={loadMetrics} disabled={metricsLoading}>
                    {metricsLoading ? 'Loading...' : 'Refresh'}
                  </Button>
                </div>
              </div>
              {teamsError && (
                <p className="text-sm text-[var(--color-destructive)]">{teamsError}</p>
              )}
              {metricsError && (
                <p className="text-sm text-[var(--color-destructive)]">{metricsError}</p>
              )}
              {metrics ? (
                <div className="space-y-3 text-sm">
                  <div className="text-[var(--color-muted)]">
                    Window: {metrics.window_days} days · Total events: {metrics.total}
                  </div>
                  <div className="space-y-2">
                    {metrics.by_action.map((item) => (
                      <div
                        key={item.action}
                        className="flex items-center justify-between rounded-[var(--radius-md)] border border-[var(--color-border)] px-3 py-2"
                      >
                        <span className="font-medium">{item.action}</span>
                        <span className="text-[var(--color-muted)]">
                          {item.count} · {item.last_seen || 'n/a'}
                        </span>
                      </div>
                    ))}
                    {metrics.by_action.length === 0 && (
                      <div className="text-[var(--color-muted)]">No events yet.</div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="text-sm text-[var(--color-muted)]">No metrics loaded.</div>
              )}
            </Card>

            <Card className="p-6 space-y-4">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <p className="text-sm text-[var(--color-muted)]">Failure Events</p>
                  <h2 className="text-xl font-bold">Ingestion Alerts</h2>
                </div>
                <div className="flex flex-wrap items-center gap-2">
                  <Input
                    type="number"
                    min={1}
                    max={90}
                    value={failureDays}
                    onChange={(e) => setFailureDays(Number(e.target.value))}
                  />
                  <Input
                    type="number"
                    min={1}
                    max={200}
                    value={failureLimit}
                    onChange={(e) => setFailureLimit(Number(e.target.value))}
                  />
                  <select
                    className="h-12 rounded-[var(--radius-md)] border border-[var(--color-border)] bg-white px-3 text-sm"
                    value={failureRole}
                    onChange={(e) => setFailureRole(e.target.value)}
                  >
                    {roleOptions.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                  <select
                    className="h-12 rounded-[var(--radius-md)] border border-[var(--color-border)] bg-white px-3 text-sm"
                    value={failureTeamId}
                    onChange={(e) => setFailureTeamId(e.target.value)}
                  >
                    <option value="">All Teams</option>
                    {teams.map((team) => (
                      <option key={team.id} value={String(team.id)}>
                        {team.name}
                      </option>
                    ))}
                  </select>
                  <Button type="button" onClick={loadFailures} disabled={failureLoading}>
                    {failureLoading ? 'Loading...' : 'Refresh'}
                  </Button>
                </div>
              </div>
              {failureError && (
                <p className="text-sm text-[var(--color-destructive)]">{failureError}</p>
              )}
              <div className="space-y-3 text-sm">
                {topFailureReasons.length > 0 && (
                  <div className="rounded-[var(--radius-md)] border border-[var(--color-border)] p-3">
                    <div className="text-xs text-[var(--color-muted)] mb-2">
                      Top Failure Reasons
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {topFailureReasons.map((item) => (
                        <span
                          key={item.reason}
                          className="rounded-full bg-[var(--color-muted-bg)] px-3 py-1 text-xs text-[var(--color-muted)]"
                        >
                          {item.reason} ({item.count})
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                {retryRecommendations.length > 0 && (
                  <div className="rounded-[var(--radius-md)] border border-[var(--color-border)] p-3">
                    <div className="text-xs text-[var(--color-muted)] mb-2">
                      Retry Policy Suggestions
                    </div>
                    <div className="space-y-2 text-xs text-[var(--color-muted)]">
                      {retryRecommendations.map((item) => (
                        <div key={item.reason}>
                          <span className="font-semibold text-[var(--color-primary)]">
                            {item.reason}
                          </span>
                          {': '}
                          {item.recommendation}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                {failures.map((item) => (
                  <div key={item.id} className="soft-section p-3 rounded-[var(--radius-md)]">
                    <div className="flex flex-wrap items-center gap-2 text-xs text-[var(--color-muted)]">
                      <span>{item.action}</span>
                      <span>•</span>
                      <span>{item.created_at}</span>
                    </div>
                    <div className="text-sm mt-1">
                      {item.actor_email} ({item.actor_role})
                      {item.actor_team?.name ? ` · ${item.actor_team.name}` : ''}
                    </div>
                    {item.metadata && (
                      <pre className="mt-2 text-xs whitespace-pre-wrap text-[var(--color-muted)]">
                        {JSON.stringify(item.metadata, null, 2)}
                      </pre>
                    )}
                  </div>
                ))}
                {!failureLoading && failures.length === 0 && (
                  <div className="text-[var(--color-muted)]">No failure events.</div>
                )}
              </div>
            </Card>
          </div>

          <Card className="p-6 space-y-6">
            <div>
              <p className="font-bold text-[var(--color-primary)] mb-2">Insight Hub</p>
              <h1 className="text-3xl font-bold mb-2">Marketing Insights Dashboard</h1>
              <p className="text-sm text-[var(--color-muted)]">
                Search, ingest, and summarize insights to improve campaign outcomes.
              </p>
            </div>

            <div className="grid gap-4 lg:grid-cols-[2fr_1fr_1fr]">
              <Input
                placeholder="Search query"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              <Input
                type="number"
                min={1}
                max={50}
                value={maxResults}
                onChange={(e) => setMaxResults(Number(e.target.value))}
              />
              <select
                className="h-12 rounded-[var(--radius-md)] border border-[var(--color-border)] bg-white px-3 text-sm"
                value={docType}
                onChange={(e) => setDocType(e.target.value)}
              >
                {docTypeOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              <Input
                placeholder="Campaign name"
                value={campaignName}
                onChange={(e) => setCampaignName(e.target.value)}
              />
              <Input
                placeholder="Channel"
                value={channel}
                onChange={(e) => setChannel(e.target.value)}
              />
              <Input
                placeholder="Region"
                value={region}
                onChange={(e) => setRegion(e.target.value)}
              />
              <Input
                placeholder="Period start (YYYY-MM-DD)"
                value={periodStart}
                onChange={(e) => setPeriodStart(e.target.value)}
              />
              <Input
                placeholder="Period end (YYYY-MM-DD)"
                value={periodEnd}
                onChange={(e) => setPeriodEnd(e.target.value)}
              />
              <Button type="button" onClick={handleSearch} disabled={searching}>
                {searching ? 'Searching...' : 'Search Insights'}
              </Button>
            </div>

            {searchError && <p className="text-sm text-[var(--color-destructive)]">{searchError}</p>}

            <div className="space-y-3">
              <div className="text-sm text-[var(--color-muted)]">
                Results: {results.length}
              </div>
              {results.map((item, index) => (
                <div key={`${item.title}-${index}`} className="soft-section p-4 rounded-[var(--radius-md)]">
                  <div className="flex flex-wrap items-center gap-2 text-xs text-[var(--color-muted)] mb-2">
                    <span>{item.doc_type || 'n/a'}</span>
                    <span>•</span>
                    <span>{item.source || 'unknown source'}</span>
                    {item.channel && (
                      <>
                        <span>•</span>
                        <span>{item.channel}</span>
                      </>
                    )}
                  </div>
                  <h3 className="text-lg font-bold mb-1">{item.title || 'Untitled'}</h3>
                  <p className="text-sm text-[var(--color-muted)]">
                    {item.snippet || item.content || 'No summary available.'}
                  </p>
                </div>
              ))}
            </div>
          </Card>

          <div className="grid gap-6 lg:grid-cols-2">
            <Card className="p-6 space-y-4">
              <h2 className="text-xl font-bold">Daily Report</h2>
              <Input
                placeholder="Report query (defaults to search query)"
                value={reportQuery}
                onChange={(e) => setReportQuery(e.target.value)}
              />
              <Input
                placeholder="Report title"
                value={reportTitle}
                onChange={(e) => setReportTitle(e.target.value)}
              />
              <Button type="button" onClick={handleReport} disabled={reporting}>
                {reporting ? 'Generating...' : 'Generate Report'}
              </Button>
              {reportError && <p className="text-sm text-[var(--color-destructive)]">{reportError}</p>}
              {reportResult?.report && (
                <div className="soft-section p-4 rounded-[var(--radius-md)] text-sm whitespace-pre-wrap">
                  <strong>{reportResult.report.title}</strong>
                  <div className="mt-2">{reportResult.report.content}</div>
                  <div className="mt-3 text-xs text-[var(--color-muted)]">
                    Ingested: {reportResult.ingested} | Items: {reportResult.items}
                  </div>
                </div>
              )}
            </Card>

            <Card className="p-6 space-y-4">
              <h2 className="text-xl font-bold">Naver External Ingest</h2>
              <Input
                placeholder="Naver query"
                value={naverQuery}
                onChange={(e) => setNaverQuery(e.target.value)}
              />
              <div className="flex flex-wrap gap-3 text-sm">
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={includeProducts}
                    onChange={(e) => setIncludeProducts(e.target.checked)}
                  />
                  Shopping
                </label>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={includeBlogs}
                    onChange={(e) => setIncludeBlogs(e.target.checked)}
                  />
                  Blogs
                </label>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={includeNews}
                    onChange={(e) => setIncludeNews(e.target.checked)}
                  />
                  News
                </label>
              </div>
              <Button type="button" onClick={handleNaverIngest} disabled={naverLoading}>
                {naverLoading ? 'Ingesting...' : 'Ingest from Naver'}
              </Button>
              {naverError && <p className="text-sm text-[var(--color-destructive)]">{naverError}</p>}
              {naverResult && (
                <div className="soft-section p-4 rounded-[var(--radius-md)] text-sm">
                  <div>Ingested: {naverResult.ingested}</div>
                  <div>Items: {naverResult.items}</div>
                  <div>Shopping: {naverResult.products}</div>
                  <div>Blogs: {naverResult.blogs}</div>
                  <div>News: {naverResult.news}</div>
                </div>
              )}
            </Card>
          </div>
        </div>
      </main>
    </>
  );
}
