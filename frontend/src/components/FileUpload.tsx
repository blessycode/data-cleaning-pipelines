import React, { useState } from 'react';
import { taskAPI } from '../services/api';

interface FileUploadProps {
  onTaskCreated: (taskId: string) => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onTaskCreated }) => {
  const [file, setFile] = useState<File | null>(null);
  const [options, setOptions] = useState({
    file_type: 'csv',
    profile_data: true,
    include_visuals: true,
    apply_cleaning: true,
    enable_feature_suggestions: true,
    validate_final_data: true,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      const ext = e.target.files[0].name.split('.').pop()?.toLowerCase();
      if (ext === 'csv') setOptions({ ...options, file_type: 'csv' });
      else if (['xlsx', 'xls'].includes(ext || '')) setOptions({ ...options, file_type: 'excel' });
      else if (ext === 'parquet') setOptions({ ...options, file_type: 'parquet' });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError('Select target file first.');
      return;
    }

    setError('');
    setLoading(true);

    try {
      const result = await taskAPI.runPipeline(file, options);
      onTaskCreated(result.task_id);
      setFile(null);
      const fileInput = document.getElementById('file-input') as HTMLInputElement;
      if (fileInput) fileInput.value = '';
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Pipeline initialization failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white border border-slate-200 rounded-[3rem] p-6 shadow-sm">
      <form onSubmit={handleSubmit} className="space-y-10">
        <div className="relative group">
          <input
            id="file-input"
            type="file"
            accept=".csv,.xlsx,.xls,.parquet"
            onChange={handleFileChange}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
          />
          <div className={`p-12 border-2 border-dashed rounded-[2.5rem] text-center transition-all duration-500 ${file ? 'border-teal-500 bg-teal-50/20' : 'border-slate-100 group-hover:border-teal-200 bg-[#fcfdfe]'}`}>
            <div className={`w-20 h-20 rounded-[2rem] flex items-center justify-center mx-auto mb-6 shadow-sm border transition-all duration-500 ${file ? 'bg-teal-600 text-white border-transparent' : 'bg-white text-slate-300 border-slate-100 group-hover:scale-110'}`}>
              <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" /></svg>
            </div>
            <p className="text-base font-black text-slate-800 leading-tight mb-2">{file ? file.name : 'Select Ingestion Path'}</p>
            <p className="text-[10px] text-slate-400 font-black uppercase tracking-widest leading-none">Drop target file or click to browse</p>
          </div>
        </div>

        <div className="space-y-6">
          <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] px-1 border-l-4 border-teal-500 ml-2">Neural Engine Flags</h4>
          <div className="grid grid-cols-1 gap-4">
            {[
              { id: 'profile_data', label: 'Matrix Profiling', desc: 'Deep statistical analysis' },
              { id: 'apply_cleaning', label: 'Imputation Logic', desc: 'Auto-fix missing fragments' },
              { id: 'include_visuals', label: 'Vision Exports', desc: 'Interactive plots & maps' },
              { id: 'enable_feature_suggestions', label: 'AI Suggests', desc: 'Predictive attribute help' }
            ].map(opt => (
              <label key={opt.id} className="flex items-center justify-between p-4 bg-slate-50 border border-slate-100 rounded-2xl group cursor-pointer hover:bg-white hover:border-teal-200 transition-all">
                <div className="flex flex-col">
                  <span className="text-xs font-black text-slate-800 uppercase tracking-widest transition-colors">{opt.label}</span>
                  <span className="text-[9px] text-slate-400 font-bold uppercase mt-1">{opt.desc}</span>
                </div>
                <input
                  type="checkbox"
                  checked={(options as any)[opt.id]}
                  onChange={(e) => setOptions({ ...options, [opt.id]: e.target.checked })}
                  className="w-6 h-6 rounded-lg text-teal-600 bg-white border-slate-200 focus:ring-teal-500 transition-all cursor-pointer"
                />
              </label>
            ))}
          </div>
        </div>

        {error && (
          <div className="p-4 bg-rose-50 border border-rose-100 rounded-2xl text-rose-600 text-[10px] font-black uppercase tracking-widest text-center animate-shake">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading || !file}
          className="w-full bg-slate-950 border border-slate-900 hover:bg-slate-800 disabled:opacity-50 text-white py-6 rounded-[2rem] font-black uppercase tracking-[0.3em] text-xs transition-all transform active:scale-95 shadow-2xl shadow-slate-900/10 flex items-center justify-center"
        >
          {loading ? (
            <div className="flex items-center space-x-3">
              <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
              <span>Synchronizing...</span>
            </div>
          ) : 'Execute Pipeline'}
        </button>
      </form>
    </div>
  );
};

export default FileUpload;
