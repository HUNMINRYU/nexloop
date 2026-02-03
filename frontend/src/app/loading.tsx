'use client';

import React from 'react';

export default function Loading() {
  return (
    <div className="min-h-screen bg-white flex flex-col items-center justify-center p-6">
      {/* Premium Logo Loading Animation */}
      <div className="relative mb-12">
        <div className="text-4xl font-black tracking-tighter animate-pulse">
          NEX<span className="text-transparent bg-clip-text bg-gradient-to-r from-[#0ca678] to-[#6366f1]">LOOP</span>
        </div>
        <div className="absolute -bottom-4 left-0 right-0 h-1 bg-slate-50 rounded-full overflow-hidden">
          <div className="h-full bg-gradient-to-r from-[#0ca678] to-[#6366f1] w-1/3 animate-[loading_1.5s_infinite_ease-in-out]" />
        </div>
      </div>
      
      {/* Skeletons for Hero content */}
      <div className="w-full max-w-4xl space-y-8 animate-pulse">
        <div className="h-20 bg-slate-50 rounded-3xl w-3/4 mx-auto" />
        <div className="h-6 bg-slate-50 rounded-full w-1/2 mx-auto" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-12">
          <div className="h-40 bg-slate-50 rounded-[32px]" />
          <div className="h-40 bg-slate-50 rounded-[32px]" />
          <div className="h-40 bg-slate-50 rounded-[32px]" />
        </div>
      </div>

      <style jsx>{`
        @keyframes loading {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(300%); }
        }
      `}</style>
    </div>
  );
}
