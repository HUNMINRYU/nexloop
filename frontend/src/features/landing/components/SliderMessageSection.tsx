'use client';

import React, { useState, useEffect } from 'react';
import Image from 'next/image';
import { Card } from '@/components/ui/Card';

/* 9:16 portrait - 시뮬레이션 이미지 (Generate Video 섹션) */
export const SLIDER_GIFS = [
  'https://picsum.photos/360/640?seed=video1',
  'https://picsum.photos/360/640?seed=video2',
  'https://picsum.photos/360/640?seed=video3',
  'https://picsum.photos/360/640?seed=video4',
];

/* 9:16 portrait - 이미지용 (Generate Thumbnail 섹션) */
export const SLIDER_IMAGES = [
  'https://picsum.photos/360/640?seed=thumb1',
  'https://picsum.photos/360/640?seed=thumb2',
  'https://picsum.photos/360/640?seed=thumb3',
  'https://picsum.photos/360/640?seed=thumb4',
];

const DEFAULT_IMAGES = SLIDER_GIFS;

type SliderMessageSectionProps = {
  title: string;
  description: string;
  brandLabel?: string;
  images?: string[];
  /** 'green' = text left, box right. 'cyan' = box left, text right */
  variant?: 'green' | 'cyan';
};

export default function SliderMessageSection({
  title,
  description,
  brandLabel = 'VEO 3.1',
  images = DEFAULT_IMAGES,
  variant = 'green',
}: SliderMessageSectionProps) {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const id = setInterval(() => {
      setIndex((i) => (i + 1) % images.length);
    }, 4000);
    return () => clearInterval(id);
  }, [images.length]);

  const outerBoxClass =
    variant === 'green'
      ? `rounded-[var(--radius-xl)] border border-[var(--color-border)] p-6 bg-[var(--color-primary)]/10 backdrop-blur-sm shadow-[var(--shadow-soft-lg)]`
      : `rounded-[var(--radius-xl)] border border-[var(--color-border)] p-6 bg-[var(--color-accent)]/10 backdrop-blur-sm shadow-[var(--shadow-soft-lg)]`;

  /* 9:16 box beside text: textCol = left or right, boxCol = right or left */
  const textFirst = variant === 'green';
  const textOrder = textFirst ? 'order-2 lg:order-1' : 'order-2 lg:order-2';
  const boxOrder = textFirst ? 'order-1 lg:order-2' : 'order-1 lg:order-1';

  return (
    <section className="relative py-24 md:py-32 px-6 md:px-12 border-t border-[var(--color-border)] bg-[var(--color-background)] overflow-hidden">
      <div className="absolute -top-24 -right-16 w-96 h-96 rounded-full bg-[var(--color-accent)]/10 blur-[120px]" aria-hidden />
      <div className="absolute -bottom-24 -left-16 w-96 h-96 rounded-full bg-[var(--color-primary)]/10 blur-[120px]" aria-hidden />
      
      <div className="relative max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12 md:gap-20 items-center">
        {/* Text side */}
        <div className={`${textOrder} min-w-0`}>
          <h2 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-black mb-6 md:mb-8 text-[var(--color-foreground)] tracking-tight leading-tight">{title}</h2>
          <p className="text-lg md:text-2xl font-medium mb-8 md:mb-12 text-[var(--color-muted)] leading-relaxed">{description}</p>
          <div className="flex items-center gap-4 p-4 rounded-full bg-[var(--color-surface)] border border-[var(--color-border)] w-fit shadow-sm">
            <span className="relative w-8 h-8 flex-shrink-0">
              <Image
                src={variant === 'green' ? '/g-logo.png' : '/google-logo.png'}
                alt="Google"
                fill
                className="object-contain"
                sizes="32px"
              />
            </span>
            <span className="text-xl font-black text-[var(--color-foreground)] tracking-tighter">{brandLabel}</span>
          </div>
        </div>

        {/* 9:16 Slider box */}
        <div className={`${boxOrder} flex justify-center`}>
          <div className={`${outerBoxClass} w-full max-w-[360px] transform hover:scale-[1.02] transition-transform duration-500`}>
            <div className="rounded-[var(--radius-lg)] overflow-hidden bg-[var(--color-surface)] border border-[var(--color-border)] shadow-2xl aspect-[9/16] relative">
              <div
                className="flex h-full transition-transform duration-700 cubic-bezier(0.4, 0, 0.2, 1)"
                style={{ transform: `translateX(-${index * 100}%)` }}
              >
                {images.map((src, i) => (
                  <div key={i} className="min-w-full h-full relative flex-shrink-0">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img src={src} alt="" className="absolute inset-0 w-full h-full object-cover" />
                  </div>
                ))}
              </div>
              <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-3">
                {images.map((_, i) => (
                  <button
                    key={i}
                    onClick={() => setIndex(i)}
                    className={`w-2.5 h-2.5 rounded-full border border-white/50 transition-all ${i === index ? 'bg-white scale-125 w-6' : 'bg-white/30 hover:bg-white/50'}`}
                    aria-label={`Go to slide ${i + 1}`}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
