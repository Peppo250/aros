import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { Sparkles, AlertCircle, Search, Cpu } from 'lucide-react';

export default function NewResearch() {
  const [topic, setTopic] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!topic.trim()) {
      setError('A research topic/keyword is required.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const result = await api.startResearch(topic.trim());
      // On success, redirect to the run tracker page
      navigate(`/runs/${result.run_id}`);
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.detail || 
        'Could not initiate research pipeline. Please verify the backend is running.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-8 animate-fadeIn">
      {/* Header */}
      <div>
        <h2 className="text-3xl font-bold tracking-tight text-white flex items-center space-x-2">
          <Sparkles className="h-8 w-8 text-accent animate-pulse" />
          <span>Launch Autonomous Agent</span>
        </h2>
        <p className="text-slate-400 mt-2">
          Initiate a multi-source intelligence collection and analysis pipeline. This will spin up agents to compile papers, repositories, trends, and patent white space.
        </p>
      </div>

      {/* Main input form */}
      <form onSubmit={handleSubmit} className="glass-panel p-8 rounded-xl space-y-6">
        {error && (
          <div className="flex items-start space-x-2.5 p-4 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm">
            <AlertCircle className="h-5 w-5 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        {/* Input: Topic */}
        <div className="space-y-2">
          <label htmlFor="topic" className="text-sm font-semibold text-slate-300 flex items-center space-x-1.5">
            <Search className="h-4 w-4 text-primary" />
            <span>Research Topic / Core Subject</span>
          </label>
          <input
            id="topic"
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            disabled={loading}
            placeholder="e.g., edge ai mesh networks, solid state battery solid-electrolyte interface..."
            className="w-full bg-bg-main border border-border hover:border-slate-600 focus:border-primary focus:outline-none rounded-lg px-4 py-3 text-white placeholder-slate-500 transition-all font-medium"
          />
          <p className="text-xs text-slate-500">
            Provide a specific, descriptive phrase to focus the knowledge extraction.
          </p>
        </div>

        {/* Input: Description */}
        <div className="space-y-2">
          <label htmlFor="description" className="text-sm font-semibold text-slate-300 flex items-center space-x-1.5">
            <Cpu className="h-4 w-4 text-accent" />
            <span>Optional Scope parameters (description)</span>
          </label>
          <textarea
            id="description"
            rows="3"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            disabled={loading}
            placeholder="Add context or define limits for literature extraction..."
            className="w-full bg-bg-main border border-border hover:border-slate-600 focus:border-accent focus:outline-none rounded-lg px-4 py-3 text-white placeholder-slate-500 transition-all text-sm"
          />
        </div>

        {/* Start button */}
        <button
          type="submit"
          disabled={loading}
          className="w-full flex items-center justify-center space-x-2 bg-gradient-to-r from-primary to-accent hover:from-primary-hover hover:to-accent-hover text-white py-3 px-5 rounded-lg font-bold transition-all duration-300 disabled:opacity-50 glow-indigo"
        >
          {loading ? (
            <>
              <div className="h-5 w-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Spawning Agents & n8n Hooks...</span>
            </>
          ) : (
            <>
              <Sparkles className="h-5 w-5" />
              <span>Trigger Pipeline Execution</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
}
