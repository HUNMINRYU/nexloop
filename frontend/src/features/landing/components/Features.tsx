'use client';

import React, { useState, useEffect } from 'react';
import PersonWithBubble from './PersonWithBubble';
import { Card } from '@/components/ui/Card';

/* 패널별 서로 다른 이미지 세트 (정방형) */
const PANEL_IMAGES = {
  visibility: [
    'https://picsum.photos/400/400?seed=vis1',
    'https://picsum.photos/400/400?seed=vis2',
    'https://picsum.photos/400/400?seed=vis3',
  ],
  ctr: [
    'https://picsum.photos/400/400?seed=ctr1',
    'https://picsum.photos/400/400?seed=ctr2',
    'https://picsum.photos/400/400?seed=ctr3',
  ],
  sentiment: [
    'https://picsum.photos/400/400?seed=sen1',
    'https://picsum.photos/400/400?seed=sen2',
    'https://picsum.photos/400/400?seed=sen3',
  ],
};

const features = [
  {
    title: 'Visibility',
    color: 'bg-emerald-50/50',
    borderColor: 'border-emerald-100',
    titleColor: 'text-emerald-900',
    speech: "I've tracked how the algorithm finds your audience—your content is reaching the right eyes.",
    align: 'left' as const,
    images: PANEL_IMAGES.visibility,
  },
  {
    title: 'CTR Precision',
    color: 'bg-indigo-50/50',
    borderColor: 'border-indigo-100',
    titleColor: 'text-indigo-900',
    speech: "These frames drove the most clicks. Optimize thumbnails with real engagement data.",
    align: 'left' as const,
    images: PANEL_IMAGES.ctr,
  },
  {
    title: 'Audience Sentiment',
    color: 'bg-purple-50/50',
    borderColor: 'border-purple-100',
    titleColor: 'text-purple-900',
    speech: "Audience response and trend report. Here's a data-backed strategy for your next move.",
    align: 'right' as const,
    images: PANEL_IMAGES.sentiment,
  },
];

function PanelSlider({ images }: { images: string[] }) {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const id = setInterval(() => setIndex((i) => (i + 1) % images.length), 4000);
    return () => clearInterval(id);
  }, [images.length]);

  return (
    <Card className="rounded-[var(--radius-lg)] overflow-hidden bg-white border border-[var(--color-border)] shadow-xl aspect-square w-full relative group">
      <div
        className="flex h-full transition-transform duration-700 ease-in-out"
        style={{ transform: `translateX(-${index * 100}%)` }}
      >
        {images.map((src, i) => (
          <div key={i} className="min-w-full aspect-square relative flex-shrink-0">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={src} alt="" className="absolute inset-0 w-full h-full object-cover group-hover:scale-105 transition-transform duration-[2000ms]" />
          </div>
        ))}
      </div>
      <div className="absolute bottom-3 left-1/2 -translate-x-1/2 flex gap-1.5 p-1 bg-black/10 backdrop-blur-md rounded-full">
        {images.map((_, i) => (
          <button
            key={i}
            onClick={() => setIndex(i)}
            className={`w-1.5 h-1.5 rounded-full transition-all ${i === index ? 'bg-white w-4' : 'bg-white/40'}`}
            aria-label={`Slide ${i + 1}`}
          />
        ))}
      </div>
    </Card>
  );
}

function FlowArrow() {
  return (
    <div className="flex items-center justify-center text-slate-300 flex-shrink-0 animate-pulse" aria-hidden>
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" className="md:hidden" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 5v14M6 13l6 6 6-6" />
      </svg>
      <svg width="40" height="32" viewBox="0 0 28 24" fill="none" className="hidden md:block" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M4 12h20M16 6l6 6-6 6" />
      </svg>
    </div>
  );
}

export default function Features() {
  return (
    <section className="py-24 md:py-32 px-6 md:px-12 bg-white border-t border-[var(--color-border)] relative overflow-hidden" id="pipeline">
      <div className="absolute top-0 left-0 w-full h-64 bg-gradient-to-b from-[var(--color-background)] to-transparent opacity-50" />
      
      <div className="relative max-w-7xl mx-auto">
        <div className="text-center mb-16 md:mb-24">
          <h2 className="text-4xl md:text-6xl font-black mb-6 tracking-tighter">
            Core <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#0ca678] to-[#6366f1]">Pipeline</span>
          </h2>
          <div className="w-24 h-1.5 bg-gradient-to-r from-[#0ca678] to-[#6366f1] mx-auto rounded-full" />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-[1fr_auto_1fr_auto_1fr] gap-6 md:gap-4 items-center">
          {features.map((feature, panelIndex) => (
            <React.Fragment key={panelIndex}>
              <Card
                className={`${feature.color} ${feature.borderColor} rounded-[var(--radius-xl)] border p-4 md:p-6 flex flex-col gap-6 md:min-h-[600px] shadow-sm hover:shadow-xl transition-all duration-500 hover:-translate-y-2 group cursor-pointer`}
              >
                <h3 className={`text-xl md:text-2xl font-black ${feature.titleColor} text-center tracking-tight`}>
                  {feature.title}
                </h3>
                <div className="flex-1 flex flex-col justify-center">
                  <div className="w-full max-w-[280px] mx-auto">
                    <PanelSlider images={feature.images} />
                  </div>
                </div>
                <div className="flex justify-center min-h-[140px]">
                  <PersonWithBubble
                    text={feature.speech}
                    position="below"
                    align={feature.align}
                  />
                </div>
              </Card>
              {panelIndex < features.length - 1 && <FlowArrow />}
            </React.Fragment>
          ))}
        </div>
      </div>
    </section>
  );
}
