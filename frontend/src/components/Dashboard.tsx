import React, { useState, useEffect, useCallback, useRef } from 'react';
import { taskAPI, Task } from '../services/api';
import Navbar from './Navbar';
import FileUpload from './FileUpload';
import TaskList from './TaskList';

const Dashboard: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeDataset, setActiveDataset] = useState<string | null>(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [logHistory, setLogHistory] = useState<string[]>([]);
  const lastMsgRef = useRef<string | null>(null);
  const logEndRef = useRef<HTMLDivElement | null>(null);

  const fetchTasks = useCallback(async () => {
    try {
      const response = await taskAPI.listTasks();
      setTasks(response.data.tasks || response.data || []); // Adjust based on your API response structure
    } catch (error) {
      console.error('Failed to fetch tasks:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTasks();
    const interval = setInterval(fetchTasks, 10000);
    return () => clearInterval(interval);
  }, [fetchTasks]);

  const activeTaskObj = tasks.find(t => t.task_id === activeDataset);

  useEffect(() => {
    if (activeTaskObj?.message && activeTaskObj.message !== lastMsgRef.current) {
      setLogHistory(prev => [...prev, `${new Date().toLocaleTimeString()} > ${activeTaskObj.message}`]);
      lastMsgRef.current = activeTaskObj.message;
    }
    if (!activeDataset) {
      setLogHistory([]);
      lastMsgRef.current = null;
    }
  }, [activeTaskObj?.message, activeDataset]);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logHistory]);

  const handleTaskCreated = () => {
    fetchTasks();
  };

  return (
    <div className="min-h-screen bg-[#f5f6fa] flex flex-col overflow-hidden">
      <Navbar />

      {/* Three Panel Layout */}
      <div className="flex-1 pt-16 flex h-[calc(100vh-64px)] overflow-hidden">

        {/* Left Side: Datasets Sidebar */}
        <aside className={`${sidebarCollapsed ? 'w-20' : 'w-80'} bg-white border-r border-slate-200 flex flex-col flex-shrink-0 transition-all duration-500 ease-in-out relative z-30 shadow-[1px_0_10px_rgba(0,0,0,0.02)]`}>
          <button
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className="absolute -right-4 top-10 w-8 h-8 bg-white border border-slate-200 rounded-full flex items-center justify-center text-slate-400 hover:text-teal-600 shadow-md z-40 transition-all active:scale-95"
          >
            <svg className={`w-4 h-4 transition-transform duration-500 ${sidebarCollapsed ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M15 19l-7-7 7-7" /></svg>
          </button>

          {!sidebarCollapsed ? (
            <>
              <div className="p-6 border-b border-slate-100">
                <h2 className="text-xs font-black text-slate-400 uppercase tracking-widest mb-4">Ingestion Source</h2>
                <div className="space-y-2">
                  {['Local File Upload', 'Database Connector', 'External API Feed'].map((src) => (
                    <button key={src} className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-sm font-bold transition-all ${src === 'Local File Upload' ? 'bg-teal-50 text-teal-700 shadow-sm' : 'text-slate-500 hover:bg-slate-50'}`}>
                      <svg className="w-5 h-5 opacity-70" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" /></svg>
                      <span>{src}</span>
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex-1 overflow-y-auto p-6 scrollbar-hide">
                <h2 className="text-xs font-black text-slate-400 uppercase tracking-widest mb-4">Recent Datasets</h2>
                <div className="space-y-3">
                  {tasks.length > 0 ? tasks.slice(0, 8).map((t) => (
                    <div key={t.task_id} onClick={() => setActiveDataset(t.task_id)} className={`p-4 rounded-2xl border transition-all cursor-pointer ${activeDataset === t.task_id ? 'bg-white border-teal-500 shadow-lg scale-[1.02]' : 'bg-[#fcfdfe] border-slate-100 hover:border-slate-300'}`}>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-black text-slate-700 truncate max-w-[120px]">{t.file_name || 'Dataset'}</span>
                        <span className={`w-2 h-2 rounded-full ${t.status === 'completed' ? 'bg-emerald-500' : 'bg-amber-400'}`} />
                      </div>
                      <p className="text-[10px] text-slate-500 uppercase font-black italic">{new Date(t.created_at).toLocaleDateString()}</p>
                    </div>
                  )) : (
                    <p className="text-xs text-slate-400 italic">No datasets processed.</p>
                  )}
                </div>
              </div>

              <div className="p-6 bg-slate-50 border-t border-slate-200">
                <button onClick={() => setActiveDataset(null)} className="w-full bg-slate-900 hover:bg-slate-800 text-white py-4 rounded-xl text-sm font-black shadow-lg transition-all active:scale-95">
                  Create New Pipeline
                </button>
              </div>
            </>
          ) : (
            <div className="flex-1 flex flex-col items-center py-10 space-y-8">
              {['M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1', 'M13 10V3L4 14h7v7l9-11h-7z', 'M12 6v6m0 0v6m0-6h6m-6 0H6'].map((ic, i) => (
                <button key={i} className="w-10 h-10 rounded-xl bg-slate-50 text-slate-400 flex items-center justify-center hover:bg-teal-50 hover:text-teal-600 transition-all">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d={ic} /></svg>
                </button>
              ))}
            </div>
          )}
        </aside>

        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Center Panel: Pipeline Canvas */}
          <main className="flex-1 bg-[#fcfdfe] relative flex flex-col overflow-hidden">
            <div className="flex items-center justify-between p-8 border-b border-slate-100 bg-white/50 backdrop-blur-sm z-20">
              <div>
                <h1 className="text-3xl font-black text-slate-800 tracking-tight">Active Canvas v1.0.4</h1>
                <p className="text-[10px] text-slate-400 font-black uppercase tracking-[0.2em] mt-1">Status: {activeTaskObj?.status === 'running' ? 'Engine Executing...' : 'Topology Valid'}</p>
              </div>
              <div className="flex items-center space-x-3">
                <div className="flex -space-x-2 mr-4">
                  {[1, 2, 3].map(i => <div key={i} className="w-8 h-8 rounded-full border-2 border-white bg-slate-200 flex items-center justify-center text-[10px] font-black uppercase">U{i}</div>)}
                </div>
                <button
                  disabled={!activeDataset || activeTaskObj?.status === 'running'}
                  className="bg-slate-950 border border-slate-900 hover:bg-slate-800 disabled:opacity-50 text-white px-8 py-3 rounded-2xl font-black text-xs shadow-xl shadow-slate-900/10 active:scale-95 transition-all flex items-center"
                >
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" /></svg>
                  Deploy Build
                </button>
              </div>
            </div>

            <div className="flex-1 relative flex overflow-hidden">
              {/* Visual Toolbar */}
              <div className="absolute left-8 top-1/2 -translate-y-1/2 flex flex-col space-y-4 z-20 bg-white border border-slate-200 p-2 rounded-2xl shadow-xl">
                {['M12 4v16m8-8H4', 'M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1', 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2'].map((ic, i) => (
                  <button key={i} className="w-10 h-10 rounded-xl hover:bg-teal-50 hover:text-teal-600 text-slate-400 flex items-center justify-center transition-all group">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d={ic} /></svg>
                  </button>
                ))}
              </div>

              {/* Grid Pattern */}
              <div className="absolute inset-0 z-0 bg-[radial-gradient(#e2e8f0_1px,transparent_1px)] bg-[size:32px_32px] pointer-events-none opacity-50" />

              {/* Pipeline Nodes */}
              <div className="flex-1 flex items-center justify-center space-x-24 relative z-10 overflow-auto py-12">
                {[
                  { label: 'Data Ingest', type: 'Source', icon: 'M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1' },
                  { label: 'Neural Filter', type: 'AI Logic', icon: 'M13 10V3L4 14h7v7l9-11h-7z' },
                  { label: 'Format Engine', type: 'Schema', icon: 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2' }
                ].map((node, i, arr) => (
                  <div key={i} className="relative transition-all duration-700">
                    <div className={`w-48 bg-white border rounded-[2.5rem] shadow-2xl p-6 group cursor-grab active:cursor-grabbing transition-all border-b-8 ${activeTaskObj?.status === 'running' && i === 1 ? 'border-teal-500 ring-4 ring-teal-500/10' : 'border-slate-200 border-b-slate-100/50 hover:border-teal-500'}`}>
                      <div className="flex justify-between items-start mb-6">
                        <div className={`w-12 h-12 rounded-2xl flex items-center justify-center shadow-inner group-hover:scale-110 transition-transform ${activeTaskObj?.status === 'running' && i === 1 ? 'bg-teal-600 text-white animate-pulse' : 'bg-teal-50 text-teal-600'}`}>
                          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d={node.icon} /></svg>
                        </div>
                        <span className="bg-slate-50 border border-slate-100 px-2 py-1 rounded-md text-[8px] font-black uppercase tracking-widest text-slate-400">Node_{i + 1}</span>
                      </div>
                      <h3 className="text-sm font-black text-slate-800 uppercase tracking-widest mb-1">{node.label}</h3>
                      <p className="text-[10px] font-bold text-teal-600 opacity-60 uppercase mb-4">{node.type}</p>
                      <div className="flex items-center space-x-2">
                        <span className={`w-1.5 h-1.5 rounded-full ${activeTaskObj?.status === 'completed' || (activeTaskObj?.status === 'running' && i < 1) ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]' : 'bg-slate-300'}`} />
                        <span className="text-[9px] font-black uppercase tracking-widest text-slate-400">{activeTaskObj?.status === 'completed' || (activeTaskObj?.status === 'running' && i < 1) ? 'Success' : 'Queued'}</span>
                      </div>
                    </div>
                    {i < arr.length - 1 && (
                      <div className="absolute top-1/2 left-full w-24 h-[2px] bg-slate-200 flex items-center justify-center">
                        <div className={`w-full h-[1px] absolute ${activeTaskObj?.status === 'running' && i === 0 ? 'bg-teal-500 animate-pulse' : 'bg-teal-500/20'}`} />
                        {activeTaskObj?.status === 'running' && i === 0 && <div className="w-2 h-2 bg-teal-500 rounded-full animate-ping shadow-lg" />}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Console / Terminal Panel */}
            <div className="h-48 bg-slate-900 border-t border-slate-800 p-6 font-mono text-[10px] flex flex-col relative z-20">
              <div className="flex items-center justify-between mb-4 border-b border-white/5 pb-2">
                <div className="flex items-center space-x-3">
                  <span className="w-2 h-2 rounded-full bg-rose-500" />
                  <span className="w-2 h-2 rounded-full bg-amber-500" />
                  <span className="w-2 h-2 rounded-full bg-emerald-500" />
                  <span className="font-bold text-white/40 uppercase tracking-widest ml-4">Live Execution logs</span>
                </div>
                <span className="text-teal-500 font-bold">STATION_ID: {activeDataset?.split('-')[0] || 'NULL'}</span>
              </div>
              <div className="flex-1 overflow-y-auto space-y-1 text-slate-400 no-scrollbar pb-10">
                <p><span className="text-teal-500/50">[{new Date().toLocaleTimeString()}]</span> <span className="text-white font-bold text-[11px]">&gt; System initialized. Awaiting source ingestion...</span></p>
                {logHistory.map((log, i) => (
                  <p key={i}><span className="text-teal-400">&gt; {log}</span></p>
                ))}
                <div ref={logEndRef} /> {/* Ref for scrolling to the bottom */}
              </div>
            </div>
          </main>
        </div>

        {/* Right Panel: Analytics & Preview */}
        <section className="w-[540px] bg-white border-l border-slate-200 flex flex-col flex-shrink-0 animate-fade-in shadow-[-1px_0_10px_rgba(0,0,0,0.02)] relative z-30">
          <div className="h-full overflow-y-auto no-scrollbar">
            {!activeDataset ? (
              <div className="p-10">
                <FileUpload onTaskCreated={handleTaskCreated} />
                <div className="mt-12 p-8 bg-slate-900 border border-slate-800 rounded-[3rem] text-white overflow-hidden relative group">
                  <div className="absolute top-0 right-0 w-40 h-40 bg-teal-500/10 blur-3xl rounded-full group-hover:scale-150 transition-all duration-1000" />
                  <h4 className="text-teal-500 font-black uppercase tracking-[0.2em] text-[10px] mb-4">Implementation Notes</h4>
                  <p className="text-sm font-medium text-slate-300 leading-relaxed mb-8">Data Cleaner Pro utilizes iterative imputers and isolation forests to ensure your production pipelines are error-free.</p>
                  <div className="flex items-center space-x-4 opacity-50 grayscale hover:grayscale-0 hover:opacity-100 transition-all">
                    <div className="w-10 h-10 bg-white/5 rounded-xl border border-white/10 flex items-center justify-center font-black text-xs">PANDA</div>
                    <div className="w-10 h-10 bg-white/5 rounded-xl border border-white/10 flex items-center justify-center font-black text-xs">NUMPY</div>
                    <div className="w-10 h-10 bg-white/5 rounded-xl border border-white/10 flex items-center justify-center font-black text-xs">SCIKIT</div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex flex-col h-full">
                <div className="p-10 border-b border-slate-100 sticky top-0 bg-white z-40">
                  <div className="flex justify-between items-center mb-2">
                    <h2 className="text-3xl font-black text-slate-800 tracking-tight">Intelligence Report</h2>
                    <button onClick={() => setActiveDataset(null)} className="w-10 h-10 bg-slate-50 border border-slate-100 rounded-2xl flex items-center justify-center text-slate-400 hover:text-rose-500 transition-all active:scale-90">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M6 18L18 6M6 6l12 12" /></svg>
                    </button>
                  </div>
                  <p className="text-[10px] text-slate-400 font-black uppercase tracking-[0.3em] ml-1">{activeTaskObj?.file_name || activeDataset.split('-')[0]}</p>
                </div>

                <div className="flex-1 p-10">
                  <TaskList tasks={tasks.filter(t => t.task_id === activeDataset)} onRefresh={fetchTasks} />
                </div>
              </div>
            )}
          </div>
        </section>

      </div>
    </div>
  );
};

export default Dashboard;
