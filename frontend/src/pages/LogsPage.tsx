/**
 * DevFlow – Logs page (full‑page view).
 */

import LogsTable from '../components/LogsTable';

export default function LogsPage() {
  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold gradient-text">Activity Logs</h1>
        <p className="text-gray-500 mt-1">Complete audit trail of all DevOps actions</p>
      </div>
      <LogsTable limit={100} />
    </div>
  );
}
