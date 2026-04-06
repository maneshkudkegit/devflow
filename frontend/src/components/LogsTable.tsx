/**
 * DevFlow – Logs table component.
 * Displays activity logs in a clean, sortable table with status badges.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchLogs, deleteLog, type LogEntry } from '../services/api';
import { RefreshCw, Clock, Zap, Trash2 } from 'lucide-react';

function StatusBadge({ status }: { status: string }) {
  const lower = status.toLowerCase();
  if (lower === 'success') return <span className="badge-success">✓ Success</span>;
  if (lower === 'error')   return <span className="badge-error">✗ Error</span>;
  return <span className="badge-pending">● {status}</span>;
}

function formatTime(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
}

export default function LogsTable({ limit = 50 }: { limit?: number }) {
  const queryClient = useQueryClient();
  const { data: logs, isLoading, isError, refetch, isFetching } = useQuery<LogEntry[]>({
    queryKey: ['logs', limit],
    queryFn: () => fetchLogs(limit),
    refetchInterval: 10_000,
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteLog(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['logs', limit] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
    },
  });

  return (
    <div className="glass-card overflow-hidden animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-glass-border">
        <div className="flex items-center gap-2">
          <Zap className="w-4 h-4 text-df-400" />
          <h3 className="text-sm font-semibold text-gray-200">Activity Logs</h3>
          {logs && (
            <span className="text-xs text-gray-500">({logs.length})</span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => refetch()}
            disabled={isFetching}
            className="p-2 rounded-lg text-gray-400 hover:text-df-300 hover:bg-df-500/10 transition-all disabled:opacity-30"
          >
            <RefreshCw className={`w-4 h-4 ${isFetching ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-500 text-xs uppercase tracking-wider border-b border-glass-border">
              <th className="px-6 py-3 font-medium">Action</th>
              <th className="px-6 py-3 font-medium">Source</th>
              <th className="px-6 py-3 font-medium">Status</th>
              <th className="px-6 py-3 font-medium">Time</th>
              <th className="px-6 py-3 font-medium">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-glass-border">
            {isLoading && (
              <tr>
                <td colSpan={5} className="px-6 py-12 text-center text-gray-500">
                  <RefreshCw className="w-5 h-5 mx-auto mb-2 animate-spin text-df-400" />
                  Loading logs…
                </td>
              </tr>
            )}
            {isError && (
              <tr>
                <td colSpan={5} className="px-6 py-12 text-center text-red-400">
                  Failed to load logs. Is the backend running?
                </td>
              </tr>
            )}
            {logs && logs.length === 0 && (
              <tr>
                <td colSpan={5} className="px-6 py-12 text-center text-gray-500">
                  No activity yet. Run a command to get started!
                </td>
              </tr>
            )}
            {logs?.map((log) => (
              <tr key={log.id} className="hover:bg-surface-50/50 transition-colors duration-150">
                <td className="px-6 py-3.5">
                  <div className="font-medium text-gray-200 truncate max-w-xs" title={log.action}>
                    {log.action}
                  </div>
                  {log.detail && (
                    <div className="text-xs text-gray-500 truncate max-w-xs mt-0.5" title={log.detail}>
                      {log.detail}
                    </div>
                  )}
                </td>
                <td className="px-6 py-3.5">
                  <span className="badge-info">{log.source}</span>
                </td>
                <td className="px-6 py-3.5">
                  <StatusBadge status={log.status} />
                </td>
                <td className="px-6 py-3.5">
                  <div className="flex items-center gap-1.5 text-gray-400 text-xs">
                    <Clock className="w-3 h-3" />
                    {formatTime(log.timestamp)}
                  </div>
                </td>
                <td className="px-6 py-3.5">
                  <button
                    type="button"
                    onClick={() => deleteMutation.mutate(log.id)}
                    disabled={deleteMutation.isPending}
                    className="btn-danger text-[11px] px-3 py-1"
                  >
                    <Trash2 className="w-3 h-3" />
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
