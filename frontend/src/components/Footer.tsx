import React from 'react';
import { Link } from 'react-router-dom';

const Footer: React.FC = () => {
    return (
        <footer className="bg-slate-900 py-20 px-4">
            <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-12 border-b border-slate-800 pb-16 mb-10">
                <div className="col-span-1 md:col-span-1">
                    <Link to="/" className="flex items-center space-x-2 mb-8">
                        <div className="w-8 h-8 bg-teal-600 rounded-lg flex items-center justify-center">
                            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477" /></svg>
                        </div>
                        <span className="text-xl font-black text-white tracking-tight">Data Cleaner <span className="text-teal-500">Pro</span></span>
                    </Link>
                    <p className="text-slate-400 text-sm leading-relaxed font-medium">Automating the world's most tedious data preprocessing tasks with state-of-the-art AI engines.</p>
                </div>

                <div>
                    <h4 className="text-white font-black uppercase tracking-widest text-[10px] mb-8">Product</h4>
                    <ul className="space-y-4 text-sm font-bold">
                        <li><Link to="/features" className="text-slate-500 hover:text-teal-400 transition-colors">Visual Pipeline</Link></li>
                        <li><Link to="/pricing" className="text-slate-500 hover:text-teal-400 transition-colors">AI Imputation</Link></li>
                        <li><Link to="/docs" className="text-slate-500 hover:text-teal-400 transition-colors">API Reference</Link></li>
                    </ul>
                </div>

                <div>
                    <h4 className="text-white font-black uppercase tracking-widest text-[10px] mb-8">Company</h4>
                    <ul className="space-y-4 text-sm font-bold">
                        <li><Link to="/about" className="text-slate-500 hover:text-teal-400 transition-colors">About</Link></li>
                        <li><Link to="/contact" className="text-slate-500 hover:text-teal-400 transition-colors">Contact</Link></li>
                        <li><Link to="/socials" className="text-slate-500 hover:text-teal-400 transition-colors">Socials</Link></li>
                    </ul>
                </div>

                <div>
                    <h4 className="text-white font-black uppercase tracking-widest text-[10px] mb-8">Legal</h4>
                    <ul className="space-y-4 text-sm font-bold">
                        <li><Link to="/terms" className="text-slate-500 hover:text-teal-400 transition-colors">Terms & Conditions</Link></li>
                        <li><Link to="/privacy" className="text-slate-500 hover:text-teal-400 transition-colors">Privacy Policy</Link></li>
                        <li><Link to="/security" className="text-slate-500 hover:text-teal-400 transition-colors">Security</Link></li>
                    </ul>
                </div>
            </div>

            <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center text-slate-600 text-[10px] font-black uppercase tracking-widest">
                <p>© 2026 Data Cleaner Pro. Built in SF.</p>
                <div className="flex space-x-8 mt-4 md:mt-0">
                    <a href="#" className="hover:text-white transition-colors">Twitter</a>
                    <a href="#" className="hover:text-white transition-colors">Github</a>
                    <a href="#" className="hover:text-white transition-colors">LinkedIn</a>
                </div>
            </div>
        </footer>
    );
};

export default Footer;
