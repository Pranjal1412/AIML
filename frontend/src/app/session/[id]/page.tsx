'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { FileText, ShieldCheck, ArrowLeft, Layers } from 'lucide-react';
import Link from 'next/link';
import StatusBadge from '@/components/StatusBadge';
import EntropyGauge from '@/components/EntropyGauge';
import DecisionTrace from '@/components/DecisionTrace';

export default function SessionDetailPage() {
  const params = useParams();
  const sessionId = params.id as string;

  const [sessionData, setSessionData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId) return;
    fetch(`/api/sessions/${sessionId}`)
      .then((res) => {
        if (!res.ok) throw new Error('Session not found.');
        return res.json();
      })
      .then((data) => setSessionData(data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [sessionId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[300px] text-xs font-mono text-gray-400">
        Loading session trace details...
      </div>
    );
  }

  if (error || !sessionData) {
    return (
      <div className="glass-panel p-6 text-center space-y-4">
        <div className="text-rose-400 font-mono text-sm">{error || 'Session not found'}</div>
        <Link href="/" className="inline-flex items-center gap-2 text-xs font-mono text-accentTeal hover:underline">
          <ArrowLeft className="w-3.5 h-3.5" /> Back to Console
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-12">
      <Link href="/" className="inline-flex items-center gap-2 text-xs font-mono text-gray-400 hover:text-accentTeal transition-all">
        <ArrowLeft className="w-3.5 h-3.5" /> Return to Observatory Console
      </Link>

      <div className="glass-panel p-6 space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-panelBorder pb-4">
          <div>
            <span className="text-[10px] font-mono text-gray-500 uppercase">Session Deep-Dive Trace</span>
            <h2 className="font-heading font-bold text-xl text-white mt-0.5">
              "{sessionData.query}"
            </h2>
          </div>
          <StatusBadge status={sessionData.status} />
        </div>

        <div className="text-xs font-mono text-gray-400 flex items-center gap-4">
          <span>Session ID: <strong className="text-gray-200">{sessionData.session_id}</strong></span>
          <span>•</span>
          <span>Action: <strong className="text-accentTeal">{sessionData.action_taken}</strong></span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="glass-panel p-6 space-y-3">
            <h3 className="font-heading font-semibold text-sm text-gray-200 border-b border-panelBorder pb-2">
              Final Answer Output
            </h3>
            <p className="text-sm text-gray-200 font-sans leading-relaxed bg-bgBase/40 p-4 rounded-xl border border-panelBorder">
              {sessionData.final_answer}
            </p>
          </div>

          <DecisionTrace
            factors={sessionData.decision_factors}
            roundsCount={sessionData.retrieval_rounds_count}
            entropy={sessionData.entropy}
            actionTaken={sessionData.action_taken}
          />
        </div>

        <div>
          <EntropyGauge
            entropy={sessionData.entropy}
            numClusters={sessionData.num_clusters}
            topClusterMass={sessionData.top_cluster_mass}
          />
        </div>
      </div>
    </div>
  );
}
