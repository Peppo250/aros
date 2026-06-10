import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Search, 
  FolderKanban, 
  Network, 
  Terminal,
  Menu,
  X,
  Compass,
  Zap,
  Activity
} from 'lucide-react';

export default function DashboardLayout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  const menuItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Start Research', path: '/research/new', icon: Search },
    { name: 'Projects & Runs', path: '/projects', icon: FolderKanban },
  ];

  const isActive = (path) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  return (
    <div className="min-h-screen bg-bg-main text-slate-100 flex flex-col md:flex-row font-sans">
      {/* Mobile Top Navigation */}
      <header className="md:hidden flex items-center justify-between p-4 bg-bg-card border-b border-border z-30">
        <div className="flex items-center space-x-2">
          <Zap className="h-6 w-6 text-primary" />
          <span className="text-xl font-bold tracking-wider bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
            AROS
          </span>
        </div>
        <button 
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="text-slate-300 hover:text-white focus:outline-none"
        >
          {sidebarOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </header>

      {/* Sidebar Navigation */}
      <aside className={`
        fixed inset-y-0 left-0 z-40 w-64 bg-bg-card border-r border-border transform transition-transform duration-300 ease-in-out md:translate-x-0 md:static md:flex md:flex-col
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        {/* Sidebar Header */}
        <div className="hidden md:flex items-center space-x-3 p-6 border-b border-border">
          <Zap className="h-7 w-7 text-primary animate-pulse" />
          <div>
            <h1 className="text-xl font-bold tracking-wider bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              AROS INTEL
            </h1>
            <p className="text-xs text-muted">Autonomous Research</p>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.path);
            return (
              <Link
                key={item.name}
                to={item.path}
                onClick={() => setSidebarOpen(false)}
                className={`
                  flex items-center space-x-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200
                  ${active 
                    ? 'bg-primary text-white shadow-lg shadow-primary/20 font-semibold' 
                    : 'text-slate-400 hover:bg-bg-hover hover:text-slate-100'}
                `}
              >
                <Icon className={`h-5 w-5 ${active ? 'text-white' : 'text-slate-400'}`} />
                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>

        {/* Sidebar Footer info */}
        <div className="p-4 border-t border-border bg-bg-main/30">
          <div className="flex items-center space-x-2 px-2 py-1 bg-primary/10 rounded-md border border-primary/20">
            <Activity className="h-4 w-4 text-primary animate-pulse" />
            <span className="text-[11px] text-primary font-medium tracking-wide uppercase">
              Orchestrator v1.0
            </span>
          </div>
        </div>
      </aside>

      {/* Backdrop overlay for mobile sidebar */}
      {sidebarOpen && (
        <div 
          onClick={() => setSidebarOpen(false)}
          className="fixed inset-0 bg-black/60 z-30 md:hidden backdrop-blur-sm"
        />
      )}

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-w-0 overflow-x-hidden">
        {/* Header/Top Bar */}
        <header className="hidden md:flex items-center justify-between px-8 py-5 border-b border-border bg-bg-card/50 backdrop-blur-md">
          <div className="flex items-center space-x-2">
            <Compass className="h-5 w-5 text-accent" />
            <span className="text-sm font-medium text-slate-400">
              System Gateway Online
            </span>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 px-3 py-1.5 rounded-full bg-slate-800/80 border border-slate-700 text-xs">
              <span className="h-2 w-2 rounded-full bg-emerald-500 animate-ping"></span>
              <span className="text-slate-300 font-mono">n8n Connected</span>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <div className="flex-1 p-6 md:p-8 overflow-y-auto">
          {children}
        </div>
      </main>
    </div>
  );
}
