'use client';

import { motion } from 'framer-motion';

interface ClusterItem {
  cluster_id: number;
  candidate_ids: number[];
  probability_mass: number;
  representative_text: string;
}

interface ClusterMapProps {
  clusters?: ClusterItem[];
}

export default function ClusterMap({ clusters = [] }: ClusterMapProps) {
  if (!clusters || clusters.length === 0) {
    return (
      <div className="glass-panel p-5 flex flex-col items-center justify-center min-h-[220px]">
        <span className="text-xs font-mono text-gray-500">No candidate clusters generated yet</span>
      </div>
    );
  }

  const colors = ['#14B8A6', '#F59E0B', '#8B5CF6', '#EC4899', '#3B82F6'];

  return (
    <div className="glass-panel p-5 flex flex-col h-full relative">
      <div className="text-xs font-mono text-gray-400 uppercase tracking-wider mb-3 flex items-center justify-between">
        <span>Semantic Clusters & Entailment Graph</span>
        <span className="text-gray-500">{clusters.length} Cluster(s)</span>
      </div>

      <div className="flex-1 flex flex-col justify-center space-y-3">
        {clusters.map((cluster, idx) => {
          const color = colors[idx % colors.length];
          return (
            <motion.div
              key={cluster.cluster_id}
              initial={{ x: -10, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: idx * 0.1 }}
              className="p-3 rounded-lg bg-bgBase/60 border border-panelBorder flex flex-col gap-1.5 relative overflow-hidden"
            >
              <div
                className="absolute top-0 left-0 bottom-0 w-1"
                style={{ backgroundColor: color }}
              />
              <div className="flex items-center justify-between text-xs font-mono pl-2">
                <span className="font-semibold text-gray-200">
                  Cluster #{cluster.cluster_id + 1} ({cluster.candidate_ids.length} Candidate(s))
                </span>
                <span
                  className="px-2 py-0.5 rounded text-[10px] font-bold"
                  style={{ backgroundColor: `${color}20`, color: color }}
                >
                  {(cluster.probability_mass * 100).toFixed(0)}% Agreement Mass
                </span>
              </div>
              <p className="text-xs text-gray-300 pl-2 line-clamp-2 italic font-sans">
                "{cluster.representative_text}"
              </p>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
