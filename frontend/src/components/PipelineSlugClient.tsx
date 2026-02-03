'use client';

import Link from 'next/link';
import { Navbar } from '@/features/landing';
import { Card, Button } from '@/components/ui';
import usePipeline from '@/hooks/usePipeline';
import { useAuth } from '@/components/AuthGate';
import { useThumbnailStudio } from '@/features/pipeline/hooks/useThumbnailStudio';
import { useVideoStudio } from '@/features/pipeline/hooks/useVideoStudio';
import { usePipelineApproval } from '@/features/pipeline/hooks/usePipelineApproval';
import { ThumbnailStudioSection } from '@/features/pipeline/components/ThumbnailStudioSection';
import { VideoStudioSection } from '@/features/pipeline/components/VideoStudioSection';
import { PipelineControlSection } from '@/features/pipeline/components/PipelineControlSection';
import { SnsContentSection } from '@/features/pipeline/components/SnsContentSection';
import { DUMMY_THUMBNAILS, DUMMY_VIDEO_URLS } from '@/lib/dummyData';

const slugs: Record<string, { title: string; subtitle: string }> = {
  'data-source': { title: 'Data Source', subtitle: 'Trend and information collection' },
  'ai-prompt': { title: 'AI Prompt', subtitle: 'Gemini-based prompt generation and optimization' },
  create: { title: 'Create', subtitle: 'AI thumbnail and short-form video automatic generation' },
  distribution: { title: 'Distribution', subtitle: 'Platform-specific optimized distribution' },
  thumbnail: { title: 'Thumbnail Studio', subtitle: '스타일 비교 (훅 테스트 포함, 9종)' },
  video: { title: 'Video Studio', subtitle: 'AI video generation with prompt presets' },
};

type PipelineSlugClientProps = {
  slug: string;
  initialData?: any;
};

export default function PipelineSlugClient({ slug, initialData }: PipelineSlugClientProps) {
  const item = slugs[slug];
  const { role } = useAuth();
  const pipeline = usePipeline();
  
  const thumbStudio = useThumbnailStudio({
    selectedProduct: pipeline.selectedProduct,
    initialStyles: initialData?.styles,
    initialHookStrategies: initialData?.hookStrategies,
  });

  const videoStudio = useVideoStudio({
    selectedProduct: pipeline.selectedProduct,
    initialVideoPresets: initialData?.videoPresets,
  });

  const approval = usePipelineApproval({
    taskId: pipeline.taskId || (pipeline.pipelineResult as any)?.status?.task_id || '',
    role: role || '',
    initialApprovalStatus: (pipeline.pipelineResult as any)?.result?.approval_status,
  });

  if (!item) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <h1 className="text-4xl font-bold">Not Found</h1>
        <Button asChild className="mt-4"><Link href="/">Back Home</Link></Button>
      </div>
    );
  }

  // Common Layout for non-studio slugs
  if (slug !== 'create' && slug !== 'thumbnail' && slug !== 'video') {
    return (
      <>
        <Navbar />
        <main className="min-h-screen bg-[var(--color-background)] p-8 pt-24">
          <Card className="max-w-2xl mx-auto text-center p-8">
            <h1 className="text-3xl font-bold">{item.title}</h1>
            <p className="mt-2 text-[var(--color-muted)]">{item.subtitle}</p>
            <Button asChild variant="secondary" className="mt-8"><Link href="/">Back Home</Link></Button>
          </Card>
        </main>
      </>
    );
  }

  return (
    <>
      <Navbar />
      <main className="min-h-screen bg-[var(--color-background)] p-8 pt-24">
        <div className="max-w-5xl mx-auto space-y-8">
          <header>
            <p className="font-bold text-[var(--color-primary)]">Pipeline</p>
            <h1 className="text-4xl font-bold">{item.title}</h1>
            <p className="text-lg text-[var(--color-muted)]">{item.subtitle}</p>
          </header>

          {slug === 'thumbnail' && (
            <ThumbnailStudioSection
              {...thumbStudio}
              products={pipeline.products}
              selectedProduct={pipeline.selectedProduct}
              setSelectedProduct={pipeline.setSelectedProduct}
            />
          )}

          {slug === 'video' && (
            <VideoStudioSection
              {...videoStudio}
              products={pipeline.products}
              selectedProduct={pipeline.selectedProduct}
              setSelectedProduct={pipeline.setSelectedProduct}
            />
          )}

          {(slug === 'create' || (slug !== 'thumbnail' && slug !== 'video')) && (
            <PipelineControlSection
              {...pipeline}
              {...approval}
              progressPercent={pipeline.pipelineStatus?.progress?.percentage ?? 0}
            />
          )}

          {/* Results section */}
          <div className="grid gap-6 md:grid-cols-2">
            <Card className="p-6 md:col-span-2">
              <h2 className="text-xl font-bold mb-4">SNS 소재</h2>
              <SnsContentSection socialPosts={pipeline.socialPosts} />
            </Card>
            <Card className="p-6">
              <h2 className="text-xl font-bold mb-4">Thumbnails</h2>
              <div className="grid grid-cols-2 gap-3">
                {(pipeline.thumbnails.length ? pipeline.thumbnails : DUMMY_THUMBNAILS).map((url, i) => (
                  <img key={i} src={url} alt="thumb" className="w-full aspect-[9/16] object-cover rounded-md" />
                ))}
              </div>
            </Card>
            <Card className="p-6">
              <h2 className="text-xl font-bold mb-4">Videos</h2>
              <div className="space-y-4">
                {(pipeline.videoUrls.length ? pipeline.videoUrls : DUMMY_VIDEO_URLS).map((url, i) => (
                  <video key={i} src={url} controls className="w-full rounded-md" />
                ))}
              </div>
            </Card>
          </div>
        </div>
      </main>
    </>
  );
}
