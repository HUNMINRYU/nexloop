'use client';

import React from 'react';
import Link from 'next/link';
import { Card } from '@/components/ui/Card';

export default function VideoMessageSection() {
  return (
    <section className="relative py-24 md:py-32 px-6 md:px-12 border-t border-[var(--color-border)] bg-gradient-to-br from-[#0ca678]/5 via-[var(--color-background)] to-[#6366f1]/5 overflow-hidden">
      <div className="absolute -top-32 -right-32 w-96 h-96 rounded-full bg-[#6366f1]/10 blur-[120px]" aria-hidden />
      <div className="absolute -bottom-32 -left-32 w-96 h-96 rounded-full bg-[#0ca678]/10 blur-[120px]" aria-hidden />
      
      <div className="relative max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12 md:gap-20 items-center">
        {/* Left: Video / Visual Container - 9:16 portrait */}
        <div className="relative transform hover:rotate-1 transition-transform duration-700">
          <Card className="rounded-[var(--radius-xl)] overflow-hidden bg-white/40 backdrop-blur-xl border border-white/40 p-5 md:p-8 shadow-2xl w-full max-w-[360px] mx-auto lg:mx-0">
            <div className="flex items-center gap-2 mb-6">
              <Link href="/" className="text-2xl font-black tracking-tighter">
                NEX<span className="text-transparent bg-clip-text bg-gradient-to-r from-[#0ca678] to-[#6366f1]">LOOP</span>
              </Link>
            </div>
            {/* Video / Graphic Area - 9:16 portrait (stable image) */}
            <div className="relative aspect-[9/16] w-full rounded-[var(--radius-lg)] overflow-hidden bg-slate-100 border border-[var(--color-border)] shadow-inner">
              <img
                src="https://picsum.photos/360/640?seed=intro"
                alt="Introducing NEXLOOP"
                className="absolute inset-0 w-full h-full object-cover transition-transform duration-1000 hover:scale-110"
              />
              <div className="absolute inset-0 bg-black/20 group-hover:bg-black/10 transition-colors" />
              <div className="absolute bottom-6 right-6 w-16 h-16 rounded-full bg-white/20 backdrop-blur-md border border-white/40 flex items-center justify-center text-white font-black text-xs tracking-widest shadow-lg hover:scale-110 transition-transform cursor-pointer">
                PLAY
              </div>
            </div>
          </Card>
        </div>

        {/* Right: Message - primary color */}
        <div className="relative">
          <Card className="rounded-[var(--radius-xl)] bg-gradient-to-br from-[#1e293b] to-[#0f172a] border border-white/10 p-8 md:p-16 flex flex-col justify-center min-h-[400px] text-white shadow-2xl overflow-hidden group">
            <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-[#0ca678]/20 to-transparent blur-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-1000" />
            
            <h2 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-black leading-tight mb-6 md:mb-8 tracking-tighter">
              Our<br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#0ca678] to-[#6366f1]">Pipeline</span><br />
              <span className="inline-block mt-2 relative">
                Never sleep!
                <div className="absolute -bottom-2 left-0 w-full h-2 bg-[#0ca678] rounded-full transform scale-x-105" />
              </span>
            </h2>
            <p className="text-lg md:text-2xl font-medium text-slate-300 max-w-lg leading-relaxed">
              Set your goals. Let Gemini's machine intelligence bridge the gap between concept and creation.
            </p>
          </Card>
        </div>
      </div>
    </section>
  );
}
