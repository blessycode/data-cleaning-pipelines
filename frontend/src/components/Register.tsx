import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authAPI } from '../services/api';
import Navbar from './Navbar';

const Register: React.FC = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirm_password: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.confirm_password) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);
    try {
      await authAPI.register(formData);
      navigate('/login');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed. Try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#f5f6fa] flex flex-col">
      <Navbar />

      <main className="flex-1 flex items-center justify-center p-6 py-24 relative overflow-hidden">
        <div className="absolute top-0 left-0 w-[500px] h-[500px] bg-teal-500/5 blur-[120px] rounded-full -ml-40 -mt-40 pointer-events-none" />

        <div className="w-full max-w-xl relative group">
          <div className="bg-white border border-slate-200 rounded-[3rem] p-10 md:p-14 shadow-[0_32px_64px_rgba(0,0,0,0.04)] relative z-10">
            <div className="text-center mb-12">
              <div className="inline-flex items-center justify-center w-20 h-20 bg-indigo-50 text-indigo-600 rounded-[1.75rem] mb-8 shadow-inner">
                <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" /></svg>
              </div>
              <h2 className="text-4xl font-black text-slate-800 tracking-tight mb-2">Create Account</h2>
              <p className="text-slate-500 font-medium">Join the professional data cleaning standard</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-8">
              {error && (
                <div className="p-4 bg-rose-50 border border-rose-100 rounded-2xl text-rose-600 text-sm font-bold flex items-center space-x-3">
                  <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                  <span>{error}</span>
                </div>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-xs font-black text-slate-400 uppercase tracking-widest mb-3 ml-1">Username</label>
                  <input
                    name="username"
                    type="text"
                    required
                    className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-6 py-4 text-slate-800 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all font-bold"
                    placeholder="data_wizard"
                    value={formData.username}
                    onChange={handleInputChange}
                  />
                </div>
                <div>
                  <label className="block text-xs font-black text-slate-400 uppercase tracking-widest mb-3 ml-1">Email</label>
                  <input
                    name="email"
                    type="email"
                    required
                    className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-6 py-4 text-slate-800 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all font-bold"
                    placeholder="pro@data.com"
                    value={formData.email}
                    onChange={handleInputChange}
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-xs font-black text-slate-400 uppercase tracking-widest mb-3 ml-1">Password</label>
                  <input
                    name="password"
                    type="password"
                    required
                    minLength={8}
                    className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-6 py-4 text-slate-800 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all font-bold"
                    placeholder="••••••••"
                    value={formData.password}
                    onChange={handleInputChange}
                  />
                </div>
                <div>
                  <label className="block text-xs font-black text-slate-400 uppercase tracking-widest mb-3 ml-1">Confirm</label>
                  <input
                    name="confirm_password"
                    type="password"
                    required
                    className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-6 py-4 text-slate-800 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all font-bold"
                    placeholder="••••••••"
                    value={formData.confirm_password}
                    onChange={handleInputChange}
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-slate-900 hover:bg-slate-800 disabled:opacity-50 text-white py-5 rounded-[1.75rem] font-black text-lg transition-all shadow-xl shadow-slate-900/10 active:scale-[0.98] flex items-center justify-center space-x-2"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                    <span>Processing...</span>
                  </>
                ) : (
                  <span>Create Account</span>
                )}
              </button>
            </form>

            <div className="mt-12 text-center pt-8 border-t border-slate-50 font-medium text-slate-500">
              Already have an account?{' '}
              <Link to="/login" className="text-teal-600 font-black hover:underline underline-offset-4">Sign In</Link>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Register;
