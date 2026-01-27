import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { authAPI } from '../services/api';
import Navbar from './Navbar';

const ForgotPassword: React.FC = () => {
    const [email, setEmail] = useState('');
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setMessage(null);

        try {
            await authAPI.forgotPassword(email);
            setMessage({ type: 'success', text: 'Instructions have been sent to your email.' });
        } catch (err: any) {
            setMessage({ type: 'error', text: 'Failed to send instructions. Please try again.' });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-[#f5f6fa] flex flex-col">
            <Navbar />

            <main className="flex-1 flex items-center justify-center p-6 py-24 relative overflow-hidden">
                <div className="w-full max-w-md relative group">
                    <div className="bg-white border border-slate-200 rounded-[2.5rem] p-10 md:p-12 shadow-[0_20px_50px_rgba(0,0,0,0.05)] text-center relative z-10 transition-all">
                        <div className="inline-flex items-center justify-center w-20 h-20 bg-teal-50 text-teal-600 rounded-[1.75rem] mb-10 shadow-inner">
                            <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" /></svg>
                        </div>

                        <h2 className="text-3xl font-black text-slate-800 tracking-tight mb-2">Reset Password</h2>
                        <p className="text-slate-500 font-medium mb-10 leading-relaxed">Enter your email for instructions</p>

                        {message ? (
                            <div className={`p-6 rounded-[1.5rem] mb-6 flex flex-col items-center space-y-4 ${message.type === 'success' ? 'bg-emerald-50 text-emerald-700 border border-emerald-100' : 'bg-rose-50 text-rose-700 border border-rose-100'}`}>
                                <p className="text-sm font-bold text-center">{message.text}</p>
                                <Link to="/login" className="text-sm font-black uppercase tracking-widest underline underline-offset-4">Return to login</Link>
                            </div>
                        ) : (
                            <form onSubmit={handleSubmit} className="space-y-8 text-left">
                                <div>
                                    <label className="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-3 ml-1">Work Email</label>
                                    <input
                                        type="email"
                                        required
                                        className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-6 py-4 text-slate-800 placeholder-slate-300 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all font-bold"
                                        placeholder="pro@data.com"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                    />
                                </div>

                                <button
                                    type="submit"
                                    disabled={loading}
                                    className="w-full bg-teal-600 hover:bg-teal-700 disabled:opacity-50 text-white py-5 rounded-[1.5rem] font-black text-lg transition-all shadow-xl shadow-teal-500/20 active:scale-[0.98] flex items-center justify-center space-x-2"
                                >
                                    {loading ? 'Processing...' : 'Send Magic Link'}
                                </button>
                            </form>
                        )}

                        <div className="mt-12 text-center pt-8 border-t border-slate-50">
                            <p className="text-slate-500 font-medium font-bold">
                                Remember it?{' '}
                                <Link to="/login" className="text-teal-600 font-black hover:text-teal-700">Login</Link>
                            </p>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
};

export default ForgotPassword;
