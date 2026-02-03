import React from 'react';
import { 
  Navbar, 
  Hero, 
  VideoMessageSection, 
  SliderMessageSection, 
  Features, 
  LeadCaptureSection, 
  Footer 
} from '@/features/landing/index';
import { SLIDER_GIFS, SLIDER_IMAGES } from '@/features/landing/components/SliderMessageSection';

export default function Home() {
  return (
    <main className="min-h-screen bg-[var(--color-background)] selection:bg-[#0ca678] selection:text-white">
      <Navbar />
      
      <div className="relative">
        <Hero demoUrl="/pipeline/create" />
      </div>

      {/* Video + Message Section */}
      <VideoMessageSection />

      {/* 9:16 box - GIF 슬라이드 (Generate Video) */}
      <SliderMessageSection
        title="Generate Video, Don't Record"
        description="Your video is already ready. Let Gemini's automated pipeline uncover the best of your content."
        brandLabel="VEO 3.1"
        variant="green"
        images={SLIDER_GIFS}
      />

      {/* Social Proof / Stats Section - Glassmorphic Marquee */}
      <section className="relative py-16 overflow-hidden bg-[#0f172a] border-y border-white/5">
        <div className="absolute inset-0 bg-gradient-to-r from-[#0ca678]/10 via-transparent to-[#6366f1]/10 pointer-events-none" />
        <div className="flex whitespace-nowrap animate-marquee py-2">
          {[...Array(10)].map((_, i) => (
            <span key={i} className="flex items-center text-white/40 text-2xl font-black mx-12 uppercase tracking-[0.2em]">
              <span className="text-[#0ca678]">Gemini 3.0</span>
              <span className="mx-6 opacity-20">•</span>
              <span>Automated Pipeline</span>
              <span className="mx-6 opacity-20">•</span>
              <span className="text-[#6366f1]">VEO 3.1</span>
              <span className="mx-6 opacity-20">•</span>
              <span>Real-time Analysis</span>
              <span className="mx-6 opacity-30 ml-12">✦</span>
            </span>
          ))}
        </div>
      </section>

      {/* 9:16 box - 이미지 슬라이드 (Generate Thumbnail) */}
      <SliderMessageSection
        title="Generate thumbnail, Don't Edit"
        description="Set your goals, then let Gemini's machine intelligence bridge the gap between idea and engagement."
        brandLabel="Gemini 3.0"
        variant="cyan"
        images={SLIDER_IMAGES}
      />
      
      <Features />

      {/* CTA Section - Client Component */}
      <LeadCaptureSection />

      <Footer />
    </main>
  );
}
