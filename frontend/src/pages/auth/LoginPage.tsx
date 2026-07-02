import { Link } from 'react-router-dom';
import Button from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { useAuthForm } from '@/hooks/useAuthForm';

export function LoginPage() {
  const { errors, validateEmailPassword } = useAuthForm();

  return (
    <form className="auth-card" onSubmit={validateEmailPassword}>
      <div>
        <h1>Welcome back</h1>
        <p>Sign in to continue to your TalentSync workspace.</p>
      </div>
      <label>
        Email
        <Input name="email" placeholder="you@company.com" type="email" />
        {errors.email && <span className="field-error">{errors.email}</span>}
      </label>
      <label>
        Password
        <Input name="password" placeholder="Enter password" type="password" />
        {errors.password && <span className="field-error">{errors.password}</span>}
      </label>
      <Button type="submit">Log in</Button>
      <div className="auth-links">
        <Link to="/auth/forgot-password">Forgot password?</Link>
        <Link to="/auth/register">Create account</Link>
      </div>
    </form>
  );
}
