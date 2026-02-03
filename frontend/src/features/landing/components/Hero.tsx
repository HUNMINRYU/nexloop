"use client";

import React from "react";
import { Tooltip } from "@/components/ui";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";

type HeroProps = {
  demoUrl: string;
};

export default function Hero({ demoUrl }: HeroProps) {
  return (
    <section className="relative pt-32 pb-20 px-8 bg-[var(--color-background)] min-h-screen flex flex-col items-center justify-center text-center overflow-hidden">
      {/* Background Video */}
      <video
        autoPlay
        loop
        muted
        playsInline
        className="absolute inset-0 w-full h-full object-cover pointer-events-none z-0"
      >
        <source src="/videos/Video.mp4" type="video/mp4" />
      </video>

      {/* Dark Overlay for Readability */}
      <div className="absolute inset-0 bg-black/40 z-[1] pointer-events-none"></div>

      {/* Background Grid Pattern */}
      <div className="absolute inset-0 bg-grid opacity-20 z-[2] pointer-events-none"></div>

      <div className="relative z-10 max-w-4xl text-center">
        {/* Taglines with glow effect */}
        <p className="text-xl md:text-2xl font-bold text-white mb-3 px-4 py-1 bg-white/15 backdrop-blur-md border border-white/20 rounded-full w-fit mx-auto shadow-xl">
          From planning to analysis
        </p>
        <p className="text-xl md:text-2xl font-bold text-white mb-10 px-4 py-1 bg-white/15 backdrop-blur-md border border-white/20 rounded-full w-fit mx-auto shadow-xl">
          The beginning of seamless automation
        </p>
        {/* Brand title with heavy shadow */}
        <h1 className="text-5xl sm:text-7xl md:text-8xl lg:text-[9rem] font-black tracking-tighter mb-10 md:mb-12 leading-[0.9] drop-shadow-[0_10px_10px_rgba(0,0,0,0.5)] text-white px-4">
          NEX<span className="text-transparent bg-clip-text bg-gradient-to-r from-[#0ca678] via-[#6366f1] to-[#0ca678]">LOOP</span>
        </h1>
        <p className="text-lg sm:text-2xl font-medium mb-12 max-w-2xl mx-auto px-2 text-white/90">
          Set your goals, then let Gemini’s intelligence bridge the gap. Your
          video is already ready.
        </p>
        <div className="flex flex-col gap-4 sm:gap-6 items-center">
          <div className="flex flex-wrap gap-4 sm:gap-6 justify-center">
            {/* 3. 툴팁: 버튼 호버 시 짧은 설명 */}
            <Tooltip content="Start with NEXLOOP pipeline" position="bottom">
              <Button variant="default" className="text-xl px-8 py-4" disabled>
                Get Started
              </Button>
            </Tooltip>
            <Button asChild variant="secondary" className="text-xl px-8 py-4">
              <a href={demoUrl}>View Demo</a>
            </Button>
          </div>
        </div>
      </div>

      {/* Decorative Elements - 모바일: 1열·회전 없음, 데스크: 3열·회전 */}
      <div className="relative z-10 mt-12 md:mt-16 w-full max-w-5xl grid grid-cols-1 sm:grid-cols-3 gap-6 md:gap-8 px-2">
        <Card className="bg-white/10 backdrop-blur-md border-white/20 rotate-0 sm:rotate-[-2deg] p-5 md:p-7 min-h-[140px] text-white cursor-pointer hover:bg-white/20 hover:-translate-y-1 transition-all duration-300 group">
          <div className="w-9 h-9 rounded-full bg-[var(--color-primary)]/40 border border-white/20 mb-3 group-hover:scale-110 transition-transform" />
          <h3 className="font-bold text-lg md:text-xl mb-2">Gemini 3.0</h3>
          <p className="text-sm md:text-base text-white/70">
            Advanced AI Analysis
          </p>
        </Card>
        <Card className="bg-white/10 backdrop-blur-md border-white/20 rotate-0 sm:rotate-[1deg] p-5 md:p-7 min-h-[140px] text-white cursor-pointer hover:bg-white/20 hover:-translate-y-1 transition-all duration-300 group">
          <div className="w-9 h-9 rounded-full bg-[var(--color-navy)]/30 border border-white/20 mb-3 group-hover:scale-110 transition-transform" />
          <h3 className="font-bold text-lg md:text-xl mb-2">VEO 3.1</h3>
          <p className="text-sm md:text-base text-white/70">
            Video Generation Engine
          </p>
        </Card>
        <Card className="bg-white/10 backdrop-blur-md border-white/20 rotate-0 sm:rotate-[-1deg] p-5 md:p-7 min-h-[140px] text-white cursor-pointer hover:bg-white/20 hover:-translate-y-1 transition-all duration-300 group">
          <div className="w-9 h-9 rounded-full bg-[var(--color-accent)]/30 border border-white/20 mb-3 group-hover:scale-110 transition-transform" />
          <h3 className="font-bold text-lg md:text-xl mb-2 text-white">
            Real-time
          </h3>
          <p className="text-sm md:text-base text-white/70">
            Automated Pipeline
          </p>
        </Card>
      </div>
    </section>
  );
}
