"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";

import { Alert } from "@/components/auth/Alert";
import { Spinner } from "@/components/auth/Spinner";

type VerifyEmailFormProps = {
  initialToken?: string;
  onSubmit: (token: string) => Promise<{ message: string }>;
};

export function VerifyEmailForm({ initialToken = "", onSubmit }: VerifyEmailFormProps) {
  const [token, setToken] = useState(initialToken);
  const [feedback, setFeedback] = useState<{ type: "success" | "error"; message: string } | null>(
    null,
  );
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (initialToken) {
      setToken(initialToken);
    }
  }, [initialToken]);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!token.trim()) {
      setFeedback({ type: "error", message: "Verification token is required" });
      return;
    }

    setIsSubmitting(true);
    setFeedback(null);
    try {
      const result = await onSubmit(token.trim());
      setFeedback({ type: "success", message: result.message });
    } catch (error) {
      setFeedback({
        type: "error",
        message: error instanceof Error ? error.message : "Verification failed",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5" noValidate>
      <div>
        <label htmlFor="verify-email-token" className="block text-sm text-stone-600 mb-2">
          Email verification token
        </label>
        <input
          id="verify-email-token"
          type="text"
          value={token}
          onChange={(event) => setToken(event.target.value)}
          className="w-full border border-sand bg-white px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-ink"
          aria-describedby="verify-email-help"
          required
        />
        <p id="verify-email-help" className="mt-2 text-sm text-stone-500 font-light">
          Paste the token from your verification email.
        </p>
      </div>

      <button type="submit" className="btn-primary w-full" disabled={isSubmitting}>
        {isSubmitting ? <Spinner label="Verifying..." className="text-white" /> : "Verify email"}
      </button>

      {feedback ? (
        <div className="space-y-3">
          <Alert variant={feedback.type === "success" ? "success" : "error"}>{feedback.message}</Alert>
          {feedback.type === "success" ? (
            <Link href="/login" className="inline-block text-sm underline">
              Continue to sign in
            </Link>
          ) : null}
        </div>
      ) : null}
    </form>
  );
}
