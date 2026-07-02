import { Link } from 'react-router-dom';
import Button from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { useAuthForm } from '@/hooks/useAuthForm';

export function RegisterPage() {
  const { errors, validateRegistration } = useAuthForm();

  return (
    <form className="auth-card" onSubmit={validateRegistration}>
      <div>
        <h1>Create account</h1>
        <p>Start screening resumes with TalentSync AI.</p>
      </div>
      <label>
        Full name
        <Input name="name" placeholder="Meghna Sharma" />
        {errors.name && <span className="field-error">{errors.name}</span>}
      </label>
      <label>
        Email
        <Input name="email" placeholder="you@company.com" type="email" />
        {errors.email && <span className="field-error">{errors.email}</span>}
      </label>
      <label>
        Password
        <Input name="password" placeholder="Create password" type="password" />
        {errors.password && <span className="field-error">{errors.password}</span>}
      </label>
      <Button type="submit">Register</Button>
      <p className="auth-switch">
        Already have an account? <Link to="/auth/login">Log in</Link>
      </p>
    </form>
  );
}
