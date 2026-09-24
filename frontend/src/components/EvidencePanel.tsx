'use client';

import { useState } from 'react';
import { ChevronDown, ChevronUp, FileText, ExternalLink } from 'lucide-react';

interface SourceItem {
  chunk_id?: string;
  doc_title: string;
  doc_type: string;
  section: string;
  page: number;
  similarity: number;
}

interface EvidencePanelProps {
  sources?: SourceItem[];
}

export default function EvidencePanel({ sources = [] }: EvidencePanelProps) {
  const [isOpen, setIsOpen] = useState(true);

  if (!sources || sources.length === 0) {
    return null;
  }

  return (
    <div className="glass-panel overflow-hidden transition-all">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-5 py-3.5 flex items-center justify-between text-left hover:bg-white/5 transition-colors border-b border-panelBorder"
      >
        <div className="flex items-center gap-2.5">
          <FileText className="w-4 h-4 text-accentTeal" />
          <span className="font-heading font-semibold text-sm text-gray-200">
            Retrieved Institutional Evidence ({sources.length} Sources Cited)
          </span>
        </div>
        {isOpen ? (
          <ChevronUp className="w-4 h-4 text-gray-400" />
        ) : (
          <ChevronDown className="w-4 h-4 text-gray-400" />
        )}
      </button>

      {isOpen && (
        <div className="p-4 space-y-3 max-h-96 overflow-y-auto">
          {sources.map((src, idx) => (
            <div
              key={idx}
              className="p-3.5 rounded-lg bg-bgBase/80 border border-panelBorder flex flex-col gap-2 hover:border-teal-500/30 transition-all"
            >
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-[10px] px-2 py-0.5 rounded bg-teal-500/10 text-accentTeal font-semibold border border-teal-500/20">
                    [{idx + 1}]
                  </span>
                  <span className="font-semibold text-gray-200 font-heading">
                    {src.doc_title}
                  </span>
                </div>
                <div className="flex items-center gap-2 font-mono text-[11px] text-gray-400">
                  <span>Sim: <strong className="text-accentTeal">{(src.similarity * 100).toFixed(1)}%</strong></span>
                </div>
              </div>

              <div className="flex items-center gap-3 text-[11px] font-mono text-gray-400 pl-6">
                <span>Section: <strong className="text-gray-300">{src.section}</strong></span>
                <span>•</span>
                <span>Page <strong className="text-gray-300">{src.page}</strong></span>
                <span>•</span>
                <span className="capitalize text-gray-400">{src.doc_type.replace('_', ' ')}</span>
              </div>

              {/* Similarity Bar */}
              <div className="w-full bg-gray-800 h-1.5 rounded-full overflow-hidden ml-6 max-w-[95%]">
                <div
                  className="bg-accentTeal h-full rounded-full transition-all duration-500"
                  style={{ width: `${Math.min(100, src.similarity * 100)}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
