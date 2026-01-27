import React from 'react';
import { Link, useNavigate } from 'react-router-dom';

const Navbar: React.FC = () => {
    const navigate = useNavigate();
    const token = localStorage.getItem('token');
    const userStr = localStorage.getItem('user');
    const user = userStr ? JSON.parse(userStr) : null;

    const handleLogout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        navigate('/login');
    };

    const scrollToSection = (id: string, e: React.MouseEvent) => {
        e.preventDefault();
        if (window.location.pathname !== '/') {
            navigate('/#' + id);
        } else {
            const element = document.getElementById(id);
            if (element) {
                element.scrollIntoView({ behavior: 'smooth' });
            }
        }
    };

    return (
        <nav className="fixed top-0 left-0 right-0 z-[100] bg-white border-b border-slate-200">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                    <div className="flex items-center">
                        <Link to="/" className="flex items-center space-x-2">
                            <div className="w-9 h-9 bg-teal-600 rounded-lg flex items-center justify-center shadow-sm">
                                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a2 2 0 00-1.96 1.414l-.718 2.155a2 2 0 01-3.714 0l-.718-2.155a2 2 0 00-1.96-1.414l-2.387.477a2 2 0 00-1.022.547l-1.393 1.393a2 2 0 01-3.146-2.407l.39-.39a2 2 0 00.338-2.127l-.61-1.221a2 2 0 01.328-2.127l1.393-1.393a2 2 0 00.547-1.022l.477-2.387a2 2 0 00-1.414-1.96L7.22 3.82a2 2 0 010-3.714l2.155-.718a2 2 0 001.414-1.96l.477-2.387a2 2 0 001.022-.547l1.393-1.393a2 2 0 012.407.39l.39.39a2 2 0 002.127.338l1.221-.61a2 2 0 012.127.328l1.393 1.393a2 2 0 001.022.547l2.387.477a2 2 0 001.96-1.414l.718-2.155a2 2 0 013.714 0l.718 2.155a2 2 0 001.96 1.414l2.387-.477a2 2 0 001.022-.547l1.393-1.393a2 2 0 013.146 2.407l-.39.39a2 2 0 00-.338 2.127l.61 1.221a2 2 0 01-.328 2.127l-1.393 1.393z" />
                                </svg>
                            </div>
                            <span className="text-xl font-bold text-slate-800 tracking-tight">
                                Data Cleaner <span className="text-teal-600">Pro</span>
                            </span>
                        </Link>
                    </div>

                    <div className="hidden md:flex items-center space-x-8">
                        <a href="#features" onClick={(e) => scrollToSection('features', e)} className="text-slate-600 hover:text-teal-600 px-3 py-2 text-sm font-medium transition-colors">Features</a>
                        <a href="#pricing" onClick={(e) => scrollToSection('pricing', e)} className="text-slate-600 hover:text-teal-600 px-3 py-2 text-sm font-medium transition-colors">Pricing</a>
                        {token ? (
                            <>
                                <Link to="/dashboard" className="text-slate-600 hover:text-teal-600 px-3 py-2 text-sm font-medium transition-colors">Dashboard</Link>
                                {user?.role === 'admin' && (
                                    <Link to="/admin" className="text-slate-600 hover:text-amber-500 px-3 py-2 text-sm font-medium transition-colors">Admin</Link>
                                )}
                                <div className="h-6 w-[1px] bg-slate-200" />
                                <div className="relative group">
                                    <button className="flex items-center space-x-3 hover:bg-slate-50 px-2 py-1 rounded-lg transition-all">
                                        <div className="w-8 h-8 bg-teal-100 text-teal-700 rounded-full flex items-center justify-center text-sm font-bold border border-teal-200">
                                            {user?.username?.[0]?.toUpperCase()}
                                        </div>
                                        <span className="text-sm font-semibold text-slate-700">{user?.username}</span>
                                    </button>
                                    <div className="absolute right-0 mt-2 w-48 bg-white border border-slate-200 rounded-xl shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 py-1 overflow-hidden z-[110]">
                                        <Link to="/profile" className="flex items-center space-x-2 px-4 py-2 text-sm text-slate-600 hover:bg-slate-50 transition-colors">
                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>
                                            <span>Profile Settings</span>
                                        </Link>
                                        <button onClick={handleLogout} className="w-full flex items-center space-x-2 px-4 py-2 text-sm text-rose-500 hover:bg-rose-50 transition-colors text-left font-medium">
                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" /></svg>
                                            <span>Sign Out</span>
                                        </button>
                                    </div>
                                </div>
                            </>
                        ) : (
                            <div className="flex items-center space-x-4">
                                <Link to="/login" className="text-slate-600 hover:text-teal-600 text-sm font-medium">Sign In</Link>
                                <Link to="/register" className="bg-teal-600 hover:bg-teal-700 text-white px-5 py-2.5 rounded-lg text-sm font-bold shadow-md shadow-teal-600/20 transition-all transform hover:scale-[1.02] active:scale-[0.98]">
                                    Get Started Free
                                </Link>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
