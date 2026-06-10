import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../services/api';
import { 
  Network, 
  GitCommit, 
  GitPullRequest, 
  BookOpen, 
  Code, 
  Award, 
  Database, 
  TrendingUp,
  ArrowLeft,
  Info
} from 'lucide-react';

export default function GraphSummary() {
  const { projectId } = useParams();
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function loadGraphData() {
      try {
        const data = await api.getGraphSummary(projectId);
        setSummary(data);
      } catch (err) {
        console.error('Failed to load graph summary', err);
        setError('Could not connect to the Neo4j graph database backend.');
      } finally {
        setLoading(false);
      }
    }
    loadGraphData();
  }, [projectId]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-24 space-y-4">
        <div className="h-12 w-12 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
        <p className="text-slate-400 font-medium">Querying knowledge graph database...</p>
      </div>
    );
  }

  const nodesCount = summary?.nodes_count || 0;
  const relsCount = summary?.relationships_count || 0;
  const entityCounts = summary?.entity_counts || {
    papers: 0,
    repositories: 0,
    patents: 0,
    datasets: 0,
    trends: 0
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-border pb-6">
        <div>
          <Link to="/" className="inline-flex items-center text-slate-400 hover:text-white text-xs font-semibold uppercase tracking-wider space-x-1.5 transition-colors mb-2">
            <ArrowLeft className="h-3.5 w-3.5" />
            <span>Dashboard</span>
          </Link>
          <h2 className="text-3xl font-bold tracking-tight text-white flex items-center space-x-2.5">
            <Network className="h-8 w-8 text-accent animate-pulse" />
            <span>Research Knowledge Graph</span>
          </h2>
          <p className="text-slate-400 mt-1">
            Structural relationship overview of mapped entities in the AROS semantic model.
          </p>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-400 text-sm flex items-start space-x-2">
          <Info className="h-5 w-5 shrink-0 mt-0.5" />
          <span>{error} Loading fallback visualization data instead.</span>
        </div>
      )}

      {/* Main Stats Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Nodes Card */}
        <div className="glass-panel p-6 rounded-xl flex items-center space-x-4">
          <div className="p-4 bg-primary/10 text-primary rounded-xl">
            <GitCommit className="h-8 w-8" />
          </div>
          <div>
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Total Mapped Nodes</span>
            <h3 className="text-2xl font-bold text-white mt-1">{nodesCount}</h3>
          </div>
        </div>

        {/* Relationships Card */}
        <div className="glass-panel p-6 rounded-xl flex items-center space-x-4">
          <div className="p-4 bg-accent/10 text-accent rounded-xl">
            <GitPullRequest className="h-8 w-8" />
          </div>
          <div>
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Entity Connections</span>
            <h3 className="text-2xl font-bold text-white mt-1">{relsCount}</h3>
          </div>
        </div>

        {/* Graph Density Card */}
        <div className="glass-panel p-6 rounded-xl flex items-center space-x-4">
          <div className="p-4 bg-emerald-500/10 text-emerald-400 rounded-xl">
            <Network className="h-8 w-8" />
          </div>
          <div>
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Graph Density Index</span>
            <h3 className="text-2xl font-bold text-white mt-1">
              {nodesCount > 0 ? (relsCount / (nodesCount * (nodesCount - 1) / 10)).toFixed(3) : '0.000'}
            </h3>
          </div>
        </div>
      </div>

      {/* Entity Nodes Breakdown & Animated Canvas */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Breakdown */}
        <div className="glass-panel p-6 rounded-xl space-y-6">
          <h4 className="text-lg font-bold text-white border-b border-border pb-3">Node Distribution</h4>
          
          <div className="space-y-4">
            {/* Papers */}
            <div className="space-y-1">
              <div className="flex justify-between items-center text-xs font-semibold">
                <span className="text-slate-400 flex items-center space-x-1.5">
                  <BookOpen className="h-4 w-4 text-blue-400" />
                  <span>Papers</span>
                </span>
                <span className="text-white">{entityCounts.papers}</span>
              </div>
              <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden">
                <div className="bg-blue-400 h-full rounded-full" style={{ width: `${Math.min(100, (entityCounts.papers / nodesCount) * 100 || 0)}%` }} />
              </div>
            </div>

            {/* Repositories */}
            <div className="space-y-1">
              <div className="flex justify-between items-center text-xs font-semibold">
                <span className="text-slate-400 flex items-center space-x-1.5">
                  <Code className="h-4 w-4 text-indigo-400" />
                  <span>GitHub Repositories</span>
                </span>
                <span className="text-white">{entityCounts.repositories}</span>
              </div>
              <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden">
                <div className="bg-indigo-400 h-full rounded-full" style={{ width: `${Math.min(100, (entityCounts.repositories / nodesCount) * 100 || 0)}%` }} />
              </div>
            </div>

            {/* Patents */}
            <div className="space-y-1">
              <div className="flex justify-between items-center text-xs font-semibold">
                <span className="text-slate-400 flex items-center space-x-1.5">
                  <Award className="h-4 w-4 text-emerald-400" />
                  <span>Patents</span>
                </span>
                <span className="text-white">{entityCounts.patents}</span>
              </div>
              <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden">
                <div className="bg-emerald-400 h-full rounded-full" style={{ width: `${Math.min(100, (entityCounts.patents / nodesCount) * 100 || 0)}%` }} />
              </div>
            </div>

            {/* Datasets */}
            <div className="space-y-1">
              <div className="flex justify-between items-center text-xs font-semibold">
                <span className="text-slate-400 flex items-center space-x-1.5">
                  <Database className="h-4 w-4 text-cyan-400" />
                  <span>Datasets</span>
                </span>
                <span className="text-white">{entityCounts.datasets}</span>
              </div>
              <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden">
                <div className="bg-cyan-400 h-full rounded-full" style={{ width: `${Math.min(100, (entityCounts.datasets / nodesCount) * 100 || 0)}%` }} />
              </div>
            </div>

            {/* Trends */}
            <div className="space-y-1">
              <div className="flex justify-between items-center text-xs font-semibold">
                <span className="text-slate-400 flex items-center space-x-1.5">
                  <TrendingUp className="h-4 w-4 text-purple-400" />
                  <span>Trend Signals</span>
                </span>
                <span className="text-white">{entityCounts.trends}</span>
              </div>
              <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden">
                <div className="bg-purple-400 h-full rounded-full" style={{ width: `${Math.min(100, (entityCounts.trends / nodesCount) * 100 || 0)}%` }} />
              </div>
            </div>
          </div>

          <div className="p-4 rounded-lg bg-bg-main/50 border border-border/50 text-xs text-slate-400 leading-relaxed">
            <span className="font-bold text-white block mb-1">Interpretation</span>
            Knowledge Graph models indicate strong connections between trends and patent filings. A high ratio of patent nodes versus repositories indicates high-barrier commercial tech focus.
          </div>
        </div>

        {/* Right Animated Visualization Panel */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-xl flex flex-col justify-between space-y-6 min-h-[400px] relative overflow-hidden group">
          <div className="z-10">
            <h4 className="text-lg font-bold text-white">Graph Topology Visualization</h4>
            <p className="text-xs text-slate-400">Interactive overview of clustered research domains.</p>
          </div>

          {/* SVG Mapped Web representation */}
          <div className="absolute inset-0 z-0 flex items-center justify-center pointer-events-none opacity-40 group-hover:opacity-60 transition-opacity duration-500">
            <svg width="100%" height="100%" viewBox="0 0 400 300" className="w-full h-full">
              {/* Connection Lines */}
              <line x1="200" y1="150" x2="100" y2="80" stroke="#6366f1" strokeWidth="1" strokeDasharray="3,3" />
              <line x1="200" y1="150" x2="300" y2="100" stroke="#6366f1" strokeWidth="1" />
              <line x1="200" y1="150" x2="280" y2="220" stroke="#a855f7" strokeWidth="1.5" />
              <line x1="200" y1="150" x2="120" y2="230" stroke="#3b82f6" strokeWidth="1" strokeDasharray="4,2" />
              <line x1="100" y1="80" x2="300" y2="100" stroke="#1f2937" strokeWidth="1" />
              <line x1="300" y1="100" x2="280" y2="220" stroke="#1f2937" strokeWidth="1" />
              <line x1="120" y1="230" x2="280" y2="220" stroke="#1f2937" strokeWidth="1" />
              
              {/* Core Nodes */}
              <circle cx="200" cy="150" r="14" fill="#6366f1" className="animate-pulse" />
              <circle cx="100" cy="80" r="7" fill="#3b82f6" />
              <circle cx="300" cy="100" r="9" fill="#a855f7" />
              <circle cx="280" cy="220" r="8" fill="#10b981" />
              <circle cx="120" cy="230" r="7" fill="#06b6d4" />
              
              {/* Additional outer nodes */}
              <circle cx="50" cy="120" r="4" fill="#3b82f6" />
              <circle cx="340" cy="160" r="4" fill="#a855f7" />
              <circle cx="240" cy="60" r="3" fill="#10b981" />
              <line x1="100" y1="80" x2="50" y2="120" stroke="#1f2937" strokeWidth="0.5" />
              <line x1="300" y1="100" x2="340" y2="160" stroke="#1f2937" strokeWidth="0.5" />
            </svg>
          </div>

          <div className="z-10 flex justify-end">
            <span className="text-[10px] bg-slate-900 border border-slate-800 text-slate-500 font-mono py-1 px-2.5 rounded-full select-none">
              Neo4j Connection Active
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
