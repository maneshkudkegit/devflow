/**
 * DevFlow – API service layer.
 * Centralises all HTTP calls to the FastAPI backend.
 */

import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  headers: { 'Content-Type': 'application/json' },
  timeout: 15_000,
});

/* ─── Types ─── */

export interface LogEntry {
  id: number;
  action: string;
  status: string;
  detail: string | null;
  source: string;
  timestamp: string;
}

export interface DashboardStats {
  total_actions: number;
  total_deployments: number;
  total_users_created: number;
  recent_logs: LogEntry[];
}

export interface SnowflakeUser {
  name: string;
  role: string;
  status: string;
}

export interface CommandResult {
  status: string;
  message?: string;
  parsed?: Record<string, unknown>;
  [key: string]: unknown;
}

/* ─── API functions ─── */

/** Fetch dashboard statistics */
export const fetchStats = async (): Promise<DashboardStats> => {
  const { data } = await api.get<DashboardStats>('/api/stats');
  return data;
};

/** Fetch activity logs */
export const fetchLogs = async (limit = 50): Promise<LogEntry[]> => {
  const { data } = await api.get<LogEntry[]>('/api/logs', { params: { limit } });
  return data;
};

/** Delete a log entry */
export const deleteLog = async (id: number): Promise<CommandResult> => {
  const { data } = await api.delete<CommandResult>(`/api/logs/${id}`);
  return data;
};

/** Trigger a deployment */
export const triggerDeploy = async (target = 'backend', ref = 'main'): Promise<CommandResult> => {
  const { data } = await api.post<CommandResult>('/api/deploy', { target, ref });
  return data;
};

/** Create a Snowflake user */
export const createUser = async (username: string, role: string): Promise<CommandResult> => {
  const { data } = await api.post<CommandResult>('/api/users', { username, role });
  return data;
};

/** List Snowflake users */
export const listUsers = async (): Promise<{ status: string; users: SnowflakeUser[] }> => {
  const { data } = await api.get('/api/users');
  return data;
};

/** Reset a user password */
export const resetPassword = async (username: string): Promise<CommandResult> => {
  const { data } = await api.post<CommandResult>('/api/users/reset', { username });
  return data;
};

/** Delete a Snowflake user */
export const deleteUser = async (username: string): Promise<CommandResult> => {
  const { data } = await api.delete<CommandResult>(`/api/users/${encodeURIComponent(username)}`);
  return data;
};

/** Run a free‑text command via the CommandBox */
export const runCommand = async (command: string): Promise<CommandResult> => {
  const { data } = await api.post<CommandResult>('/api/command', { command });
  return data;
};

export default api;
