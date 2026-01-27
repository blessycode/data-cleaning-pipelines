import React, { useState, useEffect } from 'react';
import { authAPI } from '../services/api';
import Navbar from './Navbar';
import Footer from './Footer';

const AdminDashboard: React.FC = () => {
    const [stats, setStats] = useState<any>(null);
    const [users, setUsers] = useState<any[]>([]);
    const [globalTasks, setGlobalTasks] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    const fetchData = async () => {
        try {
            const statsRes = await authAPI.getStats();
            const usersRes = await authAPI.listUsers();
            const tasksRes = await authAPI.listAllTasks();
            setStats(statsRes);
            setUsers(usersRes.users);
            setGlobalTasks(tasksRes.tasks);
        } catch (err) {
            console.error('Failed to fetch admin data:', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 5000);
        return () => clearInterval(interval);
    }, []);

    if (loading) return (
        <div className="min-h-screen bg-[#f5f6fa] flex items-center justify-center">
            <div className="animate-spin h-12 w-12 border-4 border-teal-500 border-t-transparent rounded-full" />
        </div>
    );

    return (
        <div className="min-h-screen bg-[#f5f6fa] flex flex-col text-slate-800">
            <Navbar />
            <main className="flex-1 max-w-7xl mx-auto w-full px-6 pt-32 pb-24">
                <div className="mb-14">
                    <h1 className="text-5xl font-black tracking-tight mb-3">Admin Console</h1>
                    <p className="text-slate-500 font-medium">Enterprise overview of system architecture and user traffic</p>
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
                    {[
                        { label: 'Total Nodes', val: stats?.total_users || 0, color: 'teal', icon: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197' },
                        { label: 'Active Flows', val: stats?.active_pipelines || 0, color: 'emerald', icon: 'M13 10V3L4 14h7v7l9-11h-7z' },
                        { label: 'Managed Jobs', val: stats?.total_tasks || 0, color: 'indigo', icon: 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2' },
                        { label: 'Success Rate', val: `${stats?.status_distribution?.completed ? Math.round((stats.status_distribution.completed / stats.total_tasks) * 100) : 100}%`, color: 'amber', icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0' }
                    ].map((s, i) => (
                        <div key={i} className="bg-white border border-slate-200 p-8 rounded-[2.5rem] shadow-sm relative overflow-hidden group hover:shadow-xl transition-all duration-500">
                            <div className={`absolute -right-4 -top-4 w-24 h-24 bg-${s.color}-500/5 blur-2xl rounded-full transition-all group-hover:scale-150`} />
                            <div className="flex items-center space-x-3 mb-4">
                                <svg className={`w-5 h-5 text-${s.color}-600`} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d={s.icon} /></svg>
                                <p className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">{s.label}</p>
                            </div>
                            <h3 className="text-4xl font-black tracking-tighter">{s.val}</h3>
                        </div>
                    ))}
                </div>

                <div className="grid grid-cols-1 gap-12">
                    {/* Users Table */}
                    <div className="bg-white border border-slate-200 rounded-[3rem] overflow-hidden shadow-sm">
                        <div className="p-10 border-b border-slate-100 flex justify-between items-center">
                            <h2 className="text-xl font-black tracking-tight uppercase tracking-widest text-xs">Node Directory</h2>
                        </div>
                        <div className="overflow-x-auto">
                            <table className="w-full text-left">
                                <thead>
                                    <tr className="bg-slate-50">
                                        <th className="px-10 py-6 text-[10px] font-black text-slate-400 uppercase tracking-widest">Subscriber</th>
                                        <th className="px-10 py-6 text-[10px] font-black text-slate-400 uppercase tracking-widest">Authorization</th>
                                        <th className="px-10 py-6 text-[10px] font-black text-slate-400 uppercase tracking-widest">Flow Plan</th>
                                        <th className="px-10 py-6 text-[10px] font-black text-slate-400 uppercase tracking-widest">Ingestion Date</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-50 font-bold">
                                    {users.map((u, i) => (
                                        <tr key={i} className="hover:bg-[#fcfdfe] transition-colors group">
                                            <td className="px-10 py-7">
                                                <div className="flex items-center space-x-4">
                                                    <div className="w-10 h-10 rounded-xl bg-slate-100 flex items-center justify-center text-xs font-black text-slate-400 border border-slate-200 uppercase group-hover:bg-teal-600 group-hover:text-white group-hover:border-transparent transition-all">
                                                        {u.username[0]}
                                                    </div>
                                                    <div>
                                                        <p className="text-base text-slate-800 tracking-tight">{u.username}</p>
                                                        <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest">{u.email}</p>
                                                    </div>
                                                </div>
                                            </td>
                                            <td className="px-10 py-7">
                                                <span className={`px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest border ${u.role === 'admin' ? 'border-amber-200 text-amber-600 bg-amber-50' : 'border-slate-200 text-slate-500 bg-slate-50'}`}>
                                                    {u.role}
                                                </span>
                                            </td>
                                            <td className="px-10 py-7">
                                                <span className={`px-3 py-1 rounded-lg text-[9px] font-black uppercase tracking-widest border border-teal-100 text-teal-600 bg-teal-50`}>
                                                    {u.plan || 'Free'}
                                                </span>
                                            </td>
                                            <td className="px-10 py-7 text-sm text-slate-500">{new Date(u.created_at).toLocaleDateString()}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    {/* Global Flow Table */}
                    <div className="bg-white border border-slate-200 rounded-[3rem] overflow-hidden shadow-sm">
                        <div className="p-10 border-b border-slate-100 flex justify-between items-center">
                            <h2 className="text-xl font-black tracking-tight uppercase tracking-widest text-xs">Global Flow Monitor</h2>
                            <span className="bg-teal-50 text-teal-600 px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-widest">Live Updates</span>
                        </div>
                        <div className="overflow-x-auto">
                            <table className="w-full text-left">
                                <thead>
                                    <tr className="bg-slate-50">
                                        <th className="px-10 py-6 text-[10px] font-black text-slate-400 uppercase tracking-widest">Source Node</th>
                                        <th className="px-10 py-6 text-[10px] font-black text-slate-400 uppercase tracking-widest">Pipeline Asset</th>
                                        <th className="px-10 py-6 text-[10px] font-black text-slate-400 uppercase tracking-widest">Current Instruction</th>
                                        <th className="px-10 py-6 text-[10px] font-black text-slate-400 uppercase tracking-widest text-right">Progress</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-50">
                                    {globalTasks.map((t, i) => (
                                        <tr key={i} className="group hover:bg-[#fcfdfe] transition-colors">
                                            <td className="px-10 py-7 text-sm font-black text-slate-800 tracking-tight">@{t.username}</td>
                                            <td className="px-10 py-7">
                                                <div className="text-xs font-bold text-slate-600">{t.file_name}</div>
                                                <div className="text-[9px] text-slate-300 font-black uppercase tracking-widest">{t.task_id.split('-')[0]}</div>
                                            </td>
                                            <td className="px-10 py-7">
                                                <div className="flex items-center space-x-3">
                                                    <span className={`w-2 h-2 rounded-full ${t.status === 'completed' ? 'bg-emerald-500' : t.status === 'failed' ? 'bg-rose-500' : 'bg-amber-400 animate-pulse'}`} />
                                                    <span className="text-xs font-bold text-slate-500">{t.message || 'Queued...'}</span>
                                                </div>
                                            </td>
                                            <td className="px-10 py-7 text-right">
                                                <div className="inline-flex flex-col items-end">
                                                    <span className="text-xs font-black text-slate-800 mb-1">{t.progress}%</span>
                                                    <div className="w-24 bg-slate-100 h-1 rounded-full overflow-hidden">
                                                        <div className="h-full bg-teal-600 transition-all duration-1000" style={{ width: `${t.progress}%` }} />
                                                    </div>
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </main>
            <Footer />
        </div>
    );
};

export default AdminDashboard;
