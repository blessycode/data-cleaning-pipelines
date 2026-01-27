import React, { useState, useEffect } from 'react';
import { authAPI } from '../services/api';
import Navbar from './Navbar';
import Footer from './Footer';

const Profile: React.FC = () => {
    const [user, setUser] = useState<any>(null);
    const [formData, setFormData] = useState({
        current_password: '',
        new_password: '',
        confirm_new_password: '',
    });
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

    useEffect(() => {
        const fetchUser = async () => {
            try {
                const res = await authAPI.getCurrentUser();
                setUser(res);
            } catch (err) {
                console.error('Failed to fetch user:', err);
            }
        };
        fetchUser();
    }, []);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setMessage(null);

        if (formData.new_password !== formData.confirm_new_password) {
            setMessage({ type: 'error', text: 'New passwords do not match' });
            setLoading(false);
            return;
        }

        try {
            await authAPI.changePassword(formData);
            setMessage({ type: 'success', text: 'Password updated successfully!' });
            setFormData({ current_password: '', new_password: '', confirm_new_password: '' });
        } catch (err: any) {
            setMessage({ type: 'error', text: err.response?.data?.detail || 'Update failed.' });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-[#f5f6fa] flex flex-col">
            <Navbar />
            <main className="flex-1 max-w-4xl mx-auto w-full px-6 pt-32 pb-24">
                <div className="flex items-center space-x-6 mb-12">
                    <div className="w-20 h-20 bg-teal-600 rounded-[2rem] flex items-center justify-center text-white text-3xl font-black shadow-xl shadow-teal-500/20 uppercase">
                        {user?.username?.[0] || 'U'}
                    </div>
                    <div>
                        <h1 className="text-5xl font-black text-slate-800 tracking-tight">{user?.username || 'Loading...'}</h1>
                        <p className="text-slate-500 font-bold uppercase tracking-widest text-xs mt-1">{user?.email || 'Authenticated User'}</p>
                    </div>
                </div>

                <div className="bg-white border border-slate-200 rounded-[3.5rem] overflow-hidden shadow-sm transition-all hover:shadow-xl">
                    <div className="p-10 md:p-16">

                        {/* Subscription Summary */}
                        <div className="mb-16">
                            <div className="p-8 bg-slate-900 border border-slate-800 rounded-[2.5rem] text-white flex flex-col md:flex-row justify-between items-center relative overflow-hidden mb-6">
                                <div className="absolute top-0 right-0 w-40 h-40 bg-teal-500/10 blur-3xl rounded-full" />
                                <div className="relative z-10 mb-6 md:mb-0">
                                    <p className="text-[10px] font-black text-teal-500 uppercase tracking-[0.3em] mb-2">Active Implementation</p>
                                    <h3 className="text-3xl font-black tracking-tight">{user?.plan?.toUpperCase() || 'FREE'} PLAN</h3>
                                    <p className="text-slate-400 text-sm font-medium mt-1">Renewal Date: March 12, 2026</p>
                                </div>
                                <div className="relative z-10 bg-white/5 border border-white/10 px-6 py-4 rounded-3xl flex items-center space-x-4">
                                    <span className="text-xs font-black uppercase tracking-widest text-teal-400">Total Credits Used:</span>
                                    <span className="text-xl font-black">1.2GB <span className="text-white/30">/ 5GB</span></span>
                                </div>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                {['Free', 'Professional', 'Enterprise'].map((p) => (
                                    <button
                                        key={p}
                                        className={`p-6 rounded-3xl border text-left transition-all ${user?.plan?.toLowerCase() === p.toLowerCase() ? 'bg-teal-50 border-teal-500' : 'bg-white border-slate-100 hover:border-teal-200'}`}
                                        onClick={() => alert(`Switching to ${p} implementation...`)}
                                    >
                                        <p className="text-[9px] font-black uppercase tracking-widest text-slate-400 mb-1">{p === 'Enterprise' ? 'Negotiable' : p === 'Professional' ? '$49/mo' : '$0/mo'}</p>
                                        <h4 className="text-sm font-black text-slate-800">{p} Node</h4>
                                    </button>
                                ))}
                            </div>
                        </div>

                        <form onSubmit={handleSubmit} className="max-w-2xl space-y-10">
                            <div>
                                <h2 className="text-xl font-black text-slate-800 mb-8 uppercase tracking-widest text-xs border-l-4 border-teal-500 pl-4">Authentication Update</h2>

                                {message && (
                                    <div className={`p-5 rounded-3xl mb-10 flex items-center space-x-4 animate-fade-in ${message.type === 'success' ? 'bg-emerald-50 text-emerald-700 border border-emerald-100 font-bold' : 'bg-rose-50 text-rose-700 border border-rose-100 font-bold'}`}>
                                        <svg className="w-6 h-6 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d={message.type === 'success' ? "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" : "M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"} /></svg>
                                        <span>{message.text}</span>
                                    </div>
                                )}

                                <div className="space-y-6">
                                    <div className="group">
                                        <label className="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-3 ml-1 group-focus-within:text-teal-600 transition-colors">Current Security Key</label>
                                        <input
                                            type="password"
                                            name="current_password"
                                            value={formData.current_password}
                                            onChange={handleChange}
                                            className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-6 py-4 text-slate-800 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all font-bold"
                                            required
                                        />
                                    </div>

                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        <div className="group">
                                            <label className="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-3 ml-1 group-focus-within:text-teal-600 transition-colors">New Password</label>
                                            <input
                                                type="password"
                                                name="new_password"
                                                value={formData.new_password}
                                                onChange={handleChange}
                                                className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-6 py-4 text-slate-800 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all font-bold"
                                                required
                                                minLength={8}
                                            />
                                        </div>
                                        <div className="group">
                                            <label className="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-3 ml-1 group-focus-within:text-teal-600 transition-colors">Verify Password</label>
                                            <input
                                                type="password"
                                                name="confirm_new_password"
                                                value={formData.confirm_new_password}
                                                onChange={handleChange}
                                                className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-6 py-4 text-slate-800 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all font-bold"
                                                required
                                            />
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="pt-6">
                                <button
                                    type="submit"
                                    disabled={loading}
                                    className="bg-teal-600 hover:bg-teal-700 disabled:opacity-50 text-white px-10 py-5 rounded-[1.75rem] font-black text-lg transition-all shadow-xl shadow-teal-500/30 flex items-center justify-center space-x-3 active:scale-[0.98]"
                                >
                                    {loading ? (
                                        <>
                                            <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                                            <span>Processing...</span>
                                        </>
                                    ) : (
                                        <span>Commit Password Change</span>
                                    )}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </main>
            <Footer />
        </div>
    );
};

export default Profile;
