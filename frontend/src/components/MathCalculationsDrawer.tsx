'use client';

import { useState } from 'react';
import { Calculator, ChevronDown, ChevronUp, Cpu, Layers, Network } from 'lucide-react';

interface MathCalculationsProps {
  mathData?: any;
}

export default function MathCalculationsDrawer({ mathData }: MathCalculationsProps) {
  const [isOpen, setIsOpen] = useState(false);

  if (!mathData) return null;

  return (
    <div className="glass-panel overflow-hidden border border-panelBorder hover:border-teal-500/30 transition-all mt-3">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-white/5 transition-colors"
      >
        <div className="flex items-center gap-2">
          <Calculator className="w-4 h-4 text-accentTeal" />
          <span className="font-heading font-semibold text-xs text-gray-200">
            Inspect Mathematical Calculations & Matrix Trace
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-teal-500/10 text-accentTeal border border-teal-500/20">
            H = {mathData.normalized_entropy?.toFixed(4) || '0.0000'}
          </span>
          {isOpen ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
        </div>
      </button>

      {isOpen && (
        <div className="p-5 space-y-6 border-t border-panelBorder bg-bgBase/60 text-xs font-mono">
          {/* Formula 1: Shannon Entropy */}
          <div className="space-y-2 p-3.5 rounded-lg bg-panelBase/80 border border-panelBorder">
            <div className="flex items-center justify-between text-accentTeal font-bold">
              <span>1. Continuous Shannon Semantic Entropy Formula</span>
              <span>Normalized H ∈ [0.0, 1.0]</span>
            </div>
            <div className="text-gray-300 font-mono text-[11px] space-y-1 bg-bgBase/60 p-2.5 rounded border border-panelBorder/50">
              <div>Raw Entropy H(X) = - ∑ p(C_i) * ln(p(C_i)) = <strong className="text-accentTeal">{mathData.raw_entropy}</strong></div>
              <div>Max Possible Entropy ln(N=4) = <strong className="text-gray-200">{mathData.max_possible_entropy}</strong></div>
              <div>Normalized H = H(X) / ln(N) = <strong className="text-accentTeal">{mathData.normalized_entropy}</strong></div>
            </div>
          </div>

          {/* Formula 2: NLI Pairwise Entailment Matrix */}
          {mathData.nli_matrix && mathData.nli_matrix.length > 0 && (
            <div className="space-y-2 p-3.5 rounded-lg bg-panelBase/80 border border-panelBorder">
              <div className="text-accentTeal font-bold flex items-center justify-between">
                <span>2. DeBERTa Pairwise NLI Entailment Matrix (4x4)</span>
                <span>Threshold: &gt; 0.50</span>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-center border-collapse border border-panelBorder/60 text-[11px]">
                  <thead>
                    <tr className="bg-bgBase/80 text-gray-400">
                      <th className="p-2 border border-panelBorder/60 text-left">Candidate Pair</th>
                      {mathData.candidates.map((c: any) => (
                        <th key={c.id} className="p-2 border border-panelBorder/60">Candidate #{c.id + 1}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {mathData.nli_matrix.map((row: number[], i: number) => (
                      <tr key={i} className="hover:bg-white/5">
                        <td className="p-2 border border-panelBorder/60 font-semibold text-left text-gray-300">
                          Candidate #{i + 1}
                        </td>
                        {row.map((score: number, j: number) => (
                          <td
                            key={j}
                            className={`p-2 border border-panelBorder/60 font-mono ${
                              score >= 0.5
                                ? 'text-accentTeal font-bold bg-teal-500/10'
                                : 'text-gray-400'
                            }`}
                          >
                            {score.toFixed(3)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Formula 3: 9-Dimensional State Vector */}
          {mathData.state_vector && (
            <div className="space-y-2 p-3.5 rounded-lg bg-panelBase/80 border border-panelBorder">
              <div className="text-accentTeal font-bold flex items-center justify-between">
                <span>3. 9-Dimensional RL Feature State Vector (s)</span>
                <span>PyTorch MLP Input</span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-[11px]">
                {mathData.state_vector.map((val: number, idx: number) => (
                  <div key={idx} className="p-2 rounded bg-bgBase/60 border border-panelBorder/50 flex flex-col justify-between">
                    <span className="text-[10px] text-gray-400 truncate">{mathData.state_vector_names[idx]}</span>
                    <strong className="text-accentTeal text-xs mt-1">{val}</strong>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Formula 4: PPO Router Action Probabilities */}
          {mathData.action_probabilities && (
            <div className="space-y-2 p-3.5 rounded-lg bg-panelBase/80 border border-panelBorder">
              <div className="text-accentTeal font-bold flex items-center justify-between">
                <span>4. PPO Router Softmax Action Probabilities P(a|s)</span>
                <span>Action Space</span>
              </div>
              <div className="grid grid-cols-3 gap-3 text-center">
                <div className="p-2.5 rounded bg-bgBase/60 border border-teal-500/30">
                  <span className="text-[10px] text-gray-400 block">ANSWER (0)</span>
                  <strong className="text-accentTeal text-sm font-bold">
                    {(mathData.action_probabilities.ANSWER * 100).toFixed(1)}%
                  </strong>
                </div>
                <div className="p-2.5 rounded bg-bgBase/60 border border-amber-500/30">
                  <span className="text-[10px] text-gray-400 block">RETRIEVE_MORE (1)</span>
                  <strong className="text-accentAmber text-sm font-bold">
                    {(mathData.action_probabilities.RETRIEVE_MORE * 100).toFixed(1)}%
                  </strong>
                </div>
                <div className="p-2.5 rounded bg-bgBase/60 border border-rose-500/30">
                  <span className="text-[10px] text-gray-400 block">ABSTAIN (2)</span>
                  <strong className="text-accentRose text-sm font-bold">
                    {(mathData.action_probabilities.ABSTAIN * 100).toFixed(1)}%
                  </strong>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
