'use client';

import { Sparkles, RefreshCw, AlertTriangle, CheckCircle2 } from 'lucide-react';

interface MinimalEntropyPillProps {
  status: string;
  entropy: number;
}

export default function MinimalEntropyPill({ status, entropy }: MinimalEntropyPillProps) {
  let colorClass = 'bg-teal-500/10 border-teal-500/30 text-accentTeal';
  let label = status || 'ANSWERED (Grounded)';
  let icon = <CheckCircle2 className="w-3.5 h-3.5" />;

  if (status.includes('GENERAL KNOWLEDGE') || status.includes('General Knowledge')) {
    colorClass = 'bg-purple-500/10 border-purple-500/40 text-purple-300 shadow-[0_0_12px_rgba(168,85,247,0.25)]';
    label = 'GENERAL KNOWLEDGE (Uncited)';
    icon = <Sparkles className="w-3.5 h-3.5 text-purple-400" />;
  } else if (status.includes('RETRIEV')) {
    colorClass = 'bg-amber-500/10 border-amber-500/30 text-accentAmber';
    label = 'RETRIEVING MORE CONTEXT';
    icon = <RefreshCw className="w-3.5 h-3.5 animate-spin" />;
  } else if (status.includes('ABSTAIN') || status.includes('Abstain')) {
    colorClass = 'bg-rose-500/10 border-rose-500/30 text-accentRose';
    label = 'ABSTAINED (Insufficient Evidence)';
    icon = <AlertTriangle className="w-3.5 h-3.5" />;
  }

  return (
    <div className="inline-flex items-center gap-3 font-mono text-xs">
      <div className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full border ${colorClass}`}>
        {icon}
        <span className="font-semibold">{label}</span>
      </div>
      <div className="text-gray-400 text-[11px]">
        Semantic Uncertainty H: <strong className="text-white font-bold">{entropy.toFixed(2)}</strong>
      </div>
    </div>
  );
}

