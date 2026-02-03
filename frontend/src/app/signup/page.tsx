'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { signup } from '@/lib/api';
import { Button } from '@/components/ui/Button';

export default function SignUpPage() {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        password: '',
        team_name: '',
        job_title: '',
        phone_number: '',
    });
    const [message, setMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const router = useRouter();

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSignUp = async () => {
        if (!formData.email || !formData.password || !formData.name) {
            setMessage('Name, Email and Password are required.');
            return;
        }
        
        setIsLoading(true);
        setMessage('');
        try {
            const response = await signup(formData);
            sessionStorage.setItem('auth_token', response.token);
            router.push('/login');
        } catch (error: any) {
            setMessage(error.message || '가입 실패');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <main className="min-h-screen bg-[#f8fafc] flex flex-col items-center justify-center p-6 relative overflow-hidden">
            {/* Animated Background Elements */}
            <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-[#0ca678]/5 blur-[120px] rounded-full animate-pulse" />
            <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-[#6366f1]/5 blur-[120px] rounded-full animate-pulse" />
            
            {/* Header Area */}
            <div className="absolute top-0 left-0 right-0 px-4 py-3 sm:px-6 sm:py-4 md:px-10 md:py-6 flex justify-between items-center z-50">
                <Link href="/" className="text-lg sm:text-xl md:text-2xl font-black tracking-tighter flex items-center gap-1.5 sm:gap-2 group">
                    <div className="w-7 h-7 sm:w-8 sm:h-8 bg-gradient-to-br from-[#0ca678] to-[#6366f1] rounded-lg flex items-center justify-center text-white text-xs transform group-hover:rotate-12 transition-transform">N</div>
                    <span className="text-slate-900 group-hover:text-[#0ca678] transition-colors">NEXLOOP</span>
                </Link>
                <Button asChild variant="ghost" className="text-slate-500 hover:text-slate-900 font-bold text-xs sm:text-sm md:text-base px-2 sm:px-3">
                    <Link href="/login"><span className="hidden sm:inline">Already have an account?</span> Log In</Link>
                </Button>
            </div>

            {/* Sign Up Card */}
            <div className="w-full max-w-2xl relative z-10">
                <div className="bg-white/80 backdrop-blur-2xl border border-white shadow-[0_32px_64px_-16px_rgba(0,0,0,0.1)] rounded-[40px] overflow-hidden">
                    <div className="p-8 md:p-12">
                        <div className="text-center mb-10">
                            <h1 className="text-4xl font-black text-slate-900 mb-3 tracking-tight">Create your account</h1>
                            <p className="text-slate-500 font-medium">Start your journey with Nexloop automation.</p>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="space-y-2">
                                <label className="text-xs font-black text-slate-400 uppercase tracking-widest px-1">Full Name</label>
                                <input
                                    name="name"
                                    type="text"
                                    placeholder="Your Name"
                                    className="w-full h-14 px-5 rounded-2xl bg-white border border-slate-100 focus:border-[#0ca678] focus:ring-4 focus:ring-[#0ca678]/5 outline-none transition-all font-bold text-slate-900 placeholder:text-slate-300 shadow-sm"
                                    value={formData.name}
                                    onChange={handleChange}
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-xs font-black text-slate-400 uppercase tracking-widest px-1">Email Address</label>
                                <input
                                    name="email"
                                    type="email"
                                    placeholder="name@company.com"
                                    className="w-full h-14 px-5 rounded-2xl bg-white border border-slate-100 focus:border-[#0ca678] focus:ring-4 focus:ring-[#0ca678]/5 outline-none transition-all font-bold text-slate-900 placeholder:text-slate-300 shadow-sm"
                                    value={formData.email}
                                    onChange={handleChange}
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-xs font-black text-slate-400 uppercase tracking-widest px-1">Company Name</label>
                                <input
                                    name="team_name"
                                    type="text"
                                    placeholder="Your Organization"
                                    className="w-full h-14 px-5 rounded-2xl bg-white border border-slate-100 focus:border-[#0ca678] focus:ring-4 focus:ring-[#0ca678]/5 outline-none transition-all font-bold text-slate-900 placeholder:text-slate-300 shadow-sm"
                                    value={formData.team_name}
                                    onChange={handleChange}
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-xs font-black text-slate-400 uppercase tracking-widest px-1">Job Title</label>
                                <input
                                    name="job_title"
                                    type="text"
                                    placeholder="e.g. Marketing Lead"
                                    className="w-full h-14 px-5 rounded-2xl bg-white border border-slate-100 focus:border-[#0ca678] focus:ring-4 focus:ring-[#0ca678]/5 outline-none transition-all font-bold text-slate-900 placeholder:text-slate-300 shadow-sm"
                                    value={formData.job_title}
                                    onChange={handleChange}
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-xs font-black text-slate-400 uppercase tracking-widest px-1">Phone Number</label>
                                <input
                                    name="phone_number"
                                    type="tel"
                                    placeholder="+82 00 0000 0000"
                                    className="w-full h-14 px-5 rounded-2xl bg-white border border-slate-100 focus:border-[#0ca678] focus:ring-4 focus:ring-[#0ca678]/5 outline-none transition-all font-bold text-slate-900 placeholder:text-slate-300 shadow-sm"
                                    value={formData.phone_number}
                                    onChange={handleChange}
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-xs font-black text-slate-400 uppercase tracking-widest px-1">Password</label>
                                <input
                                    name="password"
                                    type="password"
                                    placeholder="Min 8 characters"
                                    className="w-full h-14 px-5 rounded-2xl bg-white border border-slate-100 focus:border-[#0ca678] focus:ring-4 focus:ring-[#0ca678]/5 outline-none transition-all font-bold text-slate-900 placeholder:text-slate-300 shadow-sm"
                                    value={formData.password}
                                    onChange={handleChange}
                                />
                            </div>
                        </div>

                        <Button
                            disabled={isLoading}
                            className="w-full h-16 rounded-[20px] bg-[#0ca678] hover:bg-[#099268] text-white text-xl font-black shadow-lg shadow-[#0ca678]/20 transition-all active:scale-[0.98] mt-10 mb-6"
                            onClick={handleSignUp}
                        >
                            {isLoading ? 'Creating Account...' : 'Get Started Now'}
                        </Button>

                        {message && (
                            <div className="p-4 rounded-xl bg-red-50 text-red-600 text-sm font-bold text-center mb-6 animate-shake">
                                {message}
                            </div>
                        )}

                        <div className="text-center">
                            <p className="text-xs font-medium text-slate-400 max-w-sm mx-auto leading-relaxed">
                                By signing up, you agree to our <a href="#" className="text-slate-900 underline underline-offset-4 decoration-slate-200 hover:decoration-slate-900 transition-colors">Terms of Service</a> and <a href="#" className="text-slate-900 underline underline-offset-4 decoration-slate-200 hover:decoration-slate-900 transition-colors">Privacy Policy</a>
                            </p>
                        </div>
                    </div>
                    
                    {/* Social Auth Footer */}
                    <div className="bg-slate-50/50 p-8 border-t border-slate-100 flex flex-col md:flex-row items-center justify-center gap-4">
                        <button className="flex items-center justify-center gap-3 px-6 h-12 bg-white border border-slate-100 rounded-xl text-sm font-bold text-slate-700 hover:bg-slate-50 transition-colors shadow-sm w-full md:w-auto">
                            <span className="text-[#4285F4] text-lg">G</span> Continue with Google
                        </button>
                        <button className="flex items-center justify-center gap-3 px-6 h-12 bg-white border border-slate-100 rounded-xl text-sm font-bold text-slate-700 hover:bg-slate-50 transition-colors shadow-sm w-full md:w-auto">
                            <span className="text-[#03C75A] text-lg">N</span> Continue with Naver
                        </button>
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
