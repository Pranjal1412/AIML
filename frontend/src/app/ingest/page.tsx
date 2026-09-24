'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Upload, FileText, CheckCircle2, AlertCircle, Database, Layers, ArrowRight, Loader2, Sparkles } from 'lucide-react';

export default function IngestPage() {
  const [file, setFile] = useState<File | null>(null);
  const [institution, setInstitution] = useState('Apex Academic University');
  const [docType, setDocType] = useState('general_handbook');
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [progressStage, setProgressStage] = useState('');
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setUploading(true);
    setProgress(5);
    setProgressStage('Initializing file upload...');
    setError(null);
    setResult(null);

    // Progress animation interval
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
      setProgressStage('Ingestion & indexing complete!');
      setResult(data);
      setFile(null);
    } catch (err: any) {
      clearInterval(progressTimer);
      setProgress(0);
      setError(err.message || 'Document ingestion failed.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6 pb-12">
      <div className="glass-panel p-6 space-y-2">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-mono bg-teal-500/10 text-accentTeal border border-teal-500/30">
          <Database className="w-3.5 h-3.5" />
          <span>Knowledge Base Ingestion Admin</span>
        </div>
        <h2 className="font-heading font-bold text-2xl text-white tracking-tight">
          Institutional Document Ingestion & Chunking
        </h2>
        <p className="text-sm text-gray-400">
          Upload PDF or TXT policy documents (attendance, faculty policy, exam regulations, code of conduct). Documents are extracted, cleaned, chunked into ~500 tokens with 15% overlap, enriched with metadata, and upserted into persistent ChromaDB vector storage.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Upload Form */}
        <div className="lg:col-span-2 glass-panel p-6 space-y-5">
          <h3 className="font-heading font-semibold text-base text-gray-200 border-b border-panelBorder pb-3">
            Upload & Ingest Policy Document
          </h3>

          <form onSubmit={handleUpload} className="space-y-4">
            <div>
              <label className="block text-xs font-mono text-gray-400 mb-1">
                Select Policy PDF or TXT File:
              </label>
              <input
                type="file"
                accept=".pdf,.txt"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="w-full bg-bgBase/80 border border-panelBorder rounded-xl p-3 text-sm text-gray-200 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-mono file:bg-teal-500/10 file:text-accentTeal hover:file:bg-teal-500/20 font-mono cursor-pointer"
              />
              {file && (
                <span className="text-xs font-mono text-teal-400 block mt-1.5 pl-1">
                  Selected file: <strong>{file.name}</strong> ({(file.size / 1024).toFixed(1)} KB)
                </span>
              )}
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
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
                  Document Classification:
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
            </div>

            <button
              type="submit"
              disabled={uploading || !file}
              className="w-full py-3.5 bg-accentTeal hover:bg-teal-600 disabled:opacity-50 text-black font-heading font-bold text-sm rounded-xl flex items-center justify-center gap-2 transition-all shadow-[0_0_15px_rgba(20,184,166,0.3)]"
            >
              {uploading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Processing & Indexing Document ({progress}%)...</span>
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4" />
                  <span>Process & Ingest Document</span>
                </>
              )}
            </button>
          </form>

          {/* Progress Bar Display */}
          {uploading && (
            <div className="p-4 rounded-xl bg-panelBase/80 border border-teal-500/30 space-y-2 font-mono">
              <div className="flex items-center justify-between text-xs text-gray-300">
                <span className="flex items-center gap-2 text-teal-400 font-semibold">
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  {progressStage}
                </span>
                <span className="font-bold text-teal-400">{progress}%</span>
              </div>
              <div className="w-full h-2.5 bg-bgBase rounded-full overflow-hidden border border-panelBorder">
                <div
                  className="h-full bg-gradient-to-r from-teal-500 to-emerald-400 transition-all duration-300 rounded-full shadow-[0_0_12px_rgba(20,184,166,0.5)]"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          )}

          {/* Success Notification Card */}
          {result && (
            <div className="p-5 rounded-xl bg-teal-500/10 border border-teal-500/30 text-accentTeal space-y-4 font-mono shadow-[0_0_20px_rgba(20,184,166,0.15)]">
              <div className="flex items-center gap-3 font-semibold text-sm text-teal-300">
                <CheckCircle2 className="w-6 h-6 text-accentTeal shrink-0" />
                <div>
                  <div className="font-bold">{result.message}</div>
                  <div className="text-xs text-gray-300 font-normal mt-0.5">
                    Document successfully chunked, embedded, and saved to ChromaDB.
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5 text-xs text-gray-300 bg-bgBase/60 p-3 rounded-lg border border-panelBorder">
                <div>
                  <span className="text-[10px] text-gray-400 block uppercase">Vector Chunks</span>
                  <strong className="text-accentTeal text-sm font-bold">{result.chunks_count}</strong>
                </div>
                <div>
                  <span className="text-[10px] text-gray-400 block uppercase">Document Type</span>
                  <strong className="text-gray-200">{result.doc_metadata?.doc_type || 'Policy'}</strong>
                </div>
                <div>
                  <span className="text-[10px] text-gray-400 block uppercase">Institution</span>
                  <strong className="text-gray-200">{result.doc_metadata?.institution || 'Academic'}</strong>
                </div>
              </div>

              <div className="pt-1 flex justify-end">
                <Link
                  href="/"
                  className="px-4 py-2.5 rounded-xl bg-accentTeal hover:bg-teal-600 text-black font-heading font-bold text-xs flex items-center gap-2 transition-all shadow-[0_0_12px_rgba(20,184,166,0.3)]"
                >
                  <Sparkles className="w-4 h-4" />
                  <span>Start Asking Questions on Chatbot Console</span>
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </div>
            </div>
          )}

          {/* Failure Information Card */}
          {error && (
            <div className="p-5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 space-y-3 font-mono">
              <div className="flex items-center gap-3 font-semibold text-sm text-rose-300">
                <AlertCircle className="w-6 h-6 text-rose-400 shrink-0" />
                <div>
                  <div className="font-bold">Document Not Added: Ingestion Failed</div>
                  <div className="text-xs text-rose-300/80 font-normal mt-0.5">
                    The policy document could not be indexed into ChromaDB.
                  </div>
                </div>
              </div>

              <div className="text-xs text-rose-300 bg-rose-950/50 p-3 rounded-lg border border-rose-500/20 font-mono break-all">
                <strong>Error Details:</strong> {error}
              </div>

              <div className="text-[11px] text-gray-300 space-y-1.5 pt-1 bg-bgBase/40 p-3 rounded-lg border border-panelBorder">
                <div className="font-bold text-gray-200">Why did this happen & how to resolve:</div>
                <div>1. <strong>Unreadable or Scanned PDF:</strong> PDF must contain selectable text. Image-only scanned PDFs require OCR.</div>
                <div>2. <strong>Backend Disconnected:</strong> Ensure backend is running via <code className="text-teal-400 bg-black/40 px-1 py-0.5 rounded">python -m backend.main</code>.</div>
                <div>3. <strong>Supported File Formats:</strong> Upload standard <strong>.pdf</strong> or <strong>.txt</strong> text policy files.</div>
              </div>
            </div>
          )}
        </div>

        {/* Pre-loaded Demo Corpus Sidebar */}
        <div className="glass-panel p-6 space-y-4">
          <h3 className="font-heading font-semibold text-base text-gray-200 border-b border-panelBorder pb-3 flex items-center gap-2">
            <Layers className="w-4 h-4 text-accentTeal" />
            <span>Pre-loaded Policy Corpus</span>
          </h3>

          <div className="space-y-3 text-xs font-mono">
            <div className="p-3 rounded-lg bg-bgBase/60 border border-panelBorder">
              <div className="text-gray-200 font-semibold">attendance_policy.pdf</div>
              <div className="text-gray-400 mt-1">75% mandatory attendance, 65% condonation threshold.</div>
            </div>
            <div className="p-3 rounded-lg bg-bgBase/60 border border-panelBorder">
              <div className="text-gray-200 font-semibold">faculty_conduct_policy.pdf</div>
              <div className="text-gray-400 mt-1">48h email SLA, 4 office hours/week requirements.</div>
            </div>
            <div className="p-3 rounded-lg bg-bgBase/60 border border-panelBorder">
              <div className="text-gray-200 font-semibold">examination_grading_policy.pdf</div>
              <div className="text-gray-400 mt-1">4.0 CGPA scale, 14-day grade re-evaluation window.</div>
            </div>
            <div className="p-3 rounded-lg bg-bgBase/60 border border-panelBorder">
              <div className="text-gray-200 font-semibold">student_code_of_conduct.pdf</div>
              <div className="text-gray-400 mt-1">Plagiarism policy (15%), disciplinary suspension rules.</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

