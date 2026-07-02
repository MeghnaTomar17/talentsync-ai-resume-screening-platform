import { useState } from 'react';
import type { FormEvent } from 'react';
import { useToast } from '@/hooks/useToast';

type Errors = Record<string, string>;

function emailValid(value: string) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

export function useAuthForm() {
  const [errors, setErrors] = useState<Errors>({});
  const { showToast } = useToast();

  function validate(fields: Errors) {
    setErrors(fields);
    if (Object.keys(fields).length === 0) {
      showToast('Form is valid. Authentication is not connected yet.');
    }
  }

  function validateEmailPassword(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const next: Errors = {};
    if (!emailValid(String(form.get('email') || ''))) next.email = 'Enter a valid email.';
    if (String(form.get('password') || '').length < 8) next.password = 'Use at least 8 characters.';
    validate(next);
  }

  function validateRegistration(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const next: Errors = {};
    if (String(form.get('name') || '').trim().length < 2) next.name = 'Enter your name.';
    if (!emailValid(String(form.get('email') || ''))) next.email = 'Enter a valid email.';
    if (String(form.get('password') || '').length < 8) next.password = 'Use at least 8 characters.';
    validate(next);
  }

  function validateEmailOnly(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const next: Errors = {};
    if (!emailValid(String(form.get('email') || ''))) next.email = 'Enter a valid email.';
    validate(next);
  }

  return { errors, validateEmailPassword, validateRegistration, validateEmailOnly };
}
