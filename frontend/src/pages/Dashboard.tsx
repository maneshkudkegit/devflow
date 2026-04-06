/**
 * DevFlow – Dashboard page.
 * Displays summary stats, the CommandBox, and recent activity.
 */

import { useQuery } from '@tanstack/react-query';
import { fetchStats, type DashboardStats } from '../services/api';
import CommandBox from '../components/CommandBox';
import LogsTable from '../components/LogsTable';
import { Rocket, Users, Activity, TrendingUp } from 'lucide-react';

function StatCard({
  label,
  value,
  icon: Icon,
  gradient,
}: {
  label: string;
  value: number | string;
  icon: React.ElementType;
  gradient: string;
}) {
  return (
    <div className="stat-card group animate-slide-up">
      <div className="flex items-center justify-between mb-4">
        <div
          className={`flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br ${gradient} shadow-lg`}
        >
          <Icon className="w-5 h-5 text-white" />
        </div>
        <TrendingUp className="w-4 h-4 text-emerald-400 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
      </div>
      <p className="text-3xl font-bold text-white">{value}</p>
      <p className="text-sm text-gray-400 mt-1">{label}</p>
    </div>
  );
}

export default function Dashboard() {
  const { data: stats } = useQuery<DashboardStats>({
    queryKey: ['stats'],
    queryFn: fetchStats,
    refetchInterval: 15_000,
  });

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Page header */}
      <div>
        <h1 className="text-3xl font-bold gradient-text">Dashboard</h1>
        <p className="text-gray-500 mt-1">Real‑time overview of your DevOps operations</p>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        <StatCard
          label="Total Actions"
          value={stats?.total_actions ?? 0}
          icon={Activity}
          gradient="from-df-500 to-purple-600"
        />
        <StatCard
          label="Deployments"
          value={stats?.total_deployments ?? 0}
          icon={Rocket}
          gradient="from-emerald-500 to-teal-600"
        />
        <StatCard
          label="Users Created"
          value={stats?.total_users_created ?? 0}
          icon={Users}
          gradient="from-amber-500 to-orange-600"
        />
      </div>

      {/* Command Box */}
      <div>
        <h2 className="text-lg font-semibold text-gray-200 mb-3">Command Center</h2>
        <CommandBox />
      </div>

      {/* Recent logs */}
      <div>
        <h2 className="text-lg font-semibold text-gray-200 mb-3">Recent Activity</h2>
        <LogsTable limit={10} />
      </div>
    </div>
  );
}
