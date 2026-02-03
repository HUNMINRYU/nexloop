'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { login } from '@/lib/api';
import { Button, buttonVariants } from '@/components/ui/Button';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const handleLogin = async () => {
    if (!email || !password) {
      setMessage('Please enter both email and password.');
      return;
    }
    
    setIsLoading(true);
    setMessage('');
    try {
      const response = await login({ email: email as any, password });
      sessionStorage.setItem('auth_token', response.token);
      router.push('/');
    } catch (error) {
      console.error(error);
      alert(`Login failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
      setMessage('Login failed. Please check your credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-[#f8fafc] flex flex-col items-center justify-center p-6 relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute top-[-10%] right-[-10%] w-[40%] h-[40%] bg-[#0ca678]/5 blur-[120px] rounded-full animate-pulse" />
      <div className="absolute bottom-[-10%] left-[-10%] w-[40%] h-[40%] bg-[#6366f1]/5 blur-[120px] rounded-full animate-pulse" />
      
      {/* Header Area */}
      <div className="absolute top-0 left-0 right-0 px-4 py-3 sm:px-6 sm:py-4 md:px-10 md:py-6 flex justify-between items-center z-50">
        <Link href="/" className="text-lg sm:text-xl md:text-2xl font-black tracking-tighter flex items-center gap-1.5 sm:gap-2 group">
          <div className="w-7 h-7 sm:w-8 sm:h-8 bg-gradient-to-br from-[#0ca678] to-[#6366f1] rounded-lg flex items-center justify-center text-white text-xs transform group-hover:rotate-12 transition-transform">N</div>
          <span className="text-slate-900 group-hover:text-[#0ca678] transition-colors">NEXLOOP</span>
        </Link>
        <Link href="/signup" className={buttonVariants({ variant: 'ghost', className: "text-slate-500 hover:text-slate-900 font-bold text-xs sm:text-sm md:text-base px-2 sm:px-3" })}>
          <span className="hidden sm:inline">Need an account?</span> Sign Up
        </Link>
      </div>

      {/* Log In Card */}
      <div className="w-full max-w-md relative z-10">
        <div className="bg-white/80 backdrop-blur-2xl border border-white shadow-[0_32px_64px_-16px_rgba(0,0,0,0.1)] rounded-[40px] overflow-hidden">
          <div className="p-8 md:p-12">
            <div className="text-center mb-10">
              <h1 className="text-4xl font-black text-slate-900 mb-3 tracking-tight">Welcome back</h1>
              <p className="text-slate-500 font-medium">Log in to your workspace.</p>
            </div>

            <div className="space-y-6">
              <form onSubmit={(e) => { e.preventDefault(); handleLogin(); }} className="space-y-6">
              <div className="space-y-2">
                <label className="text-xs font-black text-slate-400 uppercase tracking-widest px-1">Email Address</label>
                <input
                  type="email"
                  placeholder="name@company.com"
                  className="w-full h-14 px-5 rounded-2xl bg-white border border-slate-100 focus:border-[#0ca678] focus:ring-4 focus:ring-[#0ca678]/5 outline-none transition-all font-bold text-slate-900 placeholder:text-slate-300 shadow-sm"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <div className="flex justify-between items-center px-1">
                  <label className="text-xs font-black text-slate-400 uppercase tracking-widest">Password</label>
                  <a href="#" className="text-xs font-bold text-[#0ca678] hover:underline">Forgot?</a>
                </div>
                <input
                  type="password"
                  placeholder="••••••••"
                  className="w-full h-14 px-5 rounded-2xl bg-white border border-slate-100 focus:border-[#0ca678] focus:ring-4 focus:ring-[#0ca678]/5 outline-none transition-all font-bold text-slate-900 placeholder:text-slate-300 shadow-sm"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>

              <Button
                disabled={isLoading}
                className="w-full h-16 rounded-[20px] bg-[#0ca678] hover:bg-[#099268] text-white text-xl font-black shadow-lg shadow-[#0ca678]/20 transition-all active:scale-[0.98] mt-4"
                onClick={handleLogin}
              >
                {isLoading ? 'Signing In...' : 'Log In'}
              </Button>

                {message && (
                  <div className="p-4 rounded-xl bg-red-50 text-red-600 text-sm font-bold text-center animate-shake">
                    {message}
                  </div>
                )}
              </form>
            </div>

            <div className="relative flex items-center py-10">
              <div className="flex-grow border-t border-slate-100"></div>
              <span className="flex-shrink mx-4 font-black text-slate-300 text-xs uppercase tracking-widest">OR</span>
              <div className="flex-grow border-t border-slate-100"></div>
            </div>

            <div className="space-y-3">
              <button className="flex items-center justify-center gap-3 w-full h-14 bg-white border border-slate-100 rounded-2xl text-sm font-bold text-slate-700 hover:bg-slate-50 transition-colors shadow-sm">
                <span className="text-[#4285F4] text-lg">G</span> Continue with Google
              </button>
              <button className="flex items-center justify-center gap-3 w-full h-14 bg-white border border-slate-100 rounded-2xl text-sm font-bold text-slate-700 hover:bg-slate-50 transition-colors shadow-sm">
                <span className="text-[#03C75A] text-lg">N</span> Continue with Naver
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Subtle Footer */}
      <div className="mt-12 relative z-10">
        <p className="text-xs font-bold text-slate-400">© 2026 NEXLOOP Inc. All rights reserved.</p>
      </div>
    </main>
  );
}
