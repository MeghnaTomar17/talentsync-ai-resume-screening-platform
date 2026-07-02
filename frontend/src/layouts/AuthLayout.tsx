import { Link, Outlet } from 'react-router-dom';

export function AuthLayout() {
  return (
    <main className="auth-shell">
      <section className="auth-panel">
        <Link className="brand" to="/">
          <span className="brand-mark">TS</span>
          <span>TalentSync AI</span>
        </Link>
        <div className="auth-copy">
          <p>AI-powered screening</p>
          <h1>Hire and grow with evidence, not guesswork.</h1>
          <span>Semantic matching, ATS intelligence, and career guidance in one workspace.</span>
        </div>
      </section>
      <section className="auth-form-wrap">
        <Outlet />
      </section>
    </main>
  );
}
