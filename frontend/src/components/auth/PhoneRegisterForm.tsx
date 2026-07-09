"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";

import { Alert } from "@/components/auth/Alert";
import { ConsentCheckbox } from "@/components/auth/ConsentCheckbox";
import { Spinner } from "@/components/auth/Spinner";
import { validatePhone } from "@/lib/validation";

type PhoneRegisterFormProps = {
  onSubmit: (values: {
    phone: string;
    name?: string;
    consent_accepted: boolean;
  }) => Promise<{ message: string; otp_code?: string | null }>;
};

export function PhoneRegisterForm({ onSubmit }: PhoneRegisterFormProps) {
  const [phone, setPhone] = useState("");
  const [name, setName] = useState("");
  const [consent, setConsent] = useState(false);
  const [errors, setErrors] = useState<Record<string, string | null>>({});
  const [feedback, setFeedback] = useState<{ type: "success" | "error"; message: string } | null>(
    null,
  );
  const [debugOtp, setDebugOtp] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    const nextErrors = {
      phone: validatePhone(phone),
      consent: consent ? null : "Consent is required",
    };
    setErrors(nextErrors);
    if (Object.values(nextErrors).some(Boolean)) return;

    setIsSubmitting(true);
    setFeedback(null);
    setDebugOtp(null);

    try {
      const result = await onSubmit({
        phone,
        name: name || undefined,
        consent_accepted: consent,
      });
      setFeedback({ type: "success", message: result.message });
      if (result.otp_code) {
        setDebugOtp(result.otp_code);
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
        <label htmlFor="register-phone" className="block text-sm text-stone-600 mb-2">
          Phone number
        </label>
        <input
          id="register-phone"
          type="tel"
          value={phone}
          onChange={(event) => setPhone(event.target.value)}
          placeholder="+573001234567"
          className="w-full border border-sand bg-white px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-ink"
          autoComplete="tel"
          aria-invalid={Boolean(errors.phone)}
          aria-describedby={errors.phone ? "register-phone-error" : undefined}
          required
        />
        {errors.phone ? (
          <p id="register-phone-error" className="mt-2 text-sm text-red-600" role="alert">
            {errors.phone}
          </p>
        ) : null}
      </div>

      <div>
        <label htmlFor="register-phone-name" className="block text-sm text-stone-600 mb-2">
          Name <span className="text-stone-400">(optional)</span>
        </label>
        <input
          id="register-phone-name"
          type="text"
          value={name}
          onChange={(event) => setName(event.target.value)}
          className="w-full border border-sand bg-white px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-ink"
          autoComplete="name"
        />
      </div>

      <ConsentCheckbox checked={consent} onChange={setConsent} error={errors.consent} />

      <button type="submit" className="btn-primary w-full" disabled={isSubmitting}>
        {isSubmitting ? <Spinner label="Sending OTP..." className="text-white" /> : "Send verification code"}
      </button>

      {feedback ? (
        <Alert variant={feedback.type === "success" ? "success" : "error"}>{feedback.message}</Alert>
      ) : null}

      {debugOtp ? (
        <Alert variant="info" title="Development OTP">
          <p className="mb-3">Use this code on the verify page:</p>
          <code className="block text-lg tracking-[0.4em]">{debugOtp}</code>
          <Link
            href={`/verify?phone=${encodeURIComponent(phone)}&otp=${debugOtp}`}
            className="inline-block mt-3 underline"
          >
            Verify now
          </Link>
        </Alert>
      ) : null}
    </form>
  );
}
