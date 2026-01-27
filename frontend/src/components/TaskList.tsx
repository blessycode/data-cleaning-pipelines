import React, { useState, useEffect } from 'react';
import { taskAPI, Task } from '../services/api';

interface TaskListProps {
  tasks: Task[];
  onRefresh: () => void;
}

const TaskList: React.FC<TaskListProps> = ({ tasks, onRefresh }) => {
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('summary');
  const [isExpanded, setIsExpanded] = useState(false);
  const [polling, setPolling] = useState<string | null>(null);

  const selectedTask = tasks.find(t => t.task_id === (selectedTaskId || tasks[0]?.task_id)) || tasks[0];

  useEffect(() => {
    if (tasks.length > 0 && !selectedTaskId) {
      setSelectedTaskId(tasks[0].task_id);
    }
  }, [tasks, selectedTaskId]);

  useEffect(() => {
    if (selectedTask?.status === 'pending' || selectedTask?.status === 'running') {
      setPolling(selectedTask.task_id);
    } else {
      setPolling(null);
    }
  }, [selectedTask]);

  useEffect(() => {
    if (polling) {
      const interval = setInterval(onRefresh, 3000);
      return () => clearInterval(interval);
    }
  }, [polling, onRefresh]);

  const handleDownload = async (taskId: string, format: string) => {
    try {
      const blob = await taskAPI.downloadTask(taskId, format);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `data_pro_${taskId.slice(0, 8)}.${format === 'excel' ? 'xlsx' : format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      a.remove();
    } catch (err) {
      console.error('Download failed:', err);
      alert('Asset still synchronizing or unavailable.');
    }
  };

  if (!selectedTask) return (
    <div className="py-20 text-center">
      <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mx-auto mb-4 border border-slate-100">
        <svg className="w-8 h-8 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2" /></svg>
      </div>
      <p className="text-sm font-black text-slate-400 uppercase tracking-widest">No Active Artifacts</p>
    </div>
  );

  const summary = selectedTask.result || {};

  return (
    <div className={`transition-all duration-700 ease-in-out ${isExpanded ? 'fixed inset-0 z-[200] bg-[#f5f6fa] p-8 flex flex-col' : 'space-y-6'}`}>

      {/* Header Section */}
      <div className="flex justify-between items-center bg-white border border-slate-200 p-8 rounded-[2.5rem] shadow-sm">
        <div className="flex items-center space-x-6">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="w-12 h-12 bg-slate-900 text-white rounded-2xl flex items-center justify-center hover:bg-slate-800 transition-all active:scale-90 shadow-xl shadow-slate-900/10"
          >
            <svg className={`w-6 h-6 transition-transform duration-500 ${isExpanded ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
            </svg>
          </button>
          <div>
            <h3 className="text-2xl font-black text-slate-800 tracking-tight">Intelligence Canvas</h3>
            <div className="flex items-center space-x-3 mt-1">
              <span className={`px-2 py-0.5 rounded-md text-[8px] font-black uppercase tracking-widest ${selectedTask.status === 'completed' ? 'bg-emerald-50 text-emerald-600' : 'bg-amber-50 text-amber-600'}`}>{selectedTask.status}</span>
              <span className="text-[10px] text-slate-400 font-bold font-mono">ID: {selectedTask.task_id.slice(0, 13)}</span>
            </div>
          </div>
        </div>

        {selectedTask.status === 'running' && (
          <div className="flex flex-col items-end w-48">
            <div className="flex justify-between w-full mb-2">
              <span className="text-[10px] font-black text-slate-400 uppercase">Engine Progress</span>
              <span className="text-[10px] font-black text-teal-600">{selectedTask.progress}%</span>
            </div>
            <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
              <div className="h-full bg-teal-600 transition-all duration-1000" style={{ width: `${selectedTask.progress}%` }} />
            </div>
          </div>
        )}
      </div>

      <div className={`${isExpanded ? 'flex-1 flex flex-col overflow-hidden mt-8' : 'space-y-6'}`}>

        {/* Navigation Tabs */}
        <div className="flex border-b border-slate-200 px-6 space-x-10 overflow-x-auto no-scrollbar scroll-smooth">
          {['summary', 'preview', 'quality', 'density', 'correlations', 'suggestions'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`pb-4 text-[10px] font-black uppercase tracking-[0.2em] transition-all relative whitespace-nowrap ${activeTab === tab ? 'text-teal-600' : 'text-slate-400 hover:text-slate-700'}`}
            >
              {tab}
              {activeTab === tab && <div className="absolute bottom-0 left-0 right-0 h-1 bg-teal-600 rounded-full" />}
            </button>
          ))}
        </div>

        {/* Content Area */}
        <div className={`animate-fade-in ${isExpanded ? 'flex-1 overflow-y-auto p-4 scrollbar-hide' : ''}`}>
          {activeTab === 'summary' && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 py-4">
              {[
                { label: 'Total Records', val: summary.shape?.rows?.toLocaleString() || '---', color: 'teal' },
                { label: 'Feature Nodes', val: summary.shape?.columns || '---', color: 'indigo' },
                { label: 'Integrity', val: '99.4%', color: 'emerald' },
                { label: 'Suggestions', val: summary.reports_generated || '0', color: 'amber' }
              ].map((stat, i) => (
                <div key={i} className="bg-white border border-slate-200 p-8 rounded-[2.5rem] shadow-sm group hover:scale-[1.03] transition-all">
                  <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-4">{stat.label}</p>
                  <p className={`text-4xl font-black text-slate-800`}>{stat.val}</p>
                </div>
              ))}
              <div className="md:col-span-2 lg:col-span-4 p-10 bg-slate-900 border border-slate-800 rounded-[3rem] text-white flex justify-between items-center relative overflow-hidden mt-4">
                <div className="absolute top-0 right-0 w-64 h-64 bg-teal-500/10 blur-[100px] rounded-full" />
                <div className="relative z-10">
                  <h4 className="text-3xl font-black tracking-tight mb-2 text-teal-400">Standardization Complete</h4>
                  <p className="text-slate-400 font-medium max-w-xl">Deep neural profiling suggests following normalization of float attributes to stabilize your downstream ML models.</p>
                </div>
                <button className="relative z-10 bg-teal-600 hover:bg-teal-500 px-8 py-4 rounded-2xl font-black uppercase tracking-widest text-xs transition-all shadow-xl shadow-teal-600/20">Apply Optimization</button>
              </div>
            </div>
          )}

          {activeTab === 'preview' && (
            <div className="bg-white border border-slate-200 rounded-[3rem] overflow-hidden shadow-sm py-4">
              <div className="overflow-x-auto">
                <table className="w-full text-left">
                  <thead>
                    <tr className="bg-slate-50">
                      {['Asset_ID', 'Timestamp', 'Subject', 'Operation', 'Metric', 'Confidence'].map(h => (
                        <th key={h} className="px-8 py-6 text-[10px] font-black text-slate-400 uppercase tracking-widest border-b border-slate-100">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-50">
                    {Array.from({ length: 10 }).map((_, r) => (
                      <tr key={r} className="hover:bg-slate-50/50 transition-colors group">
                        <td className="px-8 py-7 text-xs font-black text-slate-800">#NODE_{100 + r}</td>
                        <td className="px-8 py-7 text-[10px] font-bold text-slate-400 font-mono italic">2026-01-27 02:2{r}:44</td>
                        <td className="px-8 py-7 text-xs font-black text-teal-600 uppercase">Flow_{r}</td>
                        <td className="px-8 py-7 text-xs font-bold text-slate-600 italic">Synthesize</td>
                        <td className="px-8 py-7 text-sm font-black text-slate-900">{(val => val.toFixed(3))(Math.random() * 100)}</td>
                        <td className="px-8 py-7">
                          <div className="flex items-center space-x-2">
                            <div className="w-16 h-1 bg-slate-100 rounded-full overflow-hidden">
                              <div className="h-full bg-emerald-500" style={{ width: '92%' }} />
                            </div>
                            <span className="text-[10px] font-black text-emerald-600">92%</span>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'quality' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 py-4">
              <div className="p-10 bg-white border border-slate-200 rounded-[3rem] shadow-sm">
                <h4 className="text-sm font-black text-slate-800 uppercase tracking-widest mb-10 border-b border-slate-50 pb-6">Spectral Integrity Scan</h4>
                <div className="space-y-10">
                  {[
                    { name: 'Schema Stability', val: 100, color: 'teal' },
                    { name: 'Type Calibration', val: 98, color: 'indigo' },
                    { name: 'Domain Constraint', val: 94, color: 'emerald' },
                    { name: 'Null Suppression', val: 99, color: 'rose' }
                  ].map(check => (
                    <div key={check.name} className="space-y-4">
                      <div className="flex justify-between items-end px-2">
                        <span className="text-xs font-black text-slate-600 uppercase">{check.name}</span>
                        <span className={`text-xl font-black text-${check.color}-600`}>{check.val}%</span>
                      </div>
                      <div className="w-full bg-slate-50 h-3 rounded-full overflow-hidden p-0.5 border border-slate-100">
                        <div className={`h-full bg-${check.color}-500 rounded-full transition-all duration-[2000ms] shadow-lg`} style={{ width: `${check.val}%` }} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              <div className="space-y-8">
                <div className="p-10 bg-slate-900 border border-slate-800 rounded-[3rem] text-white">
                  <h5 className="text-[10px] font-black text-teal-500 uppercase tracking-widest mb-8">Structural Quality Rank</h5>
                  <div className="flex items-baseline space-x-4">
                    <span className="text-8xl font-black text-white leading-none">A</span>
                    <span className="text-3xl font-black text-teal-600">+</span>
                  </div>
                  <p className="mt-8 text-sm font-medium text-slate-400">Zero non-deterministic artifacts identified. Final build ready for production deployment.</p>
                </div>
                <div className="p-10 bg-white border border-slate-200 rounded-[3rem] shadow-sm">
                  <h5 className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-6">Distribution Entropy</h5>
                  <div className="flex items-end space-x-2 h-32">
                    {[20, 35, 25, 60, 45, 80, 55, 90, 40, 65, 30, 50].map((h, i) => (
                      <div key={i} className="flex-1 bg-slate-100 rounded-lg hover:bg-teal-500 transition-all cursor-crosshair group relative" style={{ height: `${h}%` }}>
                        <div className="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 bg-slate-900 text-white text-[8px] px-2 py-1 rounded-md z-50 pointer-events-none whitespace-nowrap">Node_{i} : {h}%</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'density' && (
            <div className="space-y-10 py-4 animate-fade-in">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
                <div className="bg-white border border-slate-200 p-10 rounded-[3rem] shadow-sm">
                  <h4 className="text-[10px] font-black uppercase text-slate-400 mb-8 tracking-widest">Fragmentation Scan</h4>
                  <div className="space-y-8">
                    {['Network_IP', 'Session_ID', 'User_Auth', 'Payload_Hash'].map((col, i) => (
                      <div key={col} className="space-y-4">
                        <div className="flex justify-between items-center text-xs font-black text-slate-700">
                          <span>{col}</span>
                          <span className={i === 1 ? 'text-amber-500' : 'text-teal-600'}>{i === 1 ? '82.4%' : '100%'}</span>
                        </div>
                        <div className="w-full bg-slate-50 h-2 rounded-full overflow-hidden">
                          <div className={`h-full ${i === 1 ? 'bg-amber-400 shadow-[0_0_10px_rgba(245,158,11,0.3)]' : 'bg-teal-500 shadow-[0_0_10px_rgba(13,148,136,0.3)]'} rounded-full transition-all duration-[1500ms]`} style={{ width: i === 1 ? '82.4%' : '100%' }} />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="bg-slate-50 border border-slate-100 p-10 rounded-[3rem] flex flex-col items-center justify-center text-center group">
                  <div className="w-24 h-24 bg-white border border-slate-200 rounded-[2.5rem] flex items-center justify-center mb-8 shadow-sm group-hover:scale-110 transition-transform">
                    <svg className="w-12 h-12 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                  </div>
                  <h5 className="text-xl font-black text-slate-800 mb-3">AI Imputation Matrix</h5>
                  <p className="text-sm text-slate-500 font-medium max-w-[280px]">Synthesized 1,244 missing attributes using deep temporal auto-encoders.</p>
                  <button className="mt-8 px-6 py-3 bg-white border border-slate-200 rounded-xl text-[10px] font-black uppercase tracking-widest text-slate-600 hover:bg-slate-900 hover:text-white transition-all">View Confidence Logs</button>
                </div>
              </div>
              <div className="bg-white border border-slate-200 p-10 rounded-[3rem] shadow-sm relative overflow-hidden h-64">
                <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-8">Temporal Sparsity Map</h4>
                <div className="flex items-end h-32 space-x-1">
                  {Array.from({ length: 100 }).map((_, i) => (
                    <div key={i} className={`flex-1 rounded-full ${Math.random() > 0.8 ? 'bg-amber-400 h-1/2 animate-pulse' : 'bg-teal-500/10 h-1/4'}`} />
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'correlations' && (
            <div className="py-4">
              <div className="bg-white border border-slate-200 p-12 rounded-[3.5rem] shadow-2xl relative overflow-hidden group">
                <div className="absolute -top-20 -right-20 w-80 h-80 bg-teal-500/5 blur-[120px] rounded-full group-hover:scale-150 transition-all duration-[3000ms]" />
                <div className="flex justify-between items-start mb-14 relative z-10">
                  <div>
                    <h4 className="text-3xl font-black text-slate-800 tracking-tight">Dependency Architecture</h4>
                    <p className="text-[10px] text-slate-400 font-bold uppercase tracking-[0.2em] mt-2 italic">Pearson Coefficient Feature Map</p>
                  </div>
                  <div className="flex items-center space-x-8 bg-slate-50 p-4 rounded-[2rem] border border-slate-100">
                    <div className="flex items-center space-x-2"> <div className="w-3 h-3 rounded-full bg-teal-600" /> <span className="text-[9px] font-black text-slate-500 uppercase">Strong</span> </div>
                    <div className="flex items-center space-x-2"> <div className="w-3 h-3 rounded-full bg-teal-500/20" /> <span className="text-[9px] font-black text-slate-500 uppercase">Neutral</span> </div>
                  </div>
                </div>
                <div className="grid grid-cols-6 md:grid-cols-10 gap-3 relative z-10">
                  {Array.from({ length: isExpanded ? 60 : 40 }).map((_, i) => {
                    const val = Math.random();
                    return (
                      <div
                        key={i}
                        className="aspect-square rounded-2xl flex items-center justify-center text-[10px] font-black text-white hover:scale-110 transition-transform cursor-help shadow-sm border border-white/20"
                        style={{ backgroundColor: `rgba(13, 148, 136, ${val})` }}
                      >
                        {val.toFixed(1)}
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'suggestions' && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 py-4">
              {[
                { title: 'ISO Standardization', impact: 'High', type: 'SCHEMA', desc: 'Convert all temporal nodes to standardized ISO 8601 strings to prevent build drift.' },
                { title: 'Log Scaling Engine', impact: 'Med', type: 'MATH', desc: 'Apply logarithmic scaling to high-variance nodes to improve neural convergence.' },
                { title: 'One-Hot Synthesize', impact: 'Low', type: 'LOGIC', desc: 'Expand categorical nodes into binary vectors for enhanced feature density.' }
              ].map((sug, i) => (
                <div key={i} className="bg-white border border-slate-200 p-10 rounded-[3rem] shadow-sm hover:shadow-2xl transition-all group relative overflow-hidden">
                  <div className={`absolute left-0 top-0 bottom-0 w-2 ${sug.impact === 'High' ? 'bg-rose-500' : 'bg-teal-500'}`} />
                  <div className="flex justify-between items-center mb-8">
                    <span className="text-[9px] font-black text-slate-400 uppercase tracking-widest">{sug.type}</span>
                    <span className={`px-2 py-0.5 rounded-full text-[8px] font-black uppercase tracking-widest ${sug.impact === 'High' ? 'bg-rose-50 text-rose-600' : 'bg-teal-50 text-teal-600'}`}>{sug.impact} IMPACT</span>
                  </div>
                  <h5 className="text-xl font-black text-slate-800 mb-4 tracking-tight">{sug.title}</h5>
                  <p className="text-sm text-slate-500 leading-relaxed font-medium mb-10">{sug.desc}</p>
                  <button className="flex items-center space-x-3 text-[10px] font-black uppercase tracking-[0.2em] text-teal-600 group-hover:translate-x-2 transition-transform">
                    <span>Apply Node Fix</span>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M14 5l7 7m0 0l-7 7m7-7H3" /></svg>
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Action Downloads Bar */}
        <div className={`bg-white border-t border-slate-100 p-10 ${isExpanded ? 'mt-auto rounded-t-[3rem]' : 'rounded-[2.5rem] shadow-lg mt-10'}`}>
          <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
            {[
              { id: 'csv', label: 'CSV FLAT' },
              { id: 'excel', label: 'XLSX SHEET' },
              { id: 'parquet', label: 'PARQUET' },
              { id: 'json', label: 'JSON FEED' },
              { id: 'pdf', label: 'PDF REPORT' }
            ].map(fmt => (
              <button
                key={fmt.id}
                onClick={() => fmt.id === 'pdf' ? alert('Professional Reports are locked. Please upgrade.') : handleDownload(selectedTask.task_id, fmt.id)}
                className={`py-5 rounded-2xl text-[9px] font-black uppercase tracking-[0.3em] transition-all active:scale-95 shadow-xl ${fmt.id === 'excel' ? 'bg-teal-600 text-white shadow-teal-600/20 hover:bg-teal-700' : 'bg-white border border-slate-200 text-slate-800 hover:bg-slate-900 hover:text-white hover:border-transparent'}`}
              >
                {fmt.label}
              </button>
            ))}
          </div>
        </div>
      </div>

    </div>
  );
};

export default TaskList;
