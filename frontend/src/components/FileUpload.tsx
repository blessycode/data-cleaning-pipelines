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
    include_visuals: false,
    apply_cleaning: true,
    enable_feature_suggestions: false,
    validate_final_data: true,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      const ext = e.target.files[0].name.split('.').pop()?.toLowerCase();
      if (ext === 'csv') {
        setOptions({ ...options, file_type: 'csv' });
      } else if (['xlsx', 'xls'].includes(ext || '')) {
        setOptions({ ...options, file_type: 'excel' });
      } else if (ext === 'parquet') {
        setOptions({ ...options, file_type: 'parquet' });
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a file');
      return;
    }

    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const result = await taskAPI.runPipeline(file, options);
      setSuccess(`Task created! ID: ${result.task_id}`);
      onTaskCreated(result.task_id);
      setFile(null);
      // Reset file input
      const fileInput = document.getElementById('file-input') as HTMLInputElement;
      if (fileInput) fileInput.value = '';
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create task');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select File
          </label>
          <input
            id="file-input"
            type="file"
            accept=".csv,.xlsx,.xls,.parquet"
            onChange={handleFileChange}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
          />
        </div>

        <div className="space-y-2">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={options.profile_data}
              onChange={(e) => setOptions({ ...options, profile_data: e.target.checked })}
              className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
            />
            <span className="ml-2 text-sm text-gray-700">Profile Data</span>
          </label>
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={options.apply_cleaning}
              onChange={(e) => setOptions({ ...options, apply_cleaning: e.target.checked })}
              className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
            />
            <span className="ml-2 text-sm text-gray-700">Apply Cleaning</span>
          </label>
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={options.include_visuals}
              onChange={(e) => setOptions({ ...options, include_visuals: e.target.checked })}
              className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
            />
            <span className="ml-2 text-sm text-gray-700">Include Visualizations</span>
          </label>
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={options.enable_feature_suggestions}
              onChange={(e) => setOptions({ ...options, enable_feature_suggestions: e.target.checked })}
              className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
            />
            <span className="ml-2 text-sm text-gray-700">Feature Engineering Suggestions</span>
          </label>
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={options.validate_final_data}
              onChange={(e) => setOptions({ ...options, validate_final_data: e.target.checked })}
              className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
            />
            <span className="ml-2 text-sm text-gray-700">Validate Final Data</span>
          </label>
        </div>

        {error && (
          <div className="rounded-md bg-red-50 p-4">
            <div className="text-sm text-red-800">{error}</div>
          </div>
        )}

        {success && (
          <div className="rounded-md bg-green-50 p-4">
            <div className="text-sm text-green-800">{success}</div>
          </div>
        )}

        <button
          type="submit"
          disabled={loading || !file}
          className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
        >
          {loading ? 'Processing...' : 'Start Pipeline'}
        </button>
      </form>
    </div>
  );
};

export default FileUpload;

