import React from 'react';

export default function Footer() {
  return (
    <footer className="bg-[#0f172a] text-slate-400 py-24 px-6 md:px-12 border-t border-white/5 relative overflow-hidden">
      <div className="absolute top-0 right-0 w-96 h-96 bg-[#6366f1]/5 blur-[120px] rounded-full" />
      
      <div className="relative max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-16">
        <div className="col-span-1 md:col-span-2">
          <h2 className="text-3xl font-black mb-6 tracking-tighter text-white">
            NEX<span className="text-transparent bg-clip-text bg-gradient-to-r from-[#0ca678] to-[#6366f1]">LOOP</span>
          </h2>
          <p className="text-lg text-slate-400 max-w-sm mb-10 leading-relaxed font-medium">
            The next generation of automated video pipelines powered by Gemini machine intelligence.
          </p>
          <div className="flex gap-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="w-12 h-12 bg-white/5 border border-white/10 rounded-xl hover:bg-white/10 hover:border-[#0ca678]/50 transition-all cursor-pointer flex items-center justify-center group">
                <div className="w-2 h-2 bg-slate-600 rounded-full group-hover:scale-150 group-hover:bg-[#0ca678] transition-all" />
              </div>
            ))}
          </div>
        </div>
        
        <div>
          <h4 className="text-sm font-black mb-8 text-white uppercase tracking-[0.2em]">Service</h4>
          <ul className="space-y-4 font-bold">
            <li><a href="#pipeline" className="hover:text-[#0ca678] transition-colors">Pipeline</a></li>
            <li><a href="#" className="hover:text-[#0ca678] transition-colors">Archive</a></li>
            <li><a href="#" className="hover:text-[#0ca678] transition-colors">Analytics</a></li>
            <li><a href="#" className="hover:text-[#0ca678] transition-colors">Prompt Lab</a></li>
          </ul>
        </div>
        
        <div>
          <h4 className="text-sm font-black mb-8 text-white uppercase tracking-[0.2em]">Company</h4>
          <ul className="space-y-4 font-bold">
            <li className="text-slate-500">Email: help@nexloop.ai</li>
            <li className="text-slate-500">Address: Global AI Hub</li>
            <li><a href="#" className="hover:text-[#0ca678] transition-colors">Privacy Policy</a></li>
            <li><a href="#" className="hover:text-[#0ca678] transition-colors">Terms of Service</a></li>
          </ul>
        </div>
      </div>
      
      <div className="max-w-7xl mx-auto mt-24 pt-8 border-t border-white/5 flex flex-col md:flex-row justify-between items-center gap-6 text-sm font-bold text-slate-500">
        <p>© 2026 NEXLOOP AI. ALL RIGHTS RESERVED.</p>
        <div className="flex gap-8">
          <a href="#" className="hover:text-white transition-colors">Twitter</a>
          <a href="#" className="hover:text-white transition-colors">LinkedIn</a>
          <a href="#" className="hover:text-white transition-colors">GitHub</a>
        </div>
      </div>
    </footer>
  );
}
