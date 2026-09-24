'use client';

interface RoundItem {
  round: number;
  k: number;
  entropy: number;
  chunks_kept: number;
  action_taken: string;
}

interface RetrievalRoundStepperProps {
  rounds?: RoundItem[];
}

export default function RetrievalRoundStepper({ rounds = [] }: RetrievalRoundStepperProps) {
  if (!rounds || rounds.length <= 1) return null;

  return (
    <div className="glass-panel p-4 overflow-x-auto">
      <div className="text-xs font-mono text-gray-400 uppercase tracking-wider mb-3">
        Multi-Round Context Expansion Stepper
      </div>
      <div className="flex items-center space-x-4 min-w-max">
        {rounds.map((r, idx) => (
          <div key={idx} className="flex items-center gap-3">
            <div className="flex flex-col p-3 rounded-lg bg-bgBase/80 border border-teal-500/30 min-w-[140px]">
              <span className="text-[10px] font-mono text-accentTeal font-bold">ROUND #{r.round}</span>
              <span className="text-xs font-mono text-gray-200 mt-1">k = {r.k} Chunks</span>
              <div className="flex items-center justify-between text-[11px] font-mono text-gray-400 mt-2 border-t border-panelBorder pt-1">
                <span>H: <strong className="text-white">{r.entropy.toFixed(2)}</strong></span>
                <span className="text-accentAmber font-semibold">{r.action_taken}</span>
              </div>
            </div>
            {idx < rounds.length - 1 && (
              <div className="w-6 h-0.5 bg-teal-500/40" />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
