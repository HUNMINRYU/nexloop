'use client';

import Link from 'next/link';
import { Navbar } from '@/features/landing';
import { Card, Button } from '@/components/ui';
import { useAnalytics } from '@/features/pipeline/hooks/useAnalytics';
import { PerformanceSection, AiInsightsSection } from '@/features/pipeline/components/AnalyticsSections';

const slugs: Record<string, { title: string; subtitle: string }> = {
  performance: { title: 'Performance', subtitle: 'Click-through rate (CTR) and bounce rate data' },
  'ai-insights': { title: 'AI Insights', subtitle: 'Feedback and improvement plans for each video' },
  audience: { title: 'Audience', subtitle: 'Viewer response and trend analysis report' },
};

type AnalyticsSlugClientProps = {
  slug: string;
  initialData?: any;
};

export default function AnalyticsSlugClient({ slug, initialData }: AnalyticsSlugClientProps) {
  const item = slugs[slug];
  const analytics = useAnalytics(slug);

  if (!item) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <h1 className="text-4xl font-bold">Not Found</h1>
        <Button asChild className="mt-4"><Link href="/">Back Home</Link></Button>
      </div>
    );
  }

  return (
    <>
      <Navbar />
      <main className="min-h-screen bg-[var(--color-background)] p-8 pt-24">
        <div className="max-w-5xl mx-auto space-y-8">
          <header>
            <p className="font-bold text-[var(--color-primary)]">Analytics</p>
            <h1 className="text-4xl font-bold">{item.title}</h1>
            <p className="text-lg text-[var(--color-muted)]">{item.subtitle}</p>
          </header>

          {analytics.isLoading && <p className="text-sm text-[var(--color-muted)]">로딩 중...</p>}
          {analytics.error && <p className="text-sm text-red-500">{analytics.error}</p>}

          {slug === 'performance' && <PerformanceSection {...analytics} />}
          {slug === 'ai-insights' && <AiInsightsSection {...analytics} />}

          <div className="mt-8">
            <Button asChild variant="secondary"><Link href="/">Back to Home</Link></Button>
          </div>
        </div>
      </main>
    </>
  );
}
