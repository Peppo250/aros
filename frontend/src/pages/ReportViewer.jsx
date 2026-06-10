import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../services/api';
import { 
  FileText, 
  Award, 
  Printer, 
  Clock, 
  Database,
  ArrowLeft,
  ChevronRight,
  GitMerge,
  BookOpen,
  Compass,
  AlertTriangle,
  Lightbulb,
  Briefcase,
  Layers,
  Map,
  Compass as ActionIcon
} from 'lucide-react';

const SECTION_METADATA = {
  executive_summary: { label: "Executive Summary", icon: FileText, color: "text-indigo-400" },
  research_landscape: { label: "Research Landscape", icon: BookOpen, color: "text-blue-400" },
  research_gaps: { label: "Research Gaps", icon: AlertTriangle, color: "text-amber-400" },
  novelty_assessment: { label: "Novelty Assessment", icon: Lightbulb, color: "text-purple-400" },
  patent_opportunities: { label: "Patent Opportunities", icon: Award, color: "text-emerald-400" },
  ieee_publication_plan: { label: "IEEE Publication Plan", icon: Layers, color: "text-cyan-400" },
  patent_filing_plan: { label: "Patent Filing Plan", icon: Award, color: "text-teal-400" },
  commercialization_strategy: { label: "Commercialization Strategy", icon: Briefcase, color: "text-rose-400" },
  research_roadmap: { label: "Research Roadmap", icon: Map, color: "text-orange-400" },
  next_actions: { label: "Recommended Next Actions", icon: ActionIcon, color: "text-pink-400" },
};

