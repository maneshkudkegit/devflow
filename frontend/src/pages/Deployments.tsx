/**
 * DevFlow – Deployments page.
 * Trigger GitHub Actions workflows and view recent deployment runs.
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { triggerDeploy, fetchLogs, type LogEntry, type CommandResult } from '../services/api';
import { Rocket, GitBranch, Target, Loader2, CheckCircle2, XCircle, Clock } from 'lucide-react';

export default function Deployments() {
  const queryClient = useQueryClient();
  const [target, setTarget] = useState('backend');
  const [ref, setRef] = useState('main');
  const [lastResult, setLastResult] = useState<CommandResult | null>(null);

  const { data: logs } = useQuery<LogEntry[]>({
    queryKey: ['deploy-logs'],
    queryFn: () => fetchLogs(20),
    refetchInterval: 10_000,
    select: (data) => data.filter((l) => l.action.startsWith('deploy')),
  });

  const deployMutation = useMutation({
    mutationFn: () => triggerDeploy(target, ref),
    onSuccess: (data) => {
      setLastResult(data);
      queryClient.invalidateQueries({ queryKey: ['deploy-logs'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
    },
    onError: (err: Error) => {
      setLastResult({ status: 'error', message: err.message });
    },
  });

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold gradient-text">Deployments</h1>
        <p className="text-gray-500 mt-1">Trigger GitHub Actions workflows and monitor their status</p>
      </div>

      {/* Deploy form */}
      <div className="glass-card p-6 animate-slide-up">
        <h2 className="text-lg font-semibold text-gray-200 mb-5 flex items-center gap-2">
          <Rocket className="w-5 h-5 text-df-400" />
          Trigger Deployment
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-5">
          <div>
            <label htmlFor="deploy-target" className="block text-xs font-medium text-gray-400 mb-1.5 uppercase tracking-wider">
              Target
            </label>
            <div className="relative">
              <Target className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              <select
                id="deploy-target"
                value={target}
                onChange={(e) => setTarget(e.target.value)}
                className="input-field pl-10 appearance-none cursor-pointer"
              >
                <option value="backend">Backend</option>
                <option value="frontend">Frontend</option>
                <option value="infra">Infrastructure</option>
                <option value="full">Full Stack</option>
              </select>
            </div>
          </div>

          <div>
            <label htmlFor="deploy-ref" className="block text-xs font-medium text-gray-400 mb-1.5 uppercase tracking-wider">
              Git Ref
            </label>
            <div className="relative">
              <GitBranch className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input
                id="deploy-ref"
                type="text"
                value={ref}
                onChange={(e) => setRef(e.target.value)}
                placeholder="main"
                className="input-field pl-10"
              />
            </div>
          </div>
        </div>

        <button
          onClick={() => deployMutation.mutate()}
          disabled={deployMutation.isPending}
          className="btn-primary"
        >
          {deployMutation.isPending ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Rocket className="w-4 h-4" />
          )}
          {deployMutation.isPending ? 'Deploying…' : 'Deploy Now'}
        </button>

        {/* Result */}
        {lastResult && (
          <div
            className={`mt-4 p-4 rounded-xl border text-sm flex items-start gap-2 animate-slide-down ${
              lastResult.status === 'success'
                ? 'border-emerald-500/20 bg-emerald-500/5 text-emerald-400'
                : 'border-red-500/20 bg-red-500/5 text-red-400'
            }`}
          >
            {lastResult.status === 'success' ? (
              <CheckCircle2 className="w-4 h-4 mt-0.5 shrink-0" />
            ) : (
              <XCircle className="w-4 h-4 mt-0.5 shrink-0" />
            )}
            {lastResult.message}
          </div>
        )}
      </div>

      {/* Deployment history */}
      <div className="glass-card overflow-hidden animate-slide-up">
        <div className="px-6 py-4 border-b border-glass-border">
          <h3 className="text-sm font-semibold text-gray-200">Deployment History</h3>
        </div>
        <div className="divide-y divide-glass-border">
          {(!logs || logs.length === 0) && (
            <div className="px-6 py-10 text-center text-gray-500 text-sm">
              No deployments yet. Trigger your first one above!
            </div>
          )}
          {logs?.map((log) => (
            <div key={log.id} className="flex items-center justify-between px-6 py-4 hover:bg-surface-50/30 transition-colors">
              <div className="flex items-center gap-3">
                <Rocket className="w-4 h-4 text-df-400" />
                <div>
                  <p className="text-sm font-medium text-gray-200">{log.action}</p>
                  {log.detail && <p className="text-xs text-gray-500 mt-0.5">{log.detail}</p>}
                </div>
              </div>
              <div className="flex items-center gap-4">
                <span
                  className={
                    log.status === 'success' ? 'badge-success' : log.status === 'error' ? 'badge-error' : 'badge-pending'
                  }
                >
                  {log.status}
                </span>
                <div className="flex items-center gap-1 text-gray-500 text-xs">
                  <Clock className="w-3 h-3" />
                  {new Date(log.timestamp).toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
