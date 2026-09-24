'use client';

import { useState, useRef } from 'react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, X, CheckCircle2, AlertCircle, Database, ExternalLink, Loader2, ArrowRight } from 'lucide-react';

interface DocumentUploadDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export default function DocumentUploadDrawer({
  isOpen,
  onClose,
  onSuccess,
}: DocumentUploadDrawerProps) {
  const [file, setFile] = useState<File | null>(null);
  const [institution, setInstitution] = useState('Apex Academic University');
  const [docType, setDocType] = useState('attendance_policy');
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [progressStage, setProgressStage] = useState('');
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setUploading(true);
    setProgress(5);
    setProgressStage('Initializing file upload...');
    setError(null);
    setResult(null);

    const progressTimer = setInterval(() => {
      setProgress((prev) => {
        if (prev < 30) {
          setProgressStage('Extracting text & cleaning formatting...');
          return prev + 5;
        } else if (prev < 65) {
          setProgressStage('Splitting into ~500 token policy chunks...');
          return prev + 5;
        } else if (prev < 90) {
          setProgressStage('Generating 768-dim embeddings (all-mpnet-base-v2)...');
          return prev + 3;
        } else if (prev < 98) {
          setProgressStage('Upserting chunks into ChromaDB vector storage...');
          return prev + 1;
        }
        return prev;
      });
    }, 250);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('institution', institution);
    formData.append('doc_type', docType);

    try {
      const response = await fetch('/api/ingest', {
        method: 'POST',
        body: formData,
      });

      clearInterval(progressTimer);

      if (!response.ok) {
        let errDetail = response.statusText;
        try {
          const errJson = await response.json();
          errDetail = errJson.detail || errJson.message || JSON.stringify(errJson);
        } catch (_) {}
        throw new Error(`HTTP ${response.status} (${response.statusText}): ${errDetail}`);
      }

      const data = await response.json();
      setProgress(100);
      setProgressStage('Ingestion complete!');
      setResult(data);
      setFile(null);
      if (onSuccess) onSuccess();
    } catch (err: any) {
      clearInterval(progressTimer);
      setProgress(0);
      setError(err.message || 'Failed to ingest document.');
    } finally {
      setUploading(false);
    }
  };

  const triggerFileSelect = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-sm">
          {/* Backdrop Click */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="absolute inset-0"
          />

          {/* Drawer Panel */}
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="relative w-full max-w-md bg-panelBase border-l border-panelBorder h-full flex flex-col z-10 shadow-2xl p-6 overflow-y-auto"
          >
            <div className="flex items-center justify-between border-b border-panelBorder pb-4 mb-5">
              <div className="flex items-center gap-2">
                <Database className="w-5 h-5 text-accentTeal" />
                <h3 className="font-heading font-bold text-base text-white">
                  Ingest Policy Document
                </h3>
              </div>
              <button
                onClick={onClose}
                className="p-1 rounded-lg text-gray-400 hover:text-white hover:bg-white/10 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Direct Link to Policy Ingestion Page */}
            <div className="mb-4 p-3 rounded-xl bg-teal-500/10 border border-teal-500/20 text-xs font-mono text-gray-300 flex items-center justify-between">
              <span>Looking for full ingestion admin & bulk corpus?</span>
              <Link
                href="/ingest"
                onClick={onClose}
                className="text-accentTeal hover:underline font-bold flex items-center gap-1 shrink-0 ml-2"
              >
                <span>Policy Ingestion Page</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </Link>
            </div>

            <form onSubmit={handleUpload} className="space-y-4 flex-1">
              <div>
                <label className="block text-xs font-mono text-gray-400 mb-1.5">
                  Select Document (PDF or TXT):
                </label>

                {/* Hidden File Input */}
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,.txt"
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                  className="hidden"
                />

                {/* Clickable Dropzone */}
                <div
                  onClick={triggerFileSelect}
                  className="border-2 border-dashed border-panelBorder hover:border-teal-500/50 cursor-pointer rounded-xl p-5 text-center transition-all bg-bgBase/40 hover:bg-white/5 group"
                >
                  <Upload className="w-7 h-7 text-accentTeal mx-auto mb-2 group-hover:scale-110 transition-transform" />
                  <span className="text-xs font-mono text-gray-200 group-hover:text-accentTeal font-semibold block">
                    {file ? file.name : 'Click anywhere here to select PDF/TXT file'}
                  </span>
                  <span className="text-[10px] text-gray-500 font-mono block mt-1">
                    {file ? `${(file.size / 1024).toFixed(1)} KB selected` : 'Supports academic PDFs & policy TXT files'}
                  </span>
                </div>
              </div>

              <div>
                <label className="block text-xs font-mono text-gray-400 mb-1">
                  Institution Name:
                </label>
                <input
                  type="text"
                  value={institution}
                  onChange={(e) => setInstitution(e.target.value)}
                  className="w-full bg-bgBase/80 border border-panelBorder rounded-xl p-3 text-sm text-gray-200 font-sans focus:border-accentTeal focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-mono text-gray-400 mb-1">
                  Policy Document Classification:
                </label>
                <select
                  value={docType}
                  onChange={(e) => setDocType(e.target.value)}
                  className="w-full bg-bgBase/80 border border-panelBorder rounded-xl p-3 text-sm text-gray-200 font-sans focus:border-accentTeal focus:outline-none"
                >
                  <option value="attendance_policy">Attendance Policy</option>
                  <option value="faculty_policy">Faculty / Teacher Conduct</option>
                  <option value="exam_regulation">Exam & Grading Regulations</option>
                  <option value="code_of_conduct">Student Code of Conduct</option>
                  <option value="general_handbook">General Handbook</option>
                </select>
              </div>

              <button
                type="submit"
                disabled={uploading || !file}
                className="w-full py-3.5 bg-accentTeal hover:bg-teal-600 disabled:opacity-50 text-black font-heading font-bold text-xs rounded-xl flex items-center justify-center gap-2 transition-all shadow-[0_0_15px_rgba(20,184,166,0.3)] mt-3"
              >
                {uploading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Processing ({progress}%)...</span>
                  </>
                ) : (
                  <>
                    <Upload className="w-4 h-4" />
                    <span>Upload & Index Document</span>
                  </>
                )}
              </button>
            </form>

            {/* Progress Bar Display */}
            {uploading && (
              <div className="p-3.5 rounded-xl bg-panelBase/80 border border-teal-500/30 space-y-1.5 font-mono mt-4">
                <div className="flex items-center justify-between text-[11px] text-gray-300">
                  <span className="text-teal-400 font-semibold truncate">{progressStage}</span>
                  <span className="font-bold text-teal-400">{progress}%</span>
                </div>
                <div className="w-full h-2 bg-bgBase rounded-full overflow-hidden border border-panelBorder">
                  <div
                    className="h-full bg-teal-400 transition-all duration-300 rounded-full"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              </div>
            )}

            {/* Failure Feedback */}
            {error && (
              <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs space-y-2 font-mono mt-4">
                <div className="flex items-center gap-2 font-semibold text-rose-300">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>Document Not Added: Ingestion Error</span>
                </div>
                <div className="text-[11px] text-rose-300/90 bg-rose-950/40 p-2 rounded border border-rose-500/20 font-mono break-all">
                  {error}
                </div>
                <div className="text-[10px] text-gray-400 space-y-0.5 pt-1">
                  <div>• Ensure PDF contains selectable text (not scanned image).</div>
                  <div>• Ensure backend is running at <code className="text-teal-400">http://localhost:8000</code>.</div>
                </div>
              </div>
            )}

            {/* Success Feedback */}
            {result && (
              <div className="p-3.5 rounded-xl bg-teal-500/10 border border-teal-500/30 text-accentTeal text-xs space-y-2 font-mono mt-4">
                <div className="flex items-center gap-2 font-semibold">
                  <CheckCircle2 className="w-4 h-4 text-accentTeal" />
                  <span>{result.message}</span>
                </div>
                <div className="text-[11px] text-gray-300 pl-6 space-y-0.5">
                  <div>Chunks Indexed: <strong>{result.chunks_count}</strong></div>
                  <div>Classification: <strong>{result.doc_metadata?.doc_type || 'Policy'}</strong></div>
                </div>
                <div className="pt-2">
                  <button
                    onClick={onClose}
                    className="w-full py-2 bg-accentTeal hover:bg-teal-600 text-black font-heading font-bold text-xs rounded-lg flex items-center justify-center gap-1.5 transition-all"
                  >
                    <span>Start Asking Questions</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            )}
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}

