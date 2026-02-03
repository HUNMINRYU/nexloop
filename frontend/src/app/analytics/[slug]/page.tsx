import AnalyticsSlugClient from '@/components/AnalyticsSlugClient';
import { analyticsSlugs } from '@/lib/slugs';
import { Metadata } from 'next';

const slugsInfo: Record<string, { title: string }> = {
  performance: { title: 'Performance' },
  'ai-insights': { title: 'AI Insights' },
  audience: { title: 'Audience' },
};

export function generateStaticParams() {
  return analyticsSlugs.map((slug) => ({ slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const title = slugsInfo[slug]?.title || 'Analytics';
  return {
    title: `${title} | NEXLOOP Analytics`,
    description: `${title} analytics report for your AI generated content.`,
  };
}

export default async function AnalyticsSlugPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  return <AnalyticsSlugClient slug={slug} />;
}
