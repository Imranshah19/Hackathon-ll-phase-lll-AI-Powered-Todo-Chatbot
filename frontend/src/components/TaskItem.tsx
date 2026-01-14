"use client";

import Link from "next/link";
import { Task } from "@/lib/api";

interface TaskItemProps {
  task: Task;
  onToggle: (id: string, completed: boolean) => void;
  onDelete: (id: string) => void;
}

export function TaskItem({ task, onToggle, onDelete }: TaskItemProps) {
  return (
    <div className="flex items-center justify-between p-4 bg-white border rounded-lg shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-center space-x-4 flex-1">
        <input
          type="checkbox"
          checked={task.is_completed}
          onChange={() => onToggle(task.id, !task.is_completed)}
          className="h-5 w-5 text-blue-600 rounded border-gray-300 focus:ring-blue-500 cursor-pointer"
        />
        <div className="flex-1 min-w-0">
          <h3
            className={`text-lg font-medium truncate ${
              task.is_completed ? "line-through text-gray-400" : "text-gray-900"
            }`}
          >
            {task.title}
          </h3>
          {task.description && (
            <p
              className={`text-sm truncate ${
                task.is_completed ? "text-gray-300" : "text-gray-500"
              }`}
            >
              {task.description}
            </p>
          )}
        </div>
      </div>

      <div className="flex items-center space-x-2 ml-4">
        <Link
          href={`/tasks/${task.id}/edit`}
          className="px-3 py-1 text-sm text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded transition-colors"
        >
          Edit
        </Link>
        <button
          onClick={() => onDelete(task.id)}
          className="px-3 py-1 text-sm text-red-600 hover:text-red-800 hover:bg-red-50 rounded transition-colors"
        >
          Delete
        </button>
      </div>
    </div>
  );
}
