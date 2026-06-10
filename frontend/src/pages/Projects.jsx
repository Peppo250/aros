import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';
import { FolderKanban, Calendar, FileText, Search, PlayCircle, GitMerge } from 'lucide-react';

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

export default function Projects() {
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    async function loadProjects() {
      try {
        const data = await api.getProjects();
        setRuns(data);
      } catch (err) {
        console.error('Failed to load runs history', err);
      } finally {
        setLoading(false);
      }
    }
    loadProjects();
  }, []);

  const filteredRuns = runs.filter(run => 
    run.topic.toLowerCase().includes(searchQuery.toLowerCase()) ||
    run.run_id.toLowerCase().includes(searchQuery.toLowerCase())
  );

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
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-white flex items-center space-x-2.5">
            <FolderKanban className="h-8 w-8 text-primary" />
            <span>Research Projects & Runs</span>
          </h2>
          <p className="text-slate-400 mt-1">
            Browse active search runs, track status transitions, and retrieve generated dossiers.
          </p>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="glass-panel p-4 rounded-xl flex items-center space-x-3">
        <Search className="h-5 w-5 text-slate-500 shrink-0 ml-1" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Filter by research topic or Run ID..."
          className="w-full bg-transparent border-none focus:outline-none text-white placeholder-slate-500 text-sm font-medium"
        />
      </div>

      {/* Table grid */}
      <div className="glass-panel rounded-xl overflow-hidden">
        {loading ? (
          <div className="py-24 flex justify-center items-center">
            <div className="h-10 w-10 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
          </div>
        ) : filteredRuns.length === 0 ? (
          <div className="py-16 text-center text-slate-500">
            No projects found matching the filter.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-border text-slate-400 text-xs font-semibold uppercase tracking-wider bg-bg-main/30">
                  <th className="p-4 pl-6">Topic</th>
                  <th className="p-4">Run UUID</th>
                  <th className="p-4">Status</th>
                  <th className="p-4">Pipeline progress</th>
                  <th className="p-4">Date triggered</th>
                  <th className="p-4 pr-6 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/40 text-sm">
                {filteredRuns.map((run) => {
                  const progressVal = PROGRESS_MAP[run.status] !== undefined ? PROGRESS_MAP[run.status] : 0;
                  return (
                    <tr key={run.run_id} className="hover:bg-bg-hover/30 transition-all">
                      <td className="p-4 pl-6 font-semibold text-white truncate max-w-[280px]">
                        {run.topic}
                      </td>
                      <td className="p-4 font-mono text-xs text-slate-400">
                        {run.run_id.slice(0, 18)}...
                      </td>
                      <td className="p-4">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusBadgeClass(run.status)}`}>
                          {run.status.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="p-4">
                        <div className="flex items-center space-x-2">
                          <div className="w-20 bg-slate-800 rounded-full h-1.5 overflow-hidden">
                            <div 
                              className="bg-primary h-full rounded-full transition-all duration-500" 
                              style={{ width: `${progressVal}%` }}
                            />
                          </div>
                          <span className="text-xs font-mono font-medium text-slate-300">{progressVal}%</span>
                        </div>
                      </td>
                      <td className="p-4 text-slate-400 text-xs flex items-center space-x-1.5 pt-6">
                        <Calendar className="h-3.5 w-3.5" />
                        <span>{run.created_at ? new Date(run.created_at).toLocaleDateString() : 'N/A'}</span>
                      </td>
                      <td className="p-4 pr-6 text-right">
                        <div className="flex justify-end space-x-2">
                          <Link 
                            to={`/runs/${run.run_id}`}
                            className="inline-flex items-center space-x-1 text-xs text-slate-300 hover:text-white font-medium bg-slate-800 hover:bg-slate-700 px-3 py-1.5 rounded transition-all border border-slate-700"
                          >
                            <PlayCircle className="h-3.5 w-3.5" />
                            <span>Track</span>
                          </Link>
                          {run.status === 'completed' && (
                            <>
                              <Link 
                                to={`/graph/${run.project_id || run.run_id}`}
                                className="inline-flex items-center space-x-1 text-xs text-secondary hover:text-white font-medium bg-secondary/10 hover:bg-secondary px-3 py-1.5 rounded transition-all"
                              >
                                <GitMerge className="h-3.5 w-3.5" />
                                <span>Graph</span>
                              </Link>
                              <Link 
                                to={`/reports/${run.run_id}`}
                                className="inline-flex items-center space-x-1 text-xs text-emerald-400 hover:text-white font-medium bg-emerald-500/10 hover:bg-emerald-500 px-3 py-1.5 rounded transition-all"
                              >
                                <FileText className="h-3.5 w-3.5" />
                                <span>Report</span>
                              </Link>
                            </>
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
    </div>
  );
}
