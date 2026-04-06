/**
 * DevFlow – Users page.
 * Create Snowflake users, reset passwords, and view the user list.
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  createUser,
  resetPassword,
  deleteUser,
  listUsers,
  type CommandResult,
  type SnowflakeUser,
} from '../services/api';
import {
  Users as UsersIcon,
  UserPlus,
  KeyRound,
  Loader2,
  CheckCircle2,
  XCircle,
  ShieldCheck,
  Trash2,
} from 'lucide-react';

export default function Users() {
  const queryClient = useQueryClient();

  /* ── Create user form state ── */
  const [username, setUsername] = useState('');
  const [role, setRole] = useState('PUBLIC');
  const [createResult, setCreateResult] = useState<CommandResult | null>(null);

  /* ── Reset password state ── */
  const [resetUser, setResetUser] = useState('');
  const [resetResult, setResetResult] = useState<CommandResult | null>(null);
  const [deleteResult, setDeleteResult] = useState<CommandResult | null>(null);

  /* ── Query: user list ── */
  const { data: usersData } = useQuery<{ status: string; users: SnowflakeUser[]; message?: string }>({
    queryKey: ['users'],
    queryFn: listUsers,
    refetchInterval: 30_000,
  });

  /* ── Mutations ── */
  const createMutation = useMutation({
    mutationFn: () => createUser(username, role),
    onSuccess: (data) => {
      setCreateResult(data);
      setUsername('');
      queryClient.invalidateQueries({ queryKey: ['users'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
    },
    onError: (err: Error) => setCreateResult({ status: 'error', message: err.message }),
  });

  const resetMutation = useMutation({
    mutationFn: () => resetPassword(resetUser),
    onSuccess: (data) => {
      setResetResult(data);
      setResetUser('');
    },
    onError: (err: Error) => setResetResult({ status: 'error', message: err.message }),
  });

  const deleteMutation = useMutation({
    mutationFn: (username: string) => deleteUser(username),
    onSuccess: (data) => {
      setDeleteResult(data);
      queryClient.invalidateQueries({ queryKey: ['users'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
    },
    onError: (err: Error) => setDeleteResult({ status: 'error', message: err.message }),
  });

  /* ── Helpers ── */
  function ResultBanner({ result }: { result: CommandResult | null }) {
    if (!result) return null;
    const ok = result.status === 'success';
    return (
      <div
        className={`mt-4 p-4 rounded-xl border text-sm flex items-start gap-2 animate-slide-down ${
          ok ? 'border-emerald-500/20 bg-emerald-500/5 text-emerald-400' : 'border-red-500/20 bg-red-500/5 text-red-400'
        }`}
      >
        {ok ? <CheckCircle2 className="w-4 h-4 mt-0.5 shrink-0" /> : <XCircle className="w-4 h-4 mt-0.5 shrink-0" />}
        {result.message}
      </div>
    );
  }

  const listError = usersData?.status === 'error' ? { status: 'error', message: usersData.message ?? 'Unable to load users' } : null;
  const users = usersData?.users ?? [];

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold gradient-text">User Management</h1>
        <p className="text-gray-500 mt-1">Create Snowflake users, assign roles, and reset passwords</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Create user */}
        <div className="glass-card p-6 animate-slide-up">
          <h2 className="text-lg font-semibold text-gray-200 mb-5 flex items-center gap-2">
            <UserPlus className="w-5 h-5 text-df-400" />
            Create User
          </h2>

          <div className="space-y-4">
            <div>
              <label htmlFor="new-username" className="block text-xs font-medium text-gray-400 mb-1.5 uppercase tracking-wider">
                Username
              </label>
              <input
                id="new-username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="e.g. john_doe"
                className="input-field"
              />
            </div>

            <div>
              <label htmlFor="new-role" className="block text-xs font-medium text-gray-400 mb-1.5 uppercase tracking-wider">
                Role
              </label>
              <select
                id="new-role"
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="input-field appearance-none cursor-pointer"
              >
                <option value="PUBLIC">PUBLIC</option>
                <option value="ANALYST">ANALYST</option>
                <option value="ENGINEER">ENGINEER</option>
                <option value="SYSADMIN">SYSADMIN</option>
                <option value="ACCOUNTADMIN">ACCOUNTADMIN</option>
              </select>
            </div>

            <button
              onClick={() => createMutation.mutate()}
              disabled={createMutation.isPending || !username.trim()}
              className="btn-primary w-full"
            >
              {createMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <UserPlus className="w-4 h-4" />}
              {createMutation.isPending ? 'Creating…' : 'Create User'}
            </button>

            <ResultBanner result={createResult} />
          </div>
        </div>

        {/* Reset password */}
        <div className="glass-card p-6 animate-slide-up" style={{ animationDelay: '0.1s' }}>
          <h2 className="text-lg font-semibold text-gray-200 mb-5 flex items-center gap-2">
            <KeyRound className="w-5 h-5 text-amber-400" />
            Reset Password
          </h2>

          <div className="space-y-4">
            <div>
              <label htmlFor="reset-username" className="block text-xs font-medium text-gray-400 mb-1.5 uppercase tracking-wider">
                Username
              </label>
              <input
                id="reset-username"
                type="text"
                value={resetUser}
                onChange={(e) => setResetUser(e.target.value)}
                placeholder="e.g. john_doe"
                className="input-field"
              />
            </div>

            <button
              onClick={() => resetMutation.mutate()}
              disabled={resetMutation.isPending || !resetUser.trim()}
              className="btn-secondary w-full"
            >
              {resetMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <KeyRound className="w-4 h-4" />}
              {resetMutation.isPending ? 'Resetting…' : 'Reset Password'}
            </button>

            <ResultBanner result={resetResult} />
          </div>
        </div>
      </div>

      {/* User list */}
      <div className="glass-card overflow-hidden animate-slide-up" style={{ animationDelay: '0.2s' }}>
        <div className="flex items-center gap-2 px-6 py-4 border-b border-glass-border">
          <UsersIcon className="w-4 h-4 text-df-400" />
          <h3 className="text-sm font-semibold text-gray-200">Current Users</h3>
          <span className="text-xs text-gray-500">({users.length})</span>
        </div>
        <div className="px-6 py-4">
          <ResultBanner result={listError} />
          <ResultBanner result={deleteResult} />
        </div>
        <div className="divide-y divide-glass-border">
          {users.length === 0 && (
            <div className="px-6 py-10 text-center text-gray-500 text-sm">No users found.</div>
          )}
          {users.map((u) => (
            <div key={u.name} className="flex items-center justify-between px-6 py-4 hover:bg-surface-50/30 transition-colors">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-df-600/20 flex items-center justify-center text-df-300 text-sm font-semibold uppercase">
                  {u.name[0]}
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-200">{u.name}</p>
                  <p className="text-xs text-gray-500">{u.status}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <div className="flex items-center gap-2 text-xs">
                  <ShieldCheck className="w-3.5 h-3.5 text-df-400" />
                  <span className="text-gray-400">{u.role}</span>
                </div>
                <button
                  type="button"
                  onClick={() => deleteMutation.mutate(u.name)}
                  disabled={deleteMutation.isPending}
                  className="btn-danger flex items-center gap-2 text-xs"
                >
                  <Trash2 className="w-4 h-4" />
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
