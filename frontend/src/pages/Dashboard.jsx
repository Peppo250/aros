import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';
import { 
  FolderKanban, 
  PlayCircle, 
  CheckCircle2, 
  Award,
  Plus,
  ArrowRight,
  TrendingUp,
  Clock
} from 'lucide-react';

const PROGRESS_MAP = {
  "queued": 0,
  "papers_completed": 10,
  "github_completed": 20,
  "patents_completed": 30,
  "datasets_completed": 40,
  "trends_completed": 50,
  "citations_completed": 60,
  "graph_completed": 70,
  "fusion_completed": 80,
  "gap_completed": 85,
  "novelty_completed": 90,
  "patent_completed": 95,
  "report_completed": 99,
  "completed": 100,
  "failed": 0
};

export default function Dashboard() {
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const data = await api.getProjects();
        setRuns(data);
      } catch (err) {
        console.error('Error loading projects', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const totalProjects = new Set(runs.map(r => r.project_id || r.id)).size;
  const activeRuns = runs.filter(r => r.status !== 'completed' && r.status !== 'failed').length;
  const completedRuns = runs.filter(r => r.status === 'completed').length;
  const avgNovelty = 0.78; // Hardcoded default placeholder value

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20';
      case 'failed':
        return 'bg-rose-500/10 text-rose-400 border border-rose-500/20';
      case 'queued':
        return 'bg-amber-500/10 text-amber-400 border border-amber-500/20';
      default:
        return 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20';
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header section */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-white">Research Workspace</h2>
          <p className="text-slate-400 mt-1">Autonomous orchestration agent metrics and reports dashboard.</p>
        </div>
        <Link
          to="/research/new"
          className="inline-flex items-center justify-center space-x-2 bg-primary hover:bg-primary-hover text-white px-5 py-3 rounded-lg font-semibold transition-all duration-200 glow-indigo"
        >
          <Plus className="h-5 w-5" />
          <span>New Research Run</span>
        </Link>
      </div>

      {/* Overview stats cards grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Card 1: Total Projects */}
        <div className="glass-panel p-6 rounded-xl relative overflow-hidden group hover:border-primary/30 transition-all duration-300">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm font-medium text-slate-400 uppercase tracking-wider">Total Projects</p>
              <h3 className="text-3xl font-bold text-white mt-2">{loading ? '...' : totalProjects}</h3>
            </div>
            <div className="p-3 rounded-lg bg-indigo-500/10 text-primary">
              <FolderKanban className="h-6 w-6" />
            </div>
          </div>
          <div className="absolute bottom-0 inset-x-0 h-1 bg-gradient-to-r from-primary/40 to-transparent" />
        </div>

        {/* Card 2: Active Runs */}
        <div className="glass-panel p-6 rounded-xl relative overflow-hidden group hover:border-indigo-400/30 transition-all duration-300">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm font-medium text-slate-400 uppercase tracking-wider">Active Pipeline Runs</p>
              <h3 className="text-3xl font-bold text-white mt-2">{loading ? '...' : activeRuns}</h3>
            </div>
            <div className="p-3 rounded-lg bg-blue-500/10 text-secondary">
              <PlayCircle className="h-6 w-6" />
            </div>
          </div>
          <div className="absolute bottom-0 inset-x-0 h-1 bg-gradient-to-r from-secondary/40 to-transparent" />
        </div>

        {/* Card 3: Completed */}
        <div className="glass-panel p-6 rounded-xl relative overflow-hidden group hover:border-emerald-500/30 transition-all duration-300">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm font-medium text-slate-400 uppercase tracking-wider">Completed Dossiers</p>
              <h3 className="text-3xl font-bold text-white mt-2">{loading ? '...' : completedRuns}</h3>
            </div>
            <div className="p-3 rounded-lg bg-emerald-500/10 text-emerald-400">
              <CheckCircle2 className="h-6 w-6" />
            </div>
          </div>
          <div className="absolute bottom-0 inset-x-0 h-1 bg-gradient-to-r from-emerald-500/40 to-transparent" />
        </div>

        {/* Card 4: Avg Novelty Score */}
        <div className="glass-panel p-6 rounded-xl relative overflow-hidden group hover:border-accent/30 transition-all duration-300">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm font-medium text-slate-400 uppercase tracking-wider">Avg Novelty Score</p>
              <h3 className="text-3xl font-bold text-white mt-2">
                {loading ? '...' : `${(avgNovelty * 100).toFixed(0)}%`}
              </h3>
            </div>
            <div className="p-3 rounded-lg bg-purple-500/10 text-accent">
              <Award className="h-6 w-6" />
            </div>
          </div>
          <div className="absolute bottom-0 inset-x-0 h-1 bg-gradient-to-r from-accent/40 to-transparent" />
        </div>
      </div>

      {/* Main dashboard content sections */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left column: Recent runs table (spans 2 cols) */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-xl space-y-6">
          <div className="flex justify-between items-center">
            <h4 className="text-xl font-bold text-white">Recent Research Runs</h4>
            <Link to="/projects" className="text-sm text-primary hover:text-white flex items-center space-x-1 font-medium transition-all">
              <span>View all runs</span>
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>

          {loading ? (
            <div className="py-12 flex justify-center items-center">
              <div className="h-8 w-8 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
            </div>
          ) : runs.length === 0 ? (
            <div className="py-12 text-center text-slate-500 border border-dashed border-border rounded-xl">
              No runs recorded yet. Get started by entering your first topic!
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-border text-slate-400 text-xs font-semibold uppercase tracking-wider">
                    <th className="pb-3">Topic / Subject</th>
                    <th className="pb-3">Run ID</th>
                    <th className="pb-3">Status</th>
                    <th className="pb-3">Progress</th>
                    <th className="pb-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/50 text-sm">
                  {runs.slice(0, 5).map((run) => {
                    const progressVal = PROGRESS_MAP[run.status] !== undefined ? PROGRESS_MAP[run.status] : 0;
                    return (
                      <tr key={run.run_id} className="hover:bg-bg-hover/30 transition-all">
                        <td className="py-4 pr-3 font-semibold text-white truncate max-w-[200px]">
                          {run.topic}
                        </td>
                        <td className="py-4 text-slate-400 font-mono text-xs">
                          {run.run_id.slice(0, 8)}...
                        </td>
                        <td className="py-4">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusBadgeClass(run.status)}`}>
                            {run.status.replace('_', ' ')}
                          </span>
                        </td>
                        <td className="py-4">
                          <div className="flex items-center space-x-2">
                            <div className="w-16 bg-slate-800 rounded-full h-1.5 overflow-hidden">
                              <div 
                                className="bg-primary h-full rounded-full transition-all duration-500" 
                                style={{ width: `${progressVal}%` }}
                              />
                            </div>
                            <span className="text-xs font-mono font-medium text-slate-300">{progressVal}%</span>
                          </div>
                        </td>
                        <td className="py-4 text-right">
                          <div className="flex justify-end space-x-3">
                            <Link 
                              to={`/runs/${run.run_id}`}
                              className="text-xs text-primary hover:text-white font-medium bg-primary/10 hover:bg-primary px-3 py-1.5 rounded transition-all"
                            >
                              Track
                            </Link>
                            {run.status === 'completed' && (
                              <Link 
                                to={`/reports/${run.run_id}`}
                                className="text-xs text-emerald-400 hover:text-white font-medium bg-emerald-500/10 hover:bg-emerald-500 px-3 py-1.5 rounded transition-all"
                              >
                                Dossier
                              </Link>
                            )}
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Right column: Quick information / guide card */}
        <div className="space-y-6">
          <div className="glass-panel p-6 rounded-xl space-y-4 relative overflow-hidden">
            <div className="p-3 bg-primary/10 text-primary w-fit rounded-lg border border-primary/20">
              <TrendingUp className="h-6 w-6" />
            </div>
            <h4 className="text-lg font-bold text-white">How AROS Pipeline Works</h4>
            <p className="text-sm text-slate-400 leading-relaxed">
              AROS triggers an automated backend research orchestration cycle through <strong>n8n webhooks</strong>.
            </p>
            <ul className="text-xs text-slate-400 space-y-2.5 font-medium">
              <li className="flex items-center space-x-2">
                <span className="h-1.5 w-1.5 bg-primary rounded-full"></span>
                <span>1. Scrapes academic papers & patents</span>
              </li>
              <li className="flex items-center space-x-2">
                <span className="h-1.5 w-1.5 bg-primary rounded-full"></span>
                <span>2. Gathers Github repos & search trends</span>
              </li>
              <li className="flex items-center space-x-2">
                <span className="h-1.5 w-1.5 bg-primary rounded-full"></span>
                <span>3. Builds a knowledge graph model</span>
              </li>
              <li className="flex items-center space-x-2">
                <span className="h-1.5 w-1.5 bg-primary rounded-full"></span>
                <span>4. Analyzes novelty & patent whitespace</span>
              </li>
              <li className="flex items-center space-x-2">
                <span className="h-1.5 w-1.5 bg-primary rounded-full"></span>
                <span>5. Compiles synthesized final dossier report</span>
              </li>
            </ul>
          </div>

          <div className="glass-panel p-6 rounded-xl space-y-4">
            <div className="flex items-center space-x-2 text-slate-200">
              <Clock className="h-5 w-5 text-accent" />
              <h4 className="text-base font-bold">Recent Graph Counts</h4>
            </div>
            <p className="text-xs text-slate-400">
              Visualizes cross-connections across all data endpoints to discover white space.
            </p>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-bg-hover/40 border border-border/50 p-3 rounded-lg text-center">
                <span className="text-xs text-slate-400">Graph Nodes</span>
                <p className="text-xl font-bold text-white mt-1">1,248</p>
              </div>
              <div className="bg-bg-hover/40 border border-border/50 p-3 rounded-lg text-center">
                <span className="text-xs text-slate-400">Relationships</span>
                <p className="text-xl font-bold text-white mt-1">4,912</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
