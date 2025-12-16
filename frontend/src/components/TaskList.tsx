import React, { useState, useEffect } from 'react';
import { taskAPI, Task } from '../services/api';

interface TaskListProps {
  tasks: Task[];
  onRefresh: () => void;
}

const TaskList: React.FC<TaskListProps> = ({ tasks, onRefresh }) => {
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [polling, setPolling] = useState<string | null>(null);

  useEffect(() => {
    // Poll for task updates
    if (polling) {
      const interval = setInterval(async () => {
        try {
          const task = await taskAPI.getTask(polling);
          setSelectedTask(task);
          if (task.status === 'completed' || task.status === 'failed') {
            setPolling(null);
            onRefresh();
          }
        } catch (error) {
          console.error('Failed to poll task:', error);
        }
      }, 2000);
      return () => clearInterval(interval);
    }
  }, [polling, onRefresh]);

  const handleTaskClick = async (taskId: string) => {
    try {
      const task = await taskAPI.getTask(taskId);
      setSelectedTask(task);
      if (task.status === 'pending' || task.status === 'running') {
        setPolling(taskId);
      }
    } catch (error) {
      console.error('Failed to load task:', error);
    }
  };

  const handleDownload = async (taskId: string, fileType: string = 'csv') => {
    try {
      const blob = await taskAPI.downloadTask(taskId, fileType);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `task_${taskId}.${fileType}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Failed to download:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'running':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white shadow rounded-lg">
      <div className="p-4">
        {tasks.length === 0 ? (
          <p className="text-gray-500 text-center py-4">No tasks yet</p>
        ) : (
          <ul className="divide-y divide-gray-200">
            {tasks.map((task) => (
              <li
                key={task.task_id}
                className="py-3 cursor-pointer hover:bg-gray-50"
                onClick={() => handleTaskClick(task.task_id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">
                      {task.file_name || task.task_id}
                    </p>
                    <p className="text-sm text-gray-500">{task.message}</p>
                  </div>
                  <span
                    className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(
                      task.status
                    )}`}
                  >
                    {task.status}
                  </span>
                </div>
                {task.progress > 0 && (
                  <div className="mt-2">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-indigo-600 h-2 rounded-full"
                        style={{ width: `${task.progress}%` }}
                      />
                    </div>
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>

      {selectedTask && (
        <div className="border-t p-4 bg-gray-50">
          <h3 className="text-lg font-semibold mb-2">Task Details</h3>
          <div className="space-y-2 text-sm">
            <p>
              <span className="font-medium">Status:</span>{' '}
              <span className={getStatusColor(selectedTask.status)}>
                {selectedTask.status}
              </span>
            </p>
            <p>
              <span className="font-medium">Progress:</span> {selectedTask.progress}%
            </p>
            {selectedTask.error && (
              <p className="text-red-600">
                <span className="font-medium">Error:</span> {selectedTask.error}
              </p>
            )}
            {selectedTask.status === 'completed' && selectedTask.output_files && (
              <div>
                <p className="font-medium mb-1">Download:</p>
                <div className="space-x-2">
                  {['csv', 'excel', 'parquet'].map((fmt) => (
                    <button
                      key={fmt}
                      onClick={() => handleDownload(selectedTask.task_id, fmt)}
                      className="px-3 py-1 bg-indigo-600 text-white rounded text-xs hover:bg-indigo-700"
                    >
                      {fmt.toUpperCase()}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default TaskList;

