import PipelineSlugClient from '@/components/PipelineSlugClient';
import { pipelineSlugs } from '@/lib/slugs';
import { fetchThumbnailStyles, fetchHookStyles, fetchVideoPresets } from '@/lib/api';
import { Metadata } from 'next';

const slugsInfo: Record<string, { title: string }> = {
  'data-source': { title: 'Data Source' },
  'ai-prompt': { title: 'AI Prompt' },
  'create': { title: 'Create' },
  'distribution': { title: 'Distribution' },
  'thumbnail': { title: 'Thumbnail Studio' },
  'video': { title: 'Video Studio' },
};

export function generateStaticParams() {
  return pipelineSlugs.map((slug) => ({ slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const title = slugsInfo[slug]?.title || 'Pipeline';
  return {
    title: `${title} | NEXLOOP Pipeline`,
    description: `${title} pipeline step for AI content automation.`,
  };
}

export default async function PipelineSlugPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  
  let initialData: any = {};
  if (slug === 'thumbnail') {
    const [styles, hooks] = await Promise.all([fetchThumbnailStyles(), fetchHookStyles()]);
    initialData = { styles: styles?.styles || [], hookStrategies: hooks?.styles || [] };
  } else if (slug === 'video') {
    const presets = await fetchVideoPresets();
    initialData = { videoPresets: presets };
  }

  return <PipelineSlugClient slug={slug} initialData={initialData} />;
}
