import { Link, Outlet } from 'react-router-dom';
import Button from '@/components/ui/Button';

export function PublicLayout() {
  return (
    <div className="public-shell">
      <header className="public-nav">
        <Link className="brand" to="/">
          <span className="brand-mark">TS</span>
          <span>TalentSync AI</span>
        </Link>
        <nav aria-label="Primary navigation">
          <a href="#features">Features</a>
          <a href="#workflow">Workflow</a>
          <a href="#stack">Stack</a>
        </nav>
        <div className="nav-actions">
          <Link to="/auth/login">Log in</Link>
          <Link to="/app/upload">
            <Button size="sm">Open app</Button>
          </Link>
        </div>
      </header>
      <Outlet />
    </div>
  );
}
