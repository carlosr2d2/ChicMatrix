"use client";

import { FormEvent, useState } from "react";

import { Alert } from "@/components/auth/Alert";
import { Spinner } from "@/components/auth/Spinner";
import { validateEmail, validatePassword } from "@/lib/validation";

type EmailLoginFormProps = {
  onSubmit: (values: { email: string; password: string }) => Promise<void>;
};

export function EmailLoginForm({ onSubmit }: EmailLoginFormProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState<Record<string, string | null>>({});
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    const nextErrors = {
      email: validateEmail(email),
      password: validatePassword(password),
    };
    setErrors(nextErrors);
    if (Object.values(nextErrors).some(Boolean)) return;

    setIsSubmitting(true);
    setError(null);
    try {
      await onSubmit({ email, password });
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Login failed");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5" noValidate>
      <div>
        <label htmlFor="login-email" className="block text-sm text-stone-600 mb-2">
          Email
        </label>
        <input
          id="login-email"
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          className="w-full border border-sand bg-white px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-ink"
          autoComplete="email"
          aria-invalid={Boolean(errors.email)}
          required
        />
        {errors.email ? <p className="mt-2 text-sm text-red-600" role="alert">{errors.email}</p> : null}
      </div>

      <div>
        <label htmlFor="login-password" className="block text-sm text-stone-600 mb-2">
          Password
        </label>
        <input
          id="login-password"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          className="w-full border border-sand bg-white px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-ink"
          autoComplete="current-password"
          aria-invalid={Boolean(errors.password)}
          required
        />
        {errors.password ? (
          <p className="mt-2 text-sm text-red-600" role="alert">{errors.password}</p>
        ) : null}
      </div>

      <button type="submit" className="btn-primary w-full" disabled={isSubmitting}>
        {isSubmitting ? <Spinner label="Signing in..." className="text-white" /> : "Sign in"}
      </button>

      {error ? <Alert variant="error">{error}</Alert> : null}
    </form>
  );
}
