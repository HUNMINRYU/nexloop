'use client';

import React, { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import { Tooltip, Drawer, useToast, Button } from '@/components/ui';
import { useAuth } from '@/components/AuthGate';

import { usePathname } from 'next/navigation';

const pipelineItems = {
  left: [
    { title: 'Data Source', subtitle: 'Trend and information collection', href: '/pipeline/data-source' },
    { title: 'AI Prompt', subtitle: 'Gemini-based prompt generation and optimization', href: '/pipeline/ai-prompt' },
    { title: 'Create', subtitle: 'AI thumbnail and short-form video automatic generation', href: '/pipeline/create' },
  ],
  right: [
    { title: 'Thumbnail Studio', subtitle: '스타일 비교 · 단일 생성 · A/B 테스트 (12종)', href: '/pipeline/thumbnail' },
    { title: 'Video Studio', subtitle: 'AI 비디오 생성 및 프리셋', href: '/pipeline/video' },
    { title: 'Scheduler', subtitle: '파이프라인 자동 실행 스케줄 관리', href: '/admin/scheduler' },
    { title: 'Distribution', subtitle: 'Platform-specific optimized distribution', href: '/pipeline/distribution' },
  ],
};

const storageItems = {
  left: [
    { title: 'Video Vault', subtitle: 'Storage for completed short-form videos', href: '/storage/video-vault' },
    { title: 'Asset Library', subtitle: 'Storage for generated thumbnails and image sources', href: '/storage/asset-library' },
  ],
  right: [
    { title: 'Prompt Log', subtitle: 'Management of successful prompt history', href: '/storage/prompt-log' },
  ],
};

const analyticsItems = {
  left: [
    { title: 'Performance', subtitle: 'Click-through rate (CTR) and bounce rate data', href: '/analytics/performance' },
    { title: 'AI Insights', subtitle: 'Feedback and improvement plans for each video', href: '/analytics/ai-insights' },
  ],
  right: [
    { title: 'Audience', subtitle: 'Viewer response and trend analysis report', href: '/analytics/audience' },
    { title: 'Insights Hub', subtitle: 'Unified insight search and daily reports', href: '/insights' },
  ],
};

interface MenuItem {
  title: string;
  subtitle: string;
  href: string;
}



function MegaMenu({
  items,
  isOpen,
  onClose,
  onEnter,
  className,
}: {
  items: { left: MenuItem[]; right: MenuItem[] };
  isOpen: boolean;
  onClose: () => void;
  onEnter: () => void;
  className?: string;
}) {
  if (!isOpen) return null;
  return (
    <div
      className={`absolute top-full left-1/2 -translate-x-1/2 pt-4 z-50 ${className ?? ''}`}
      onMouseEnter={onEnter}
      onMouseLeave={onClose}
    >
      <div className="min-w-[520px] bg-white/90 backdrop-blur-xl flex rounded-2xl border border-white/40 shadow-2xl overflow-hidden p-2 transform origin-top animate-in fade-in zoom-in-95 duration-200">
        <div className="flex-1 p-2 space-y-1">
          {items.left.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="block p-4 rounded-xl border border-transparent hover:bg-slate-50 transition-all group"
            >
              <div className="font-bold text-slate-900 group-hover:text-[#0ca678] transition-colors">{item.title}</div>
              <div className="text-sm text-slate-500">{item.subtitle}</div>
            </Link>
          ))}
        </div>
        <div className="w-[1px] bg-slate-100 my-4" />
        <div className="flex-1 p-2 space-y-1">
          {items.right.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="block p-4 rounded-xl border border-transparent hover:bg-slate-50 transition-all group"
            >
              <div className="font-bold text-slate-900 group-hover:text-[#6366f1] transition-colors">{item.title}</div>
              <div className="text-sm text-slate-500">{item.subtitle}</div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}

type MenuKey = 'pipeline' | 'storage' | 'analytics' | null;

export default function Navbar() {
  const [openMenu, setOpenMenu] = useState<MenuKey>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const closeTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const toast = useToast();
  const { email: userEmail, role } = useAuth();
  const pathname = usePathname();
  const userInitial = userEmail ? userEmail[0]?.toUpperCase() : "U";

  // 랜딩 페이지가 아니거나 스크롤된 경우 다크 모드(흰 배경 + 검은 글씨) 적용
  const isLanding = pathname === '/';
  const showDarkNav = scrolled || !isLanding;

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleLogout = () => {
    if (typeof window === 'undefined') return;
    sessionStorage.removeItem('auth_token');
    window.location.href = '/login';
  };

  const clearCloseTimeout = () => {
    if (closeTimeoutRef.current) {
      clearTimeout(closeTimeoutRef.current);
      closeTimeoutRef.current = null;
    }
  };

  const scheduleClose = () => {
    clearCloseTimeout();
    closeTimeoutRef.current = setTimeout(() => setOpenMenu(null), 150);
  };

  const open = (key: MenuKey) => {
    clearCloseTimeout();
    setOpenMenu(key);
  };

  const [drawerExpanded, setDrawerExpanded] = useState<'pipeline' | 'storage' | 'analytics' | null>(null);

  const pipelineAll = [...pipelineItems.left, ...pipelineItems.right];
  const storageAll = [...storageItems.left, ...storageItems.right];
  const analyticsAll = [...analyticsItems.left, ...analyticsItems.right];

  return (
    <nav className={`fixed top-0 left-0 right-0 z-[100] transition-all duration-500 px-6 md:px-12 py-4 flex justify-between items-center ${showDarkNav ? 'bg-white/80 backdrop-blur-2xl border-b border-slate-100 shadow-[0_4px_30px_rgba(0,0,0,0.03)] py-3' : 'bg-transparent'}`}>
      <Link href="/" className="text-2xl font-black tracking-tighter flex items-center group cursor-pointer">
        <span className={`${showDarkNav ? 'text-slate-900' : 'text-white'} transition-colors duration-500`}>NEX</span>
        <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#0ca678] to-[#6366f1] group-hover:from-[#6366f1] group-hover:to-[#0ca678] transition-all duration-1000">LOOP</span>
      </Link>

      {/* 데스크톱 메뉴 */}
      <div className="hidden lg:flex gap-2 items-center">
        {[
          { key: 'pipeline', label: 'Pipeline', items: pipelineItems },
          { key: 'storage', label: 'Storage', items: storageItems },
          { key: 'analytics', label: 'Analytics', items: analyticsItems },
        ].map((menu) => (
          <div
            key={menu.key}
            className="relative"
            onMouseEnter={() => open(menu.key as MenuKey)}
            onMouseLeave={scheduleClose}
          >
            <button
              type="button"
              className={`px-5 py-2 font-bold tracking-tight transition-all rounded-full hover:bg-white/10 ${openMenu === menu.key ? 'text-[#0ca678]' : showDarkNav ? 'text-slate-600' : 'text-white/80'} hover:text-[#0ca678]`}
            >
              {menu.label}
            </button>
            <MegaMenu
              items={menu.items}
              isOpen={openMenu === menu.key}
              onClose={scheduleClose}
              onEnter={() => open(menu.key as MenuKey)}
            />
          </div>
        ))}
      </div>

      <div className="flex items-center gap-4">
        <div className="hidden lg:flex gap-4 items-center">
          {userEmail ? (
            <>
              <span className={`font-bold text-sm ${showDarkNav ? 'text-slate-400' : 'text-white/50'}`}>{userEmail}</span>
              <Button variant={showDarkNav ? "outline" : "secondary"} className="rounded-full font-bold h-10 px-6" onClick={handleLogout}>Log Out</Button>
            </>
          ) : (
            <>
              <Link href="/login">
                <Button variant="ghost" className={`font-bold rounded-full h-10 px-6 ${showDarkNav ? 'text-slate-600' : 'text-white hover:bg-white/10'}`}>Log In</Button>
              </Link>
              <Link href="/signup">
                <Button className="font-bold rounded-full h-10 px-6 bg-[#0f172a] hover:bg-[#1e293b] text-white shadow-xl">Sign Up</Button>
              </Link>
            </>
          )}
        </div>

        {/* 모바일 햄버거 버튼 */}
        <button
          type="button"
          onClick={() => setDrawerOpen(true)}
          className={`lg:hidden w-11 h-11 rounded-full border flex flex-col items-center justify-center gap-1.5 transition-all ${showDarkNav ? 'bg-slate-900 border-slate-800 text-white' : 'bg-white/10 border-white/20 text-white backdrop-blur-md'}`}
          aria-label="메뉴 열기"
        >
          <span className="w-5 h-0.5 bg-current rounded-full" />
          <span className="w-5 h-0.5 bg-current rounded-full opacity-70" />
          <span className="w-5 h-0.5 bg-current rounded-full" />
        </button>
      </div>

      <Drawer open={drawerOpen} onClose={() => { setDrawerOpen(false); setDrawerExpanded(null); }} side="right" title="NEXLOOP Menu">
        <div className="space-y-6 pt-4">
          {[
            { key: 'pipeline' as const, label: 'Pipeline', items: pipelineAll, color: 'text-[#0ca678]' },
            { key: 'storage' as const, label: 'Storage', items: storageAll, color: 'text-[#6366f1]' },
            { key: 'analytics' as const, label: 'Analytics', items: analyticsAll, color: 'text-[#0ca678]' },
          ].map((menu) => (
            <div key={`${menu.key}-mobile`} className="border-b border-slate-50 last:border-0 pb-4">
              <button 
                type="button" 
                className={`w-full text-left font-black text-2xl py-4 flex justify-between items-center ${drawerExpanded === menu.key ? menu.color : 'text-slate-900'} transition-colors duration-300`} 
                onClick={() => setDrawerExpanded(drawerExpanded === menu.key ? null : menu.key)}
              >
                {menu.label} 
                <span className={`text-xl transition-transform duration-300 ${drawerExpanded === menu.key ? 'rotate-45' : ''}`}>＋</span>
              </button>
              <div 
                className={`overflow-hidden transition-all duration-500 ease-in-out ${drawerExpanded === menu.key ? 'opacity-100 mt-2' : 'opacity-0'}`}
                style={{ maxHeight: drawerExpanded === menu.key ? '1000px' : '0px' }}
              >
                <ul className="space-y-2">
                  {menu.items.map((item: MenuItem) => (
                    <li key={item.href}>
                      <Link href={item.href} className="block p-4 rounded-2xl hover:bg-slate-50 transition-all group" onClick={() => setDrawerOpen(false)}>
                        <div className="font-bold text-slate-800 group-hover:text-[#0ca678] transition-colors">{item.title}</div>
                        <div className="text-xs text-slate-400 mt-1">{item.subtitle}</div>
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
          
          <div className="pt-10 mt-6">
            {userEmail ? (
              <div className="bg-slate-50 rounded-3xl p-6 space-y-4">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center font-bold text-[#0ca678] shadow-sm">
                        {userInitial}
                    </div>
                    <div className="flex-1 min-w-0">
                        <div className="text-xs font-black text-slate-400 uppercase tracking-widest">Account</div>
                        <div className="font-bold text-slate-900 truncate">{userEmail}</div>
                    </div>
                </div>
                <Button variant="outline" className="w-full rounded-2xl font-bold py-6 border-slate-200 text-slate-600" onClick={handleLogout}>Log Out</Button>
              </div>
            ) : (
              <div className="flex flex-col gap-3">
                <Link href="/signup" className="flex items-center justify-center h-14 rounded-2xl bg-slate-900 font-bold text-white shadow-xl shadow-slate-200" onClick={() => setDrawerOpen(false)}>Get Started Free</Link>
                <Link href="/login" className="flex items-center justify-center h-14 rounded-2xl border border-slate-200 font-bold text-slate-600" onClick={() => setDrawerOpen(false)}>Log In</Link>
              </div>
            )}
          </div>
        </div>
      </Drawer>
    </nav>
  );
}
