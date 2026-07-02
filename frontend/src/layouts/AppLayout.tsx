import { Link, NavLink, Outlet, useLocation } from 'react-router-dom';
import {
  Bell,
  BrainCircuit,
  ChevronDown,
  FileSearch,
  LayoutDashboard,
  Map,
  Menu,
  Moon,
  UploadCloud,
} from 'lucide-react';
import Button from '@/components/ui/Button';
import { useTheme } from '@/hooks/useTheme';

const navItems = [
  { to: '/app', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/app/upload', label: 'Resume Upload', icon: UploadCloud },
  { to: '/app/analysis', label: 'Analysis', icon: FileSearch },
  { to: '/app/coach', label: 'AI Coach', icon: BrainCircuit },
  { to: '/app/roadmap', label: 'Roadmap', icon: Map },
];

function Breadcrumbs() {
  const location = useLocation();
  const segment = location.pathname.split('/').filter(Boolean).at(-1) || 'dashboard';
  return (
    <div className="breadcrumbs">
      <Link to="/app">Workspace</Link>
      <span>/</span>
      <span>{segment.replace('-', ' ')}</span>
    </div>
  );
}

export function AppLayout() {
  const { toggleTheme } = useTheme();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <Link className="brand" to="/">
          <span className="brand-mark">TS</span>
          <span>TalentSync AI</span>
        </Link>
        <nav className="sidebar-nav" aria-label="Application navigation">
          {navItems.map((item) => (
            <NavLink
              className={({ isActive }) => (isActive ? 'sidebar-link active' : 'sidebar-link')}
              end={item.to === '/app'}
              key={item.to}
              to={item.to}
            >
              <item.icon size={18} />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
      </aside>
      <div className="workspace">
        <header className="topbar">
          <div className="mobile-menu">
            <Button aria-label="Open navigation" size="icon" variant="ghost">
              <Menu size={20} />
            </Button>
          </div>
          <Breadcrumbs />
          <div className="topbar-actions">
            <Button aria-label="Toggle theme" onClick={toggleTheme} size="icon" variant="ghost">
              <Moon size={18} />
            </Button>
            <Button aria-label="Notifications" size="icon" variant="ghost">
              <Bell size={18} />
            </Button>
            <button className="profile-menu" type="button">
              <span className="avatar">MS</span>
              <span>Meghna</span>
              <ChevronDown size={16} />
            </button>
          </div>
        </header>
        <main className="workspace-content">
          <Outlet />
        </main>
        <footer className="app-footer">TalentSync AI workspace</footer>
      </div>
    </div>
  );
}
