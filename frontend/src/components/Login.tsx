import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authAPI } from '../services/api';
import Navbar from './Navbar';

const Login: React.FC = () => {
  const [formData, setFormData] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = await authAPI.login(formData);
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('user', JSON.stringify({ username: data.username, role: data.role }));
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid username or password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#f5f6fa] flex flex-col">
      <Navbar />

      <main className="flex-1 flex items-center justify-center p-6 py-24 relative overflow-hidden">
        {/* Background blurs */}
        <div className="absolute top-1/4 right-0 w-[400px] h-[400px] bg-teal-500/5 blur-[80px] rounded-full pointer-events-none" />
        <div className="absolute bottom-1/4 left-0 w-[400px] h-[400px] bg-indigo-500/5 blur-[80px] rounded-full pointer-events-none" />

        <div className="w-full max-w-md relative group">
          <div className="bg-white border border-slate-200 rounded-[2.5rem] p-10 md:p-12 shadow-[0_20px_50px_rgba(0,0,0,0.05)] text-center relative z-10 transition-all group-hover:shadow-[0_32px_64px_rgba(0,0,0,0.08)]">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-teal-50 text-teal-600 rounded-[1.75rem] mb-10 shadow-inner">
              <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M12 11c0 3.517-1.009 6.799-2.753 9.571m-3.44-4.514A9.01 9.01 0 0012 21a9.003 9.003 0 0012-21 9.003 9.003 0 00-12 21z" /></svg>
            </div>

            <h2 className="text-3xl font-black text-slate-800 tracking-tight mb-2">Welcome Back</h2>
            <p className="text-slate-500 font-medium mb-10 leading-relaxed">Sign in to manage your data pipelines</p>

            <form onSubmit={handleSubmit} className="space-y-6 text-left">
              {error && (
                <div className="p-4 bg-rose-50 border border-rose-100 rounded-2xl text-rose-600 text-sm font-bold flex items-center space-x-3 transition-opacity">
                  <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                  <span>{error}</span>
                </div>
              )}

              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-black text-slate-400 uppercase tracking-widest mb-2 ml-1">Username</label>
                  <input
                    type="text"
                    required
                    className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-6 py-4 text-slate-800 placeholder-slate-300 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all font-bold"
                    placeholder="Enter username"
                    value={formData.username}
                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  />
                </div>
                <div>
                  <div className="flex justify-between items-center mb-2 ml-1">
                    <label className="block text-xs font-black text-slate-400 uppercase tracking-widest">Password</label>
                    <Link to="/forgot-password" title="Reset Password" className="text-xs font-bold text-teal-600 hover:text-teal-500 underline decoration-teal-500/30">Reset?</Link>
                  </div>
                  <input
                    type="password"
                    required
                    className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-6 py-4 text-slate-800 placeholder-slate-300 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all font-bold"
                    placeholder="••••••••"
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-teal-600 hover:bg-teal-700 disabled:opacity-50 text-white py-5 rounded-[1.5rem] font-black text-lg transition-all shadow-xl shadow-teal-500/20 active:scale-[0.98] flex items-center justify-center space-x-2"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                    <span>Verifying...</span>
                  </>
                ) : (
                  <span>Sign In</span>
                )}
              </button>
            </form>

            <div className="mt-12 text-center pt-8 border-t border-slate-50">
              <p className="text-slate-500 font-medium">
                New to Pro?{' '}
                <Link to="/register" className="text-teal-600 font-black hover:text-teal-700 transition-colors">Start for free</Link>
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Login;