export default function ReportViewer() {
  const { runId } = useParams();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('executive_summary');

  useEffect(() => {
    async function loadReport() {
      try {
        const data = await api.getRunResult(runId);
        setReport(data);
      } catch (err) {
        console.error(err);
        setError('The report dossier is not ready yet, or there was a server connection issue.');
      } finally {
        setLoading(false);
      }
    }
    loadReport();
  }, [runId]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-24 space-y-4">
        <div className="h-12 w-12 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
        <p className="text-slate-400 font-medium">Assembling research dossier...</p>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="max-w-xl mx-auto text-center py-16 space-y-6">
        <AlertTriangle className="h-16 w-16 text-rose-500 mx-auto" />
        <h3 className="text-2xl font-bold text-white">Report Dossier Unavailable</h3>
        <p className="text-slate-400">
          We couldn't retrieve the final dossier for this run. Make sure the orchestrator completed successfully.
        </p>
        <div className="flex justify-center space-x-4">
          <Link to="/" className="bg-slate-800 hover:bg-slate-700 text-white px-4 py-2 rounded-lg font-semibold text-sm transition-all">
            Back to Dashboard
          </Link>
          <Link to={`/runs/${runId}`} className="bg-primary hover:bg-primary-hover text-white px-4 py-2 rounded-lg font-semibold text-sm transition-all">
            Track Pipeline Progress
          </Link>
        </div>
      </div>
    );
  }

  const handlePrint = () => {
    window.print();
  };

  const confidencePct = report.confidence_score ? (report.confidence_score * 100).toFixed(0) : 'N/A';

  return (
    <div className="space-y-8 animate-fadeIn max-w-7xl mx-auto print:bg-white print:text-black">
      {/* Top action header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-border pb-6 print:hidden">
        <div className="space-y-1">
          <Link to="/" className="inline-flex items-center text-slate-400 hover:text-white text-xs font-semibold uppercase tracking-wider space-x-1.5 transition-colors mb-2">
            <ArrowLeft className="h-3.5 w-3.5" />
            <span>Dashboard</span>
          </Link>
          <h2 className="text-3xl font-bold text-white tracking-tight">
            Research Intelligence Dossier
          </h2>
          <p className="text-slate-400 text-sm">
            Synthesized expert report for: <span className="font-semibold text-primary">{report.topic}</span>
          </p>
        </div>

        <div className="flex flex-wrap gap-3">
          <Link
            to={`/graph/${report.project_id}`}
            className="inline-flex items-center space-x-2 bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 px-4 py-2.5 rounded-lg font-semibold transition-all text-sm"
          >
            <GitMerge className="h-4 w-4" />
            <span>Explore Knowledge Graph</span>
          </Link>
          <button
            onClick={handlePrint}
            className="inline-flex items-center space-x-2 bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 px-4 py-2.5 rounded-lg font-semibold transition-all text-sm"
          >
            <Printer className="h-4 w-4" />
            <span>Print Dossier</span>
          </button>
        </div>
      </div>

      {/* Metadata summary cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 print:grid-cols-3">
        {/* Confidence Dial Card */}
        <div className="glass-panel p-6 rounded-xl flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Confidence Assessment</span>
            <p className="text-sm text-slate-400">Score of evidence depth</p>
          </div>
          <div className="relative flex items-center justify-center">
            <svg className="w-16 h-16 transform -rotate-90">
              <circle cx="32" cy="32" r="28" className="stroke-slate-800 fill-none" strokeWidth="6" />
              <circle cx="32" cy="32" r="28" className="stroke-primary fill-none transition-all duration-1000" strokeWidth="6" strokeDasharray={2 * Math.PI * 28} strokeDashoffset={2 * Math.PI * 28 * (1 - (report.confidence_score || 0))} />
            </svg>
            <span className="absolute text-sm font-mono font-bold text-white">{confidencePct}%</span>
          </div>
        </div>

        {/* Model Card */}
        <div className="glass-panel p-6 rounded-xl space-y-1.5 flex flex-col justify-center">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Cognitive Engine</span>
          <div className="flex items-center space-x-2">
            <Compass className="h-5 w-5 text-accent" />
            <span className="text-lg font-bold text-white font-mono">{report.metadata?.model_used || 'qwen3'}</span>
          </div>
        </div>

        {/* Date / Time Card */}
        <div className="glass-panel p-6 rounded-xl space-y-1.5 flex flex-col justify-center">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Synthesized Date</span>
          <div className="flex items-center space-x-2">
            <Clock className="h-5 w-5 text-secondary" />
            <span className="text-base font-bold text-white font-mono">
              {report.created_at ? new Date(report.created_at).toLocaleDateString() : 'N/A'}
            </span>
          </div>
        </div>
      </div>

      {/* Main Tabs Navigation and Section Display */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Left Tabs Column */}
        <div className="lg:col-span-1 flex flex-col space-y-1.5 print:hidden">
          <span className="text-xs font-bold text-slate-500 uppercase tracking-widest pl-3 pb-2">
            Dossier Sections
          </span>
          {Object.keys(SECTION_METADATA).map((key) => {
            const meta = SECTION_METADATA[key];
            const Icon = meta.icon;
            const active = activeTab === key;
            return (
              <button
                key={key}
                onClick={() => setActiveTab(key)}
                className={`
                  w-full flex items-center justify-between px-4 py-3 rounded-lg text-left text-sm font-medium transition-all duration-200
                  ${active 
                    ? 'bg-primary/20 text-white border-l-4 border-primary font-semibold' 
                    : 'text-slate-400 hover:bg-bg-hover hover:text-slate-200'}
                `}
              >
                <div className="flex items-center space-x-2.5">
                  <Icon className={`h-4.5 w-4.5 ${active ? 'text-primary' : 'text-slate-400'}`} />
                  <span>{meta.label}</span>
                </div>
                <ChevronRight className={`h-4 w-4 opacity-50 ${active ? 'block' : 'hidden'}`} />
              </button>
            );
          })}
        </div>

        {/* Right Content Column */}
        <div className="lg:col-span-3 space-y-8 print:col-span-4">
          {/* Active section display */}
          <div className="glass-panel p-8 rounded-xl space-y-6 print:border-none print:shadow-none print:p-0">
            {Object.keys(SECTION_METADATA).map((key) => {
              const meta = SECTION_METADATA[key];
              const Icon = meta.icon;
              const content = report.sections?.[key] || '';
              const isSelected = activeTab === key;

              return (
                <div 
                  key={key} 
                  className={`space-y-6 ${isSelected ? 'block' : 'hidden print:block print:space-y-6 print:border-b print:border-slate-200 print:pb-8'}`}
                >
                  <div className="flex items-center space-x-3 pb-3 border-b border-border print:border-slate-300">
                    <div className={`p-2 rounded-lg bg-slate-800/80 ${meta.color} print:bg-slate-100 print:text-black`}>
                      <Icon className="h-6 w-6" />
                    </div>
                    <h3 className="text-xl font-bold text-white print:text-black">{meta.label}</h3>
                  </div>

                  <div className="text-slate-300 leading-relaxed text-sm whitespace-pre-line font-medium space-y-4 print:text-slate-800">
                    {content || `No content available for section "${meta.label}".`}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Supporting Evidence references */}
          {report.supporting_evidence && (
            <div className="glass-panel p-6 rounded-xl space-y-4 print:hidden">
              <h4 className="text-base font-bold text-white flex items-center space-x-2">
                <Database className="h-5 w-5 text-secondary" />
                <span>Supporting Evidence Records</span>
              </h4>
              <p className="text-xs text-slate-400">
                This dossier was compiled by combining and cross-referencing these underlying agent reports:
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs font-mono text-slate-400">
                <div className="p-3 bg-bg-main/50 rounded border border-border/40">
                  <span className="text-slate-500 font-semibold uppercase block text-[10px]">Fusion Report V2</span>
                  <span className="text-slate-300 mt-1 block truncate">
                    {report.supporting_evidence.fusion_report_id || 'N/A'}
                  </span>
                </div>
                <div className="p-3 bg-bg-main/50 rounded border border-border/40">
                  <span className="text-slate-500 font-semibold uppercase block text-[10px]">Gap Analysis V2</span>
                  <span className="text-slate-300 mt-1 block truncate">
                    {report.supporting_evidence.research_gap_report_id || 'N/A'}
                  </span>
                </div>
                <div className="p-3 bg-bg-main/50 rounded border border-border/40">
                  <span className="text-slate-500 font-semibold uppercase block text-[10px]">Novelty Assessment</span>
                  <span className="text-slate-300 mt-1 block truncate">
                    {report.supporting_evidence.novelty_report_id || 'N/A'}
                  </span>
                </div>
                <div className="p-3 bg-bg-main/50 rounded border border-border/40">
                  <span className="text-slate-500 font-semibold uppercase block text-[10px]">Patent Opportunities</span>
                  <span className="text-slate-300 mt-1 block truncate">
                    {report.supporting_evidence.patent_opportunity_report_id || 'N/A'}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
