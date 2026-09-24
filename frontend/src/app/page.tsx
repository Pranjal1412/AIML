'use client';

import { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import { Send, Upload, Sparkles, RefreshCw, Cpu, BookOpen, Layers, Plus, Trash2, AlertTriangle, Bug, FileText } from 'lucide-react';

import LivePipelineProcessor from '@/components/LivePipelineProcessor';
import MathCalculationsDrawer from '@/components/MathCalculationsDrawer';
import DocumentUploadDrawer from '@/components/DocumentUploadDrawer';
import MinimalEntropyPill from '@/components/MinimalEntropyPill';
import EvidencePanel from '@/components/EvidencePanel';
import DecisionTrace from '@/components/DecisionTrace';
import EntropyGauge from '@/components/EntropyGauge';
import ClusterMap from '@/components/ClusterMap';

interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  isError?: boolean;
  traceData?: any;
  devErrorDetails?: string;
}

export default function ChatbotObservatory() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputQuery, setInputQuery] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [uploadDrawerOpen, setUploadDrawerOpen] = useState(false);
  const [docCount, setDocCount] = useState<number>(0);
  const [devMode, setDevMode] = useState<boolean>(true);
  const [activeInspectionTab, setActiveInspectionTab] = useState<Record<string, string>>({});

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const samplePrompts = [
    'What is the minimum attendance required to appear for final exams?',
    'What are the penalties for a first offense of plagiarism?',
    'How many office hours must full-time faculty members hold each week?',
    'What is the monthly stipend and maximum work hours for Graduate Assistants?',
  ];

  const fetchDocCount = async () => {
    try {
      const res = await fetch('/api/documents/count');
      if (res.ok) {
        const data = await res.json();
        setDocCount(data.count || 0);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchDocCount();
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isProcessing]);

  const handleSendMessage = async (queryToSubmit?: string) => {
    const q = queryToSubmit || inputQuery;
    if (!q.trim() || isProcessing) return;

    const userMsgId = `msg_user_${Date.now()}`;
    const userMsg: ChatMessage = { id: userMsgId, sender: 'user', text: q };

    setMessages((prev) => [...prev, userMsg]);
    setInputQuery('');
    setIsProcessing(true);

    try {
      const response = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: q }),
      });

      if (!response.ok) {
        let errDetail = response.statusText;
        try {
          const errJson = await response.json();
          errDetail = errJson.detail || errJson.message || JSON.stringify(errJson);
        } catch (_) {}

        throw new Error(`HTTP ${response.status} (${response.statusText}): ${errDetail}`);
      }

      const trace = await response.json();
      const assistantMsgId = `msg_ast_${Date.now()}`;
      const assistantMsg: ChatMessage = {
        id: assistantMsgId,
        sender: 'assistant',
        text: trace.final_answer,
        traceData: trace,
      };

      setMessages((prev) => [...prev, assistantMsg]);
      fetchDocCount();
    } catch (err: any) {
      console.error(err);
      const assistantMsgId = `msg_err_${Date.now()}`;
      const errorMsg: ChatMessage = {
        id: assistantMsgId,
        sender: 'assistant',
        text: 'An error occurred while connecting to the Semantic Entropy Engine backend.',
        isError: true,
        devErrorDetails: err.message || String(err),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsProcessing(false);
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  const toggleTab = (msgId: string, tab: string) => {
    setActiveInspectionTab((prev) => ({
      ...prev,
      [msgId]: prev[msgId] === tab ? '' : tab,
    }));
  };

  return (
    <div className="flex flex-col h-[calc(100vh-6rem)] max-w-5xl mx-auto relative font-sans">
      {/* Top Header Bar */}
      <div className="flex items-center justify-between py-3 px-4 glass-panel mb-4 border border-panelBorder shrink-0">
        <div className="flex items-center gap-2.5">
          <Cpu className="w-5 h-5 text-accentTeal" />
          <div>
            <h2 className="font-heading font-bold text-sm text-white leading-tight flex items-center gap-2">
              <span>Semantic Entropy Policy Assistant</span>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-teal-500/10 text-accentTeal border border-teal-500/30">
                DEV MODE
              </span>
            </h2>
            <div className="flex items-center gap-2 text-[10px] font-mono text-gray-400">
              <span>RL-Driven Context Optimization</span>
              <span>•</span>
              <span className={docCount > 0 ? 'text-accentTeal font-bold' : 'text-accentAmber font-bold'}>
                Indexed Chunks: {docCount}
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <Link
            href="/ingest"
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-accentTeal hover:bg-teal-600 text-black text-xs font-heading font-bold transition-all shadow-[0_0_12px_rgba(20,184,166,0.3)]"
          >
            <Plus className="w-4 h-4" />
            <span>+ Ingest Document</span>
          </Link>
          {messages.length > 0 && (
            <button
              onClick={clearChat}
              className="p-1.5 rounded-lg text-gray-400 hover:text-rose-400 hover:bg-white/5 transition-colors"
              title="Clear Conversation"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Main Conversational Feed */}
      <div className="flex-1 overflow-y-auto px-2 space-y-6 pb-24">
        {docCount === 0 && (
          <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs flex items-center justify-between gap-3 font-mono shadow-lg">
            <div className="flex items-center gap-2.5">
              <AlertTriangle className="w-5 h-5 text-accentAmber shrink-0" />
              <span>
                <strong>Document Required:</strong> Please submit or upload an academic policy PDF/TXT document first before asking questions.
              </span>
            </div>
            <Link
              href="/ingest"
              className="px-3.5 py-1.5 rounded-lg bg-accentAmber text-black font-heading font-bold text-xs shrink-0 hover:bg-amber-400 transition-all flex items-center gap-1.5 shadow-[0_0_10px_rgba(245,158,11,0.3)]"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Go to Policy Ingestion</span>
            </Link>
          </div>
        )}

        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center py-12 px-4 space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-teal-500/10 border border-teal-500/30 flex items-center justify-center text-accentTeal">
              <Sparkles className="w-6 h-6" />
            </div>
            <div className="max-w-md space-y-1.5">
              <h3 className="font-heading font-bold text-lg text-white">
                Institutional Policy Intelligence
              </h3>
              <p className="text-xs text-gray-400 leading-relaxed">
                Upload your institutional policy PDF first, then ask questions about regulations, attendance, grading, or faculty conduct.
              </p>
            </div>

            {/* Quick Prompts */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 max-w-2xl w-full pt-4">
              {samplePrompts.map((sq, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSendMessage(sq)}
                  className="p-3 rounded-xl bg-bgBase/60 hover:bg-white/5 border border-panelBorder text-xs text-gray-300 hover:text-accentTeal transition-all text-left font-sans line-clamp-2"
                >
                  "{sq}"
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Message Stream */}
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex flex-col ${
              msg.sender === 'user' ? 'items-end' : 'items-start'
            }`}
          >
            {/* User Message Bubble */}
            {msg.sender === 'user' ? (
              <div className="max-w-2xl bg-teal-500/15 border border-teal-500/30 text-gray-100 text-sm py-3 px-4.5 rounded-2xl rounded-tr-sm font-sans shadow-sm">
                {msg.text}
              </div>
            ) : (
              /* Assistant Response Block */
              <div className="w-full space-y-3">
                <div className={`max-w-3xl glass-panel p-5 space-y-3 border ${
                  msg.isError ? 'border-rose-500/40 bg-rose-500/5' : 'border-panelBorder'
                }`}>
                  <div className="flex items-center justify-between border-b border-panelBorder pb-2.5">
                    <MinimalEntropyPill
                      status={msg.isError ? 'ABSTAINED' : (msg.traceData?.status || 'ANSWERED')}
                      entropy={msg.traceData?.entropy || 0.0}
                    />
                    <span className="font-mono text-[10px] text-gray-500">
                      ID: {msg.traceData?.session_id || 'ERR'}
                    </span>
                  </div>

                  <div className={`text-sm leading-relaxed font-sans whitespace-pre-line ${
                    msg.isError ? 'text-rose-300 font-semibold' : 'text-gray-100'
                  }`}>
                    {msg.text}
                  </div>

                  {/* Dev Mode Error Inspector Box */}
                  {msg.isError && msg.devErrorDetails && (
                    <div className="mt-3 p-3.5 rounded-lg bg-bgBase/90 border border-rose-500/40 space-y-2 font-mono text-xs">
                      <div className="flex items-center gap-2 text-rose-400 font-bold">
                        <Bug className="w-4 h-4" />
                        <span>DEV MODE DIAGNOSTIC ERROR TRACE</span>
                      </div>
                      <div className="p-2.5 rounded bg-black/60 text-rose-300 text-[11px] overflow-x-auto whitespace-pre-wrap">
                        {msg.devErrorDetails}
                      </div>
                      <div className="text-[10px] text-gray-400">
                        Troubleshooting: Verify that the FastAPI backend server is running on <code className="text-accentTeal">http://localhost:8000</code> by executing <code className="text-white">.\venv\Scripts\python -m backend.main</code> in your terminal.
                      </div>
                    </div>
                  )}

                  {/* Inline Source Chips */}
                  {(msg.traceData?.routing_mode === 'grounded' || msg.traceData?.status?.includes('Grounded')) && msg.traceData?.sources && msg.traceData.sources.length > 0 && (
                    <div className="pt-2 flex items-center gap-2 flex-wrap">
                      <span className="text-[11px] font-mono text-gray-400">Cited:</span>
                      {msg.traceData.sources.map((src: any, sIdx: number) => (
                        <span
                          key={sIdx}
                          className="px-2.5 py-0.5 rounded bg-teal-500/10 border border-teal-500/30 text-accentTeal font-mono text-[11px]"
                        >
                          [{sIdx + 1}] {src.doc_title} §{src.section || 'General'}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {/* Metric Inspection Drawer Tabs */}
                {msg.traceData && (
                  <div className="max-w-3xl space-y-2">
                    <div className="flex items-center gap-2 text-xs font-mono">
                      <button
                        onClick={() => toggleTab(msg.id, 'sources')}
                        className={`px-3 py-1.5 rounded-lg border transition-all ${
                          activeInspectionTab[msg.id] === 'sources'
                            ? 'bg-teal-500/10 border-teal-500/40 text-accentTeal'
                            : 'bg-bgBase/60 border-panelBorder text-gray-400 hover:text-gray-200'
                        }`}
                      >
                        Cited Evidence ({msg.traceData.sources?.length || 0})
                      </button>

                      <button
                        onClick={() => toggleTab(msg.id, 'factors')}
                        className={`px-3 py-1.5 rounded-lg border transition-all ${
                          activeInspectionTab[msg.id] === 'factors'
                            ? 'bg-teal-500/10 border-teal-500/40 text-accentTeal'
                            : 'bg-bgBase/60 border-panelBorder text-gray-400 hover:text-gray-200'
                        }`}
                      >
                        Decision Factors
                      </button>

                      <button
                        onClick={() => toggleTab(msg.id, 'math')}
                        className={`px-3 py-1.5 rounded-lg border transition-all ${
                          activeInspectionTab[msg.id] === 'math'
                            ? 'bg-teal-500/10 border-teal-500/40 text-accentTeal'
                            : 'bg-bgBase/60 border-panelBorder text-gray-400 hover:text-gray-200'
                        }`}
                      >
                        Math & Calculations
                      </button>

                      <button
                        onClick={() => toggleTab(msg.id, 'clusters')}
                        className={`px-3 py-1.5 rounded-lg border transition-all ${
                          activeInspectionTab[msg.id] === 'clusters'
                            ? 'bg-teal-500/10 border-teal-500/40 text-accentTeal'
                            : 'bg-bgBase/60 border-panelBorder text-gray-400 hover:text-gray-200'
                        }`}
                      >
                        Entropy Gauge & Clusters
                      </button>
                    </div>

                    {/* Expandable Content Panes */}
                    {activeInspectionTab[msg.id] === 'sources' && (
                      <EvidencePanel sources={msg.traceData.sources} />
                    )}

                    {activeInspectionTab[msg.id] === 'factors' && (
                      <DecisionTrace
                        factors={msg.traceData.decision_factors}
                        roundsCount={msg.traceData.retrieval_rounds_count}
                        entropy={msg.traceData.entropy}
                        actionTaken={msg.traceData.action_taken}
                      />
                    )}

                    {activeInspectionTab[msg.id] === 'math' && (
                      <MathCalculationsDrawer mathData={msg.traceData.math_calculations} />
                    )}

                    {activeInspectionTab[msg.id] === 'clusters' && (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                        <EntropyGauge
                          entropy={msg.traceData.entropy}
                          numClusters={msg.traceData.num_clusters}
                          topClusterMass={msg.traceData.top_cluster_mass}
                        />
                        <ClusterMap clusters={msg.traceData.clusters} />
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}

        {/* Live Processing Animation */}
        {isProcessing && (
          <div className="w-full max-w-3xl">
            <LivePipelineProcessor />
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Fixed Bottom Input Bar */}
      <div className="absolute bottom-0 left-0 right-0 p-4 bg-bgBase/90 backdrop-blur-xl border-t border-panelBorder">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSendMessage();
          }}
          className="flex gap-2.5 max-w-5xl mx-auto"
        >
          <input
            type="text"
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            placeholder="Ask a policy question..."
            disabled={isProcessing}
            className="flex-1 bg-bgBase/80 border border-panelBorder rounded-xl px-4 py-3 text-sm text-gray-100 placeholder-gray-500 focus:outline-none focus:border-accentTeal font-sans transition-all disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={isProcessing || !inputQuery.trim()}
            className="px-5 py-3 bg-accentTeal hover:bg-teal-600 disabled:opacity-50 text-black font-heading font-bold text-xs rounded-xl flex items-center gap-2 transition-all shadow-[0_0_15px_rgba(20,184,166,0.3)] shrink-0"
          >
            {isProcessing ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <>
                <Send className="w-4 h-4" />
                <span>Ask</span>
              </>
            )}
          </button>
        </form>
      </div>

      {/* Document Upload Slide-Over Drawer */}
      <DocumentUploadDrawer
        isOpen={uploadDrawerOpen}
        onClose={() => setUploadDrawerOpen(false)}
        onSuccess={fetchDocCount}
      />
    </div>
  );
}
