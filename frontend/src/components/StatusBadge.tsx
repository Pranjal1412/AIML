'use client';

import { CheckCircle2, RefreshCw, AlertTriangle, Sparkles } from 'lucide-react';

interface StatusBadgeProps {
  status: string;
}

export default function StatusBadge({ status }: StatusBadgeProps) {
  if (status.includes('GENERAL KNOWLEDGE') || status.includes('General Knowledge')) {
    return (
      <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono font-semibold bg-purple-500/10 border border-purple-500/40 text-purple-300 shadow-[0_0_12px_rgba(168,85,247,0.25)]">
        <Sparkles className="w-3.5 h-3.5 text-purple-400" />
        <span>GENERAL KNOWLEDGE (Uncited)</span>
      </div>
    );
  } else if (status.includes('ANSWERED') || status === 'grounded') {
    return (
      <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono font-semibold bg-teal-500/10 border border-teal-500/40 text-accentTeal shadow-[0_0_12px_rgba(20,184,166,0.25)]">
        <CheckCircle2 className="w-3.5 h-3.5" />
        <span>ANSWERED (Grounded)</span>
      </div>
    );
  } else if (status.includes('RETRIEV')) {
    return (
      <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono font-semibold bg-amber-500/10 border border-amber-500/40 text-accentAmber animate-pulse-slow shadow-[0_0_12px_rgba(245,158,11,0.25)]">
        <RefreshCw className="w-3.5 h-3.5 animate-spin" />
        <span>RETRIEVING MORE CONTEXT</span>
      </div>
    );
  } else {
    return (
      <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono font-semibold bg-rose-500/10 border border-rose-500/40 text-accentRose shadow-[0_0_12px_rgba(244,63,94,0.25)]">
        <AlertTriangle className="w-3.5 h-3.5" />
        <span>ABSTAINED (Insufficient Evidence)</span>
      </div>
    );
  }
}

