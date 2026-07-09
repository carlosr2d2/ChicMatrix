"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";

import { Alert } from "@/components/auth/Alert";
import { ConsentCheckbox } from "@/components/auth/ConsentCheckbox";
import { Spinner } from "@/components/auth/Spinner";
import { validateEmail, validatePassword } from "@/lib/validation";

type EmailRegisterFormProps = {
  onSubmit: (values: {
    email: string;
    password: string;
    name?: string;
    consent_accepted: boolean;
  }) => Promise<{ message: string; verification_token?: string | null }>;
};

export function EmailRegisterForm({ onSubmit }: EmailRegisterFormProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [consent, setConsent] = useState(false);
  const [errors, setErrors] = useState<Record<string, string | null>>({});
  const [feedback, setFeedback] = useState<{ type: "success" | "error"; message: string } | null>(
    null,
  );
  const [debugToken, setDebugToken] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    const nextErrors = {
      email: validateEmail(email),
      password: validatePassword(password),
      consent: consent ? null : "Consent is required",
    };
    setErrors(nextErrors);
    if (Object.values(nextErrors).some(Boolean)) return;

    setIsSubmitting(true);
    setFeedback(null);
    setDebugToken(null);

    try {
      const result = await onSubmit({
        email,
        password,
        name: name || undefined,
        consent_accepted: consent,
      });
      setFeedback({ type: "success", message: result.message });
      if (result.verification_token) {
        setDebugToken(result.verification_token);
      }
    } catch (error) {
      setFeedback({
        type: "error",
        message: error instanceof Error ? error.message : "Registration failed",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5" noValidate>
      <div>
        <label htmlFor="register-name" className="block text-sm text-stone-600 mb-2">
          Name <span className="text-stone-400">(optional)</span>
        </label>
        <input
          id="register-name"
          type="text"
          value={name}
          onChange={(event) => setName(event.target.value)}
          className="w-full border border-sand bg-white px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-ink"
          autoComplete="name"
        />
      </div>

      <div>
        <label htmlFor="register-email" className="block text-sm text-stone-600 mb-2">
          Email
        </label>
        <input
          id="register-email"
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          className="w-full border border-sand bg-white px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-ink"
          autoComplete="email"
          aria-invalid={Boolean(errors.email)}
          aria-describedby={errors.email ? "register-email-error" : undefined}
          required
        />
        {errors.email ? (
          <p id="register-email-error" className="mt-2 text-sm text-red-600" role="alert">
            {errors.email}
          </p>
        ) : null}
      </div>

      <div>
        <label htmlFor="register-password" className="block text-sm text-stone-600 mb-2">
          Password
        </label>
        <input
          id="register-password"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          className="w-full border border-sand bg-white px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-ink"
          autoComplete="new-password"
          aria-invalid={Boolean(errors.password)}
          aria-describedby={errors.password ? "register-password-error" : undefined}
          required
          minLength={8}
        />
        {errors.password ? (
          <p id="register-password-error" className="mt-2 text-sm text-red-600" role="alert">
            {errors.password}
          </p>
        ) : null}
      </div>

      <ConsentCheckbox checked={consent} onChange={setConsent} error={errors.consent} />

      <button type="submit" className="btn-primary w-full" disabled={isSubmitting}>
        {isSubmitting ? <Spinner label="Creating account..." className="text-white" /> : "Create account"}
      </button>

      {feedback ? (
        <Alert variant={feedback.type === "success" ? "success" : "error"}>{feedback.message}</Alert>
      ) : null}

      {debugToken ? (
        <Alert variant="info" title="Development verification token">
          <p className="mb-3">Use this token on the verify page:</p>
          <code className="block break-all text-xs bg-cream px-2 py-2">{debugToken}</code>
          <Link href={`/verify?token=${encodeURIComponent(debugToken)}`} className="inline-block mt-3 underline">
            Verify now
          </Link>
        </Alert>
      ) : null}
    </form>
  );
}
