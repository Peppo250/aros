import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import DashboardLayout from './layouts/DashboardLayout';
import Dashboard from './pages/Dashboard';
import NewResearch from './pages/NewResearch';
import RunDetails from './pages/RunDetails';
import ReportViewer from './pages/ReportViewer';
import Projects from './pages/Projects';
import GraphSummary from './pages/GraphSummary';

export default function App() {
  return (
    <Router>
      <DashboardLayout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/research/new" element={<NewResearch />} />
          <Route path="/runs/:runId" element={<RunDetails />} />
          <Route path="/reports/:runId" element={<ReportViewer />} />
          <Route path="/projects" element={<Projects />} />
          <Route path="/graph/:projectId" element={<GraphSummary />} />
        </Routes>
      </DashboardLayout>
    </Router>
  );
}
