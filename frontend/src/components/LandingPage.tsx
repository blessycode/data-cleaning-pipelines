import React, { useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import Navbar from './Navbar';
import Footer from './Footer';

const LandingPage: React.FC = () => {
    const { hash } = useLocation();

    useEffect(() => {
        if (hash) {
            const id = hash.replace('#', '');
            const element = document.getElementById(id);
            if (element) {
                setTimeout(() => {
                    element.scrollIntoView({ behavior: 'smooth' });
                }, 100);
            }
        }
    }, [hash]);

    return (
        <div className="min-h-screen bg-[#f5f6fa]">
            <Navbar />

            {/* Hero Section */}
            <section className="pt-40 pb-24 px-4 overflow-hidden relative">
                <div className="max-w-7xl mx-auto flex flex-col items-center relative z-10 text-center">
                    <div className="inline-flex items-center space-x-2 bg-teal-50 border border-teal-100 px-4 py-2 rounded-full mb-10 group cursor-default">
                        <span className="flex h-2 w-2 rounded-full bg-teal-500 animate-ping group-hover:animate-none" />
                        <p className="text-sm font-bold text-teal-700 tracking-wider uppercase">v2.0 Now Live</p>
                    </div>

                    <h1 className="text-6xl md:text-[5.5rem] font-black text-slate-800 leading-[1.05] tracking-tight mb-8">
                        Clean, Profile, and Transform <br />
                        <span className="text-teal-600">Your Data Effortlessly</span>
                    </h1>

                    <p className="max-w-2xl text-xl text-slate-500 mb-12 leading-relaxed">
                        The professional edge for data scientists. Automate normalization, detect outliers, and generate high-fidelity reports with our AI-powered visual workflow.
                    </p>

                    <div className="flex flex-col sm:flex-row items-center space-y-4 sm:space-y-0 sm:space-x-6">
                        <Link to="/register" className="w-full sm:w-auto bg-teal-600 hover:bg-teal-700 text-white px-10 py-5 rounded-2xl text-lg font-black transition-all shadow-xl shadow-teal-500/20 active:scale-95 flex items-center justify-center group">
                            <span>Get Started Free</span>
                            <svg className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M13 7l5 5m0 0l-5 5m5-5H6" /></svg>
                        </Link>
                        <Link to="/login" className="w-full sm:w-auto bg-white border border-slate-200 hover:border-teal-500 hover:text-teal-600 text-slate-600 px-10 py-5 rounded-2xl text-lg font-black transition-all active:scale-95">
                            View Live Demo
                        </Link>
                    </div>

                    {/* Hero Image / Illustration Placeholder */}
                    <div className="mt-24 w-full max-w-5xl rounded-[2.5rem] bg-white p-4 shadow-2xl border border-slate-100 relative group">
                        <div className="absolute -inset-1 bg-gradient-to-r from-teal-500 to-indigo-500 rounded-[2.5rem] blur opacity-10 group-hover:opacity-20 transition-all duration-1000" />
                        <div className="relative overflow-hidden rounded-[1.5rem] border border-slate-100 aspect-[16/9] bg-slate-50 flex items-center justify-center">
                            <div className="flex items-center space-x-12 opacity-40">
                                <div className="w-24 h-24 rounded-2xl bg-teal-100 flex items-center justify-center"><svg className="w-10 h-10 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" /></svg></div>
                                <div className="w-16 h-1 bg-slate-300 rounded-full" />
                                <div className="w-24 h-24 rounded-2xl bg-indigo-100 flex items-center justify-center"><svg className="w-10 h-10 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg></div>
                                <div className="w-16 h-1 bg-slate-300 rounded-full" />
                                <div className="w-24 h-24 rounded-2xl bg-emerald-100 flex items-center justify-center"><svg className="w-10 h-10 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg></div>
                            </div>
                            <div className="absolute inset-0 bg-gradient-to-t from-white/80 via-transparent text-slate-400 flex flex-col items-center justify-end pb-12 font-bold tracking-widest uppercase text-sm">
                                Interactive Pipeline Canvas
                            </div>
                        </div>
                    </div>
                </div>

                {/* Background decorations */}
                <div className="absolute top-0 right-0 w-[800px] h-[800px] bg-teal-500/5 blur-[120px] rounded-full -mr-96 -mt-96 pointer-events-none" />
                <div className="absolute bottom-0 left-0 w-[600px] h-[600px] bg-indigo-500/5 blur-[100px] rounded-full -ml-40 -mb-40 pointer-events-none" />
            </section>

            {/* Features Section */}
            <section id="features" className="py-32 px-4 bg-white border-y border-slate-100">
                <div className="max-w-7xl mx-auto">
                    <div className="text-center mb-20">
                        <h2 className="text-4xl font-black text-slate-800 mb-6 tracking-tight">Standardize Your Entire Stack</h2>
                        <p className="max-w-xl mx-auto text-slate-500 text-lg">One platform to ingestion, sanitize, and validate every dataset in your organization.</p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                        {[
                            {
                                title: 'Deep Ingestion',
                                desc: 'Native support for Excel, Parquet, and live SQL database connections.',
                                color: 'teal',
                                icon: 'M8 7v8a2 2 0 002 2h6M8 7V5a2 2 0 012-2h4.586a1 1 0 01.707.293l4.414 4.414a1 1 0 01.293.707V15a2 2 0 01-2 2h-2'
                            },
                            {
                                title: 'AI Imputation',
                                desc: 'Predict and fill missing values using iterative machine learning models.',
                                color: 'indigo',
                                icon: 'M13 10V3L4 14h7v7l9-11h-7z'
                            },
                            {
                                title: 'Pro Profiling',
                                desc: 'High-density metrics on skewness, kurtosis, and correlation matrices.',
                                color: 'emerald',
                                icon: 'M16 8v8m-4-5v5m-4-2v2M4 21h16a2 2 0 002-2V5a2 2 0 00-2-2H4a2 2 0 00-2 2v14a2 2 0 002 2z'
                            },
                            {
                                title: 'Visual Pipelines',
                                desc: 'Drag-and-drop cleaning nodes to create repeatable data flows.',
                                color: 'rose',
                                icon: 'M11 4a2 2 0 114 0v1a2 2 0 01-2 2 2 2 0 01-2-2V4zm-2 9a2 2 0 100 4h5a2 2 0 100-4h-5z'
                            }
                        ].map((f, i) => (
                            <div key={i} className="group p-8 bg-[#f8fafc] border border-slate-100 rounded-[2rem] hover:bg-white hover:shadow-2xl hover:border-transparent transition-all duration-500">
                                <div className={`w-14 h-14 bg-${f.color}-50 text-${f.color}-600 rounded-2xl flex items-center justify-center mb-8 group-hover:scale-110 group-hover:rotate-3 transition-transform duration-500`}>
                                    <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.3" d={f.icon} /></svg>
                                </div>
                                <h3 className="text-xl font-black text-slate-800 mb-4 tracking-tight">{f.title}</h3>
                                <p className="text-slate-500 text-sm leading-relaxed">{f.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Pricing Section */}
            <section id="pricing" className="py-32 px-4 bg-white border-y border-slate-100">
                <div className="max-w-7xl mx-auto">
                    <div className="text-center mb-20">
                        <h2 className="text-4xl font-black text-slate-800 mb-6 tracking-tight">Flexible Plans for Every Team</h2>
                        <p className="max-w-xl mx-auto text-slate-500 text-lg">Start free and scale as your data complexity grows.</p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
                        {[
                            {
                                name: 'Free',
                                price: '$0',
                                features: ['Basic Cleaning', 'CSV Export', '5 Datasets / month', 'Community Support'],
                                cta: 'Start for Free',
                                highlight: false
                            },
                            {
                                name: 'Professional',
                                price: '$49',
                                features: ['AI Imputation', 'Excel & Parquet Export', 'Unlimited Datasets', 'Interactive Dashboards', 'Email Support'],
                                cta: 'Go Pro Now',
                                highlight: true
                            },
                            {
                                name: 'Enterprise',
                                price: 'Custom',
                                features: ['SQL Database Connectors', 'API Access', 'Admin Monitoring', 'SLA Guarantee', 'Dedicated Manager'],
                                cta: 'Contact Sales',
                                highlight: false
                            }
                        ].map((plan, i) => (
                            <div key={i} className={`p-10 rounded-[3rem] border transition-all duration-500 flex flex-col ${plan.highlight ? 'bg-slate-900 border-slate-900 shadow-[0_30px_60px_rgba(13,148,136,0.2)] scale-105 relative z-10' : 'bg-slate-50 border-slate-100 hover:bg-white hover:border-teal-500/30'}`}>
                                {plan.highlight && (
                                    <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-teal-500 text-white px-4 py-1 rounded-full text-[10px] font-black uppercase tracking-[0.2em] shadow-lg">Most Popular</div>
                                )}
                                <div className="mb-8">
                                    <h3 className={`text-xs font-black uppercase tracking-[0.2em] mb-4 ${plan.highlight ? 'text-teal-400' : 'text-slate-400'}`}>{plan.name}</h3>
                                    <div className="flex items-baseline space-x-1">
                                        <span className={`text-4xl font-black ${plan.highlight ? 'text-white' : 'text-slate-800'}`}>{plan.price}</span>
                                        {plan.price !== 'Custom' && <span className={`text-sm font-bold ${plan.highlight ? 'text-slate-500' : 'text-slate-400'}`}>/month</span>}
                                    </div>
                                </div>

                                <ul className="space-y-4 mb-12 flex-1">
                                    {plan.features.map((feat, fi) => (
                                        <li key={fi} className="flex items-start space-x-3 group">
                                            <svg className={`w-5 h-5 flex-shrink-0 mt-0.5 ${plan.highlight ? 'text-teal-500' : 'text-teal-600'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7" /></svg>
                                            <span className={`text-sm font-medium ${plan.highlight ? 'text-slate-300' : 'text-slate-600'}`}>{feat}</span>
                                        </li>
                                    ))}
                                </ul>

                                <Link
                                    to={plan.name === 'Enterprise' ? '/contact' : '/register'}
                                    className={`w-full py-4 rounded-[1.5rem] text-sm font-black uppercase tracking-widest text-center transition-all ${plan.highlight ? 'bg-teal-600 text-white hover:bg-teal-500' : 'bg-white border border-slate-200 text-slate-700 hover:border-teal-500 hover:text-teal-600'}`}
                                >
                                    {plan.cta}
                                </Link>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="py-24 px-4 bg-[#f5f6fa]">
                <div className="max-w-5xl mx-auto rounded-[3rem] bg-slate-900 px-8 py-16 md:p-20 relative overflow-hidden text-center md:text-left">
                    <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-teal-500/10 blur-[100px] rounded-full -mr-40 -mt-40 pointer-events-none" />
                    <div className="relative z-10 grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
                        <div>
                            <h2 className="text-4xl md:text-5xl font-black text-white mb-6 leading-tight">Ready to clean <br /> like a pro?</h2>
                            <p className="text-slate-400 text-lg mb-0 font-medium">Join 50k+ developers automating their data prep workflows.</p>
                        </div>
                        <div className="flex flex-col space-y-4">
                            <Link to="/register" className="bg-teal-600 hover:bg-teal-500 text-white px-8 py-5 rounded-2xl text-xl font-black transition-all shadow-2xl shadow-teal-600/30">
                                Create Free Account
                            </Link>
                            <p className="text-slate-500 text-xs text-center font-bold tracking-widest uppercase">No credit card required</p>
                        </div>
                    </div>
                </div>
            </section>

            <Footer />
        </div>
    );
};

export default LandingPage;
