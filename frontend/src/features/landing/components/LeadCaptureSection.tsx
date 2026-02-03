'use client';

import React, { useState, useEffect } from 'react';
import { Modal, useToast, Input } from '@/components/ui';
import { Button as UIButton } from '@/components/ui/Button';
import { createLead } from '@/lib/api';

type LeadCaptureSectionProps = {
  externalTrigger?: boolean;
  onExternalClose?: () => void;
  triggerReason?: 'chatbot_limit' | 'cta';
};

export default function LeadCaptureSection({
  externalTrigger = false,
  onExternalClose,
  triggerReason = 'cta'
}: LeadCaptureSectionProps) {
  const [modalOpen, setModalOpen] = useState(false);
  const [leadEmail, setLeadEmail] = useState('');
  const toast = useToast();

  useEffect(() => {
    if (externalTrigger) {
      setModalOpen(true);
    }
  }, [externalTrigger]);

  const handleClose = () => {
    setModalOpen(false);
    if (onExternalClose) {
      onExternalClose();
    }
  };

  return (
    <section className="py-40 px-6 bg-slate-50 relative overflow-hidden">
      {/* Decorative Background Glows */}
      <div className="absolute top-1/2 left-1/4 -translate-y-1/2 w-[600px] h-[600px] bg-[#0ca678]/5 blur-[140px] rounded-full pointer-events-none" />
      <div className="absolute top-1/2 right-1/4 -translate-y-1/2 w-[600px] h-[600px] bg-[#6366f1]/5 blur-[140px] rounded-full pointer-events-none" />
      
      <div className="max-w-5xl mx-auto relative z-10">
        <div className="relative p-16 md:p-24 rounded-[48px] bg-white border border-slate-100 shadow-[0_40px_80px_-24px_rgba(0,0,0,0.12)] text-center group transition-all duration-700 hover:shadow-[0_60px_100px_-30px_rgba(0,0,0,0.15)]">
          <div className="relative z-10">
            <h2 className="text-4xl sm:text-5xl md:text-8xl font-black mb-12 tracking-tight leading-tight italic text-slate-900 px-4">
              Ready to go <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#0ca678] via-[#4facfe] to-[#6366f1] not-italic inline-block">with us?</span>
            </h2>
            <div className="space-y-4 mb-16">
              <p className="text-xl md:text-3xl font-medium text-slate-400 tracking-tight">
                I&apos;m ready to analyze your next project.
              </p>
              <p className="text-2xl md:text-4xl font-black text-slate-900 tracking-tighter">
                The future of automation starts here.
              </p>
            </div>
            
            <UIButton
              onClick={() => setModalOpen(true)}
              className="text-xl md:text-2xl px-16 py-8 h-auto font-black shadow-xl transition-all group rounded-2xl bg-[#0ca678] hover:bg-[#099268] text-white hover:scale-105 active:scale-95 shadow-[#0ca678]/30 hover:shadow-[#0ca678]/50"
            >
              Yes, SURE! 
            </UIButton>
          </div>
          
          {/* Subtle card decoration */}
          <div className="absolute top-0 right-0 w-48 h-48 bg-gradient-to-br from-[#0ca678]/5 to-transparent rounded-full blur-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-1000" />
          <div className="absolute bottom-0 left-0 w-48 h-48 bg-gradient-to-tr from-[#6366f1]/5 to-transparent rounded-full blur-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-1000" />
        </div>
      </div>

      {/* Modal */}
      <Modal open={modalOpen} onClose={handleClose} title={triggerReason === 'chatbot_limit' ? '더 많은 질문이 필요하신가요?' : 'Get started'}>
        <div className="p-2">
          {triggerReason === 'chatbot_limit' ? (
            <p className="text-lg text-slate-600 mb-8 leading-relaxed">
              무료 체험이 종료되었습니다. 계속해서 AI 챗봇을 이용하시려면 이메일을 남겨주세요. 저희 팀이 24시간 내에 연락드리겠습니다.
            </p>
          ) : (
            <p className="text-lg text-slate-600 mb-8 leading-relaxed">
              We&apos;ll help you set up your first pipeline. Leave your email and our team will reach out within 24 hours.
            </p>
          )}
          <Input
            type="email"
            placeholder="your@email.com"
            className="mb-6 h-14 text-lg px-6 rounded-xl border-slate-200 focus:border-[#0ca678] focus:ring-[#0ca678]"
            value={leadEmail}
            onChange={(e) => setLeadEmail(e.target.value)}
          />
          <UIButton
            className="w-full h-14 text-xl font-bold rounded-xl bg-[#0f172a]"
            onClick={async () => {
              try {
                await createLead({ email: leadEmail });
                handleClose();
                toast.addToast("Thanks! We'll be in touch soon.");
                setLeadEmail('');
              } catch {
                toast.addToast("Failed to submit. Please try again.");
              }
            }}
          >
            Send Request
          </UIButton>
        </div>
      </Modal>
    </section>
  );
}
