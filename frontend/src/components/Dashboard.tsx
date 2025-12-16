import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { taskAPI, Task } from '../services/api';
import FileUpload from './FileUpload';
import TaskList from './TaskList';

const Dashboard: React.FC = () => {
  const [user, setUser] = useState<any>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const userStr = localStorage.getItem('user');
    if (!userStr) {
      navigate('/login');
      return;
    }
    setUser(JSON.parse(userStr));
    loadTasks();
  }, [navigate]);

  const loadTasks = async () => {
    try {
      const data = await taskAPI.listTasks(20);
      setTasks(data.tasks || []);
    } catch (error) {
      console.error('Failed to load tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  const handleTaskCreated = (taskId: string) => {
    loadTasks();
  };

  if (loading) {
    return <div className="flex justify-center items-center h-screen">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold">Data Cleaning Pipeline</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">Welcome, {user?.username}</span>
              <button
                onClick={handleLogout}
                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <h2 className="text-2xl font-bold mb-4">Upload Data File</h2>
              <FileUpload onTaskCreated={handleTaskCreated} />
            </div>
            <div>
              <h2 className="text-2xl font-bold mb-4">Recent Tasks</h2>
              <TaskList tasks={tasks} onRefresh={loadTasks} />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;

