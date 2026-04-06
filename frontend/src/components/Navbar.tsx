/**
 * DevFlow – Global navigation bar.
 * Features a glowing brand logo and smooth link transitions.
 */

import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Terminal, Users, Rocket, ScrollText } from 'lucide-react';

const links = [
  { to: '/',            label: 'Dashboard',   icon: LayoutDashboard },
  { to: '/deployments', label: 'Deployments', icon: Rocket },
  { to: '/users',       label: 'Users',       icon: Users },
  { to: '/logs',        label: 'Logs',        icon: ScrollText },
];

export default function Navbar() {
  return (
    <aside className="fixed inset-y-0 left-0 z-40 flex flex-col w-64 bg-surface-100/80 backdrop-blur-xl border-r border-glass-border">
      {/* Brand */}
      <div className="flex items-center gap-3 px-6 py-6">
        <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-df-500 to-purple-600 shadow-glow-sm">
          <Terminal className="w-5 h-5 text-white" />
          <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-df-500 to-purple-600 blur-lg opacity-40" />
        </div>
        <div>
          <h1 className="text-lg font-bold gradient-text">DevFlow</h1>
          <p className="text-[10px] uppercase tracking-widest text-gray-500 font-medium">Automation Hub</p>
        </div>
      </div>

      {/* Navigation links */}
      <nav className="flex-1 px-3 mt-4 space-y-1">
        {links.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 group ${
                isActive
                  ? 'bg-df-600/15 text-df-300 border border-df-500/20 shadow-glow-sm'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-surface-50/80'
              }`
            }
          >
            <Icon className="w-[18px] h-[18px] transition-transform duration-200 group-hover:scale-110" />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-6 py-4 border-t border-glass-border">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse-slow" />
          <span className="text-xs text-gray-500">System Online</span>
        </div>
      </div>
    </aside>
  );
}
