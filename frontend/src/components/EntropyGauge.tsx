'use client';

import { motion } from 'framer-motion';

interface EntropyGaugeProps {
  entropy: number; // 0.0 to 1.0
  numClusters?: number;
  topClusterMass?: number;
}

export default function EntropyGauge({
  entropy = 0.0,
  numClusters = 1,
  topClusterMass = 1.0,
}: EntropyGaugeProps) {
  // SVG gauge constants
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference * (1 - entropy * 0.75); // 270 deg arc

  // Color interpolation
  let strokeColor = '#14B8A6'; // Teal
  let label = 'Low Uncertainty';
  if (entropy > 0.25 && entropy <= 0.5) {
    strokeColor = '#F59E0B'; // Amber
    label = 'Moderate Uncertainty';
  } else if (entropy > 0.5) {
    strokeColor = '#F43F5E'; // Rose
    label = 'High Uncertainty';
  }

  return (
    <div className="glass-panel p-5 flex flex-col items-center justify-center relative overflow-hidden">
      <div className="absolute top-3 left-4 text-xs font-mono text-gray-400 uppercase tracking-wider flex items-center gap-1.5">
        <span className="w-2 h-2 rounded-full bg-accentTeal animate-ping" />
        Semantic Entropy Gauge
      </div>

      <div className="relative w-44 h-44 flex items-center justify-center mt-4">
        <svg className="w-full h-full transform -rotate-135" viewBox="0 0 140 140">
          {/* Background Arc */}
          <circle
            cx="70"
            cy="70"
            r={radius}
            fill="none"
            stroke="rgba(255, 255, 255, 0.08)"
            strokeWidth="10"
            strokeDasharray={circumference}
            strokeDashoffset={circumference * 0.25}
            strokeLinecap="round"
          />
          {/* Foreground Animated Gauge Arc */}
          <motion.circle
            cx="70"
            cy="70"
            r={radius}
            fill="none"
            stroke={strokeColor}
            strokeWidth="10"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{ type: 'spring', stiffness: 60, damping: 15 }}
            strokeLinecap="round"
            className="filter drop-shadow-[0_0_8px_rgba(20,184,166,0.5)]"
          />
        </svg>

        {/* Center Text */}
        <div className="absolute flex flex-col items-center justify-center text-center">
          <motion.span
            key={entropy}
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="text-3xl font-mono font-bold text-white tracking-tight"
          >
            {entropy.toFixed(2)}
          </motion.span>
          <span className="text-[10px] font-mono text-gray-400 uppercase tracking-widest mt-0.5">
            Normalized H
          </span>
        </div>
      </div>

      <div className="mt-2 text-center">
        <div
          className="text-xs font-semibold px-2.5 py-0.5 rounded-full inline-block font-mono"
          style={{ backgroundColor: `${strokeColor}15`, color: strokeColor }}
        >
          {label}
        </div>
        <div className="flex items-center gap-4 mt-3 text-[11px] font-mono text-gray-400 border-t border-panelBorder pt-2.5 w-full justify-center">
          <span>Clusters: <strong className="text-gray-200">{numClusters}</strong></span>
          <span>Agreement: <strong className="text-gray-200">{(topClusterMass * 100).toFixed(0)}%</strong></span>
        </div>
      </div>
    </div>
  );
}
