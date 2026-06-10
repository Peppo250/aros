import React, { useEffect, useState, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../services/api';
import { 
  Play, 
  CheckCircle, 
  XCircle, 
  Hourglass,
  ArrowRight,
  Database,
  Terminal,
  Activity,
  FileText,
  GitMerge
} from 'lucide-react';

const STEPS_ORDER = [
  { key: "queued", label: "Queued in Orchestrator", progress: 0 },
  { key: "papers_completed", label: "Scraped Academic Literature", progress: 10 },
  { key: "github_completed", label: "Ingested GitHub Repository Metrics", progress: 20 },
  { key: "patents_completed", label: "Searched USPTO Patent Registers", progress: 30 },
  { key: "datasets_completed", label: "Checked Open Datasets Repository", progress: 40 },
  { key: "trends_completed", label: "Parsed Tech Search Trends", progress: 50 },
  { key: "citations_completed", label: "Aggregated Citation Indices", progress: 60 },
  { key: "graph_completed", label: "Constructed Knowledge Graph", progress: 70 },
  { key: "fusion_completed", label: "Executed Fusion Agent v2 Engine", progress: 80 },
  { key: "gap_completed", label: "Identified Research Gaps v2", progress: 85 },
  { key: "novelty_completed", label: "Evaluated Novelty & Market Fit", progress: 90 },
  { key: "patent_completed", label: "Compiled Patent Opportunity White Space", progress: 95 },
  { key: "report_completed", label: "Synthesizing Final Dossier", progress: 99 },
  { key: "completed", label: "Completed Final Dossier Report", progress: 100 }
];

export default function RunDetails() {
  const { runId } = useParams();
  const [run, setRun] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  const pollTimerRef = useRef(null);

  useEffect(() => {
    async function fetchStatus() {
      try {
        const data = await api.getRunStatus(runId);
        setRun(data);
        setError('');
        
        // Stop polling if completed or failed
        if (data.status === 'completed' || data.status === 'failed') {
          if (pollTimerRef.current) clearInterval(pollTimerRef.current);
        }
      } catch (err) {
        console.error('Polling error', err);
        setError('Connection interrupted. Retrying status sync...');
      } finally {
        setLoading(false);
      }
    }

    fetchStatus();
    // Poll every 3 seconds
    pollTimerRef.current = setInterval(fetchStatus, 3000);

    return () => {
      if (pollTimerRef.current) clearInterval(pollTimerRef.current);
    };
  }, [runId]);

  if (loading && !run) {
    return (
      <div className="flex flex-col items-center justify-center py-24 space-y-4">
        <div className="h-12 w-12 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
        <p className="text-slate-400 font-medium">Synchronizing pipeline status...</p>
      </div>
    );
  }

  const currentStatus = run?.status || 'queued';
  const currentProgress = run?.progress !== undefined ? run.progress : 0;
  
  // Find current active step index in STEPS_ORDER
  const activeStepIndex = STEPS_ORDER.findIndex(s => s.key === currentStatus);

  const getStepStatus = (index) => {
    if (currentStatus === 'failed') {
      if (index === activeStepIndex) return 'failed';
      return index < activeStepIndex ? 'completed' : 'pending';
    }
    if (currentStatus === 'completed') return 'completed';
    if (index === activeStepIndex) return 'active';
    return index < activeStepIndex ? 'completed' : 'pending';
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-fadeIn">
      {/* Title / Action Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-border pb-6">
        <div>
          <span className="text-xs font-semibold text-primary uppercase tracking-widest font-mono">
            Pipeline Tracker
          </span>
          <h2 className="text-2xl md:text-3xl font-bold text-white mt-1">
            Research Run ID: <span className="font-mono text-slate-300 text-xl md:text-2xl">{runId.slice(0, 18)}...</span>
          </h2>
        </div>
        
        {currentStatus === 'completed' && (
          <div className="flex items-center space-x-3">
            <Link
              to={`/graph/${run.project_id || runId}`}
              className="inline-flex items-center space-x-2 bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 px-4 py-2.5 rounded-lg font-semibold transition-all text-sm"
            >
              <GitMerge className="h-4 w-4" />
              <span>View Graph</span>
            </Link>
            <Link
              to={`/reports/${runId}`}
              className="inline-flex items-center space-x-2 bg-emerald-500 hover:bg-emerald-600 text-white px-5 py-2.5 rounded-lg font-bold transition-all glow-indigo text-sm"
            >
              <FileText className="h-4 w-4" />
              <span>Open Dossier Report</span>
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        )}
      </div>

      {/* Main Status Display */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Progress Card */}
        <div className="md:col-span-2 glass-panel p-6 rounded-xl space-y-6 flex flex-col justify-between">
          <div className="space-y-2">
            <div className="flex justify-between items-center text-sm font-semibold">
              <span className="text-slate-400">Pipeline Completion</span>
              <span className="text-primary font-mono text-base">{currentProgress}%</span>
            </div>
            {/* Custom styled progress bar */}
            <div className="w-full h-3 bg-slate-950 rounded-full overflow-hidden border border-border">
              <div 
                className="h-full bg-gradient-to-r from-primary to-accent rounded-full transition-all duration-700 ease-out"
                style={{ width: `${currentProgress}%` }}
              />
            </div>
          </div>

          <div className="flex items-center justify-between text-xs text-slate-500 font-mono">
            <div className="flex items-center space-x-1">
              <Activity className="h-4 w-4 text-secondary animate-pulse" />
              <span>Orchestrator: ACTIVE</span>
            </div>
            <span>Polling frequency: 3s</span>
          </div>
        </div>

        {/* Current State Indicator Card */}
        <div className="glass-panel p-6 rounded-xl flex flex-col justify-between items-center text-center space-y-4">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-widest font-mono">
            Current Status
          </span>
          <div className="flex flex-col items-center">
            {currentStatus === 'completed' ? (
              <CheckCircle className="h-12 w-12 text-emerald-400 animate-bounce" />
            ) : currentStatus === 'failed' ? (
              <XCircle className="h-12 w-12 text-rose-500" />
            ) : (
              <Hourglass className="h-12 w-12 text-amber-400 animate-spin" style={{ animationDuration: '4s' }} />
            )}
            <span className="text-lg font-bold text-white mt-3 uppercase tracking-wide">
              {currentStatus.replace('_', ' ')}
            </span>
          </div>
          <span className="text-[10px] text-slate-500 font-mono">
            {run.project_id ? `Project ID: ${run.project_id.slice(0, 8)}...` : ''}
          </span>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-400 text-sm">
          {error}
        </div>
      )}

      {/* Steps Visual List */}
      <div className="glass-panel p-8 rounded-xl space-y-6">
        <h3 className="text-lg font-bold text-white flex items-center space-x-2">
          <Terminal className="h-5 w-5 text-primary" />
          <span>Workflow Step-by-Step logs</span>
        </h3>
        
        <div className="relative border-l border-border ml-3 pl-6 space-y-8">
          {STEPS_ORDER.map((step, idx) => {
            const stepStatus = getStepStatus(idx);
            return (
              <div key={step.key} className="relative flex items-start group">
                {/* Node indicator */}
                <div className={`
                  absolute -left-[31px] h-4 w-4 rounded-full border-2 transition-all duration-300
                  ${stepStatus === 'completed' ? 'bg-emerald-400 border-emerald-400 glow-indigo scale-110' : ''}
                  ${stepStatus === 'active' ? 'bg-primary border-primary animate-ping' : ''}
                  ${stepStatus === 'failed' ? 'bg-rose-500 border-rose-500 scale-110' : ''}
                  ${stepStatus === 'pending' ? 'bg-slate-900 border-slate-700' : ''}
                `} />
                {/* Visual indicator for active step to make it stand out */}
                {stepStatus === 'active' && (
                  <div className="absolute -left-[31px] h-4 w-4 rounded-full border-2 bg-primary border-primary scale-110 shadow-lg shadow-primary/50" />
                )}

                <div className="space-y-1">
                  <h4 className={`
                    text-sm font-semibold transition-all duration-300
                    ${stepStatus === 'completed' ? 'text-slate-300' : ''}
                    ${stepStatus === 'active' ? 'text-primary font-bold text-base' : ''}
                    ${stepStatus === 'failed' ? 'text-rose-400 font-bold' : ''}
                    ${stepStatus === 'pending' ? 'text-slate-500' : ''}
                  `}>
                    {step.label}
                  </h4>
                  <span className="text-[10px] text-slate-500 font-mono">
                    Status stage: {step.key}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
