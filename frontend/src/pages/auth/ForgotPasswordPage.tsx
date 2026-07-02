import { Link } from 'react-router-dom';
import Button from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { useAuthForm } from '@/hooks/useAuthForm';

export function ForgotPasswordPage() {
  const { errors, validateEmailOnly } = useAuthForm();

  return (
    <form className="auth-card" onSubmit={validateEmailOnly}>
      <div>
        <h1>Reset password</h1>
        <p>Enter your email and we will prepare a reset link.</p>
      </div>
      <label>
        Email
        <Input name="email" placeholder="you@company.com" type="email" />
        {errors.email && <span className="field-error">{errors.email}</span>}
      </label>
      <Button type="submit">Send reset link</Button>
      <p className="auth-switch">
        Remembered it? <Link to="/auth/login">Back to login</Link>
      </p>
    </form>
  );
}
