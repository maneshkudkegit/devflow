/**
 * DevFlow – Application root.
 * Sets up React Router and the layout (sidebar + main content area).
 */

import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Deployments from './pages/Deployments';
import Users from './pages/Users';
import LogsPage from './pages/LogsPage';

export default function App() {
  return (
    <BrowserRouter>
      {/* Ambient background glow */}
      <div className="ambient-glow" />

      <div className="flex min-h-screen">
        {/* Sidebar */}
        <Navbar />

        {/* Main content */}
        <main className="flex-1 ml-64 p-8 lg:p-10">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/deployments" element={<Deployments />} />
            <Route path="/users" element={<Users />} />
            <Route path="/logs" element={<LogsPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
