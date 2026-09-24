'use client';

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle2, Loader2, Sparkles, Cpu, Layers, Network, ShieldCheck, Database } from 'lucide-react';

interface Step {
  id: number;
  label: string;
  description: string;
  icon: any;
}

const PIPELINE_STEPS: Step[] = [
  { id: 1, label: 'Domain Validation', description: 'Checking query similarity against institutional corpus floor (0.35)', icon: Database },
  { id: 2, label: 'Vector Retrieval', description: 'ChromaDB dense similarity search (MPNet 768-dim embeddings)', icon: Layers },
  { id: 3, label: 'Context Engineering', description: 'Filtering, dedup, reranking & wrapping chunk source boundaries', icon: Cpu },
  { id: 4, label: 'Candidate Generation', description: 'Stochastic sampling N=4 candidates (temp=0.8, top_p=0.95)', icon: Sparkles },
  { id: 5, label: 'DeBERTa Pairwise NLI', description: 'Cross-encoder scoring & Union-Find bidirectional clustering', icon: Network },
  { id: 6, label: 'Continuous Semantic Entropy', description: 'Computing normalized Shannon entropy H over cluster probability mass', icon: Cpu },
  { id: 7, label: 'PPO Policy Routing', description: 'Evaluating 9-dim state vector -> Action: ANSWER / RETRIEVE_MORE / ABSTAIN', icon: ShieldCheck },
];

export default function LivePipelineProcessor() {
  const [currentStep, setCurrentStep] = useState(1);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStep((prev) => (prev < 7 ? prev + 1 : prev));
    }, 450);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="glass-panel p-5 my-4 border border-teal-500/20 bg-panelBase/90 backdrop-blur-xl relative overflow-hidden">
      <div className="flex items-center justify-between border-b border-panelBorder pb-3 mb-4">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-accentTeal animate-ping" />
          <span className="font-mono text-xs text-accentTeal font-semibold uppercase tracking-wider">
            Live Pipeline Execution Engine
          </span>
        </div>
        <span className="font-mono text-xs text-gray-400">
          Step {currentStep} of 7
        </span>
      </div>

      <div className="space-y-2.5">
        {PIPELINE_STEPS.map((step) => {
          const Icon = step.icon;
          const isDone = currentStep > step.id;
          const isActive = currentStep === step.id;

          return (
            <div
              key={step.id}
              className={`flex items-start gap-3 p-2.5 rounded-lg transition-all ${
                isActive
                  ? 'bg-teal-500/10 border border-teal-500/30 text-white'
                  : isDone
                  ? 'bg-bgBase/40 text-gray-300 opacity-80'
                  : 'text-gray-600 opacity-40'
              }`}
            >
              <div className="mt-0.5 shrink-0">
                {isDone ? (
                  <CheckCircle2 className="w-4 h-4 text-accentTeal" />
                ) : isActive ? (
                  <Loader2 className="w-4 h-4 text-accentTeal animate-spin" />
                ) : (
                  <Icon className="w-4 h-4 text-gray-500" />
                )}
              </div>
              <div className="flex-1 text-xs font-mono">
                <div className="flex items-center justify-between">
                  <span className={`font-semibold ${isActive ? 'text-accentTeal' : ''}`}>
                    [{step.id}] {step.label}
                  </span>
                  {isActive && (
                    <span className="text-[10px] text-accentTeal font-bold animate-pulse">PROCESSING</span>
                  )}
                </div>
                <p className="text-[11px] text-gray-400 font-sans mt-0.5">{step.description}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
