'use client';

import { useState } from 'react';
import { ShieldCheck, ChevronDown, ChevronUp, Layers, Activity } from 'lucide-react';

interface DecisionTraceProps {
  factors?: string[];
  roundsCount?: number;
  entropy?: number;
  actionTaken?: string;
}

export default function DecisionTrace({
  factors = [],
  roundsCount = 1,
  entropy = 0.0,
  actionTaken = 'ANSWER',
}: DecisionTraceProps) {
  const [isOpen, setIsOpen] = useState(true);

  if (!factors || factors.length === 0) return null;

  return (
    <div className="glass-panel overflow-hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-5 py-3 flex items-center justify-between text-left hover:bg-white/5 transition-colors border-b border-panelBorder"
      >
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-accentTeal" />
          <span className="font-heading font-semibold text-sm text-gray-200">
            Transparency & Decision Factors (No Raw Chain-of-Thought)
          </span>
        </div>
        {isOpen ? (
          <ChevronUp className="w-4 h-4 text-gray-400" />
        ) : (
          <ChevronDown className="w-4 h-4 text-gray-400" />
        )}
      </button>

      {isOpen && (
        <div className="p-5 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div className="p-3 rounded-lg bg-bgBase/60 border border-panelBorder">
              <span className="text-[10px] font-mono uppercase text-gray-500 block">Retrieval Rounds</span>
              <span className="text-sm font-mono font-semibold text-gray-200">{roundsCount} Round(s)</span>
            </div>
            <div className="p-3 rounded-lg bg-bgBase/60 border border-panelBorder">
              <span className="text-[10px] font-mono uppercase text-gray-500 block">Uncertainty Signal</span>
              <span className="text-sm font-mono font-semibold text-gray-200">H = {entropy.toFixed(2)}</span>
            </div>
            <div className="p-3 rounded-lg bg-bgBase/60 border border-panelBorder">
              <span className="text-[10px] font-mono uppercase text-gray-500 block">Policy Decision</span>
              <span className="text-sm font-mono font-semibold text-accentTeal">{actionTaken}</span>
            </div>
          </div>

          <div className="space-y-2 pt-2">
            <span className="text-xs font-mono text-gray-400 uppercase tracking-wider block">
              Structured Decision Criteria:
            </span>
            <ul className="space-y-2">
              {factors.map((factor, idx) => (
                <li key={idx} className="flex items-start gap-2.5 text-xs text-gray-300 font-mono bg-bgBase/40 p-2.5 rounded border border-panelBorder/50">
                  <span className="w-1.5 h-1.5 rounded-full bg-accentTeal mt-1.5 shrink-0" />
                  <span>{factor}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
