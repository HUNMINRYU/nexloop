import dynamic from 'next/dynamic';
import React from 'react';

// 초기 로드에 필요한 핵심 컴포넌트
export { default as Navbar } from './components/Navbar';
export { default as Hero } from './components/Hero';

export const VideoMessageSection = dynamic(() => import('./components/VideoMessageSection'), {
  loading: () => <div className="h-96 bg-slate-50 animate-pulse rounded-3xl m-8" />
});

export const SliderMessageSection = dynamic(() => import('./components/SliderMessageSection'), {
  loading: () => <div className="h-96 bg-slate-50 animate-pulse rounded-3xl m-8" />
});

export const Features = dynamic(() => import('./components/Features'), {
  loading: () => <div className="h-96 bg-slate-50 animate-pulse rounded-3xl m-8" />
});

export const LeadCaptureSection = dynamic(() => import('./components/LeadCaptureSection'));

export const Footer = dynamic(() => import('./components/Footer'));
