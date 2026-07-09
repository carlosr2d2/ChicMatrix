"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";

import { Alert } from "@/components/auth/Alert";
import { Spinner } from "@/components/auth/Spinner";
import { validateOtp, validatePhone } from "@/lib/validation";

type VerifyPhoneFormProps = {
  initialPhone?: string;
  initialOtp?: string;
  onSubmit: (phone: string, otpCode: string) => Promise<{ message: string }>;
};

export function VerifyPhoneForm({
  initialPhone = "",
  initialOtp = "",
  onSubmit,
}: VerifyPhoneFormProps) {
  const [phone, setPhone] = useState(initialPhone);
  const [otpCode, setOtpCode] = useState(initialOtp);
  const [errors, setErrors] = useState<Record<string, string | null>>({});
  const [feedback, setFeedback] = useState<{ type: "success" | "error"; message: string } | null>(
    null,
  );
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (initialPhone) setPhone(initialPhone);
    if (initialOtp) setOtpCode(initialOtp);
  }, [initialPhone, initialOtp]);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    const nextErrors = {
      phone: validatePhone(phone),
      otp: validateOtp(otpCode),
    };
    setErrors(nextErrors);
    if (Object.values(nextErrors).some(Boolean)) return;

    setIsSubmitting(true);
    setFeedback(null);
    try {
      const result = await onSubmit(phone, otpCode);
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
        <label htmlFor="verify-phone" className="block text-sm text-stone-600 mb-2">
          Phone number
        </label>
        <input
          id="verify-phone"
          type="tel"
          value={phone}
          onChange={(event) => setPhone(event.target.value)}
          placeholder="+573001234567"
          className="w-full border border-sand bg-white px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-ink"
          autoComplete="tel"
          aria-invalid={Boolean(errors.phone)}
          required
        />
        {errors.phone ? <p className="mt-2 text-sm text-red-600" role="alert">{errors.phone}</p> : null}
      </div>

      <div>
        <label htmlFor="verify-otp" className="block text-sm text-stone-600 mb-2">
          OTP code
        </label>
        <input
          id="verify-otp"
          type="text"
          inputMode="numeric"
          pattern="\d{6}"
          maxLength={6}
          value={otpCode}
          onChange={(event) => setOtpCode(event.target.value)}
          className="w-full border border-sand bg-white px-4 py-3 text-sm tracking-[0.4em] focus:outline-none focus:ring-2 focus:ring-ink"
          autoComplete="one-time-code"
          aria-invalid={Boolean(errors.otp)}
          required
        />
        {errors.otp ? <p className="mt-2 text-sm text-red-600" role="alert">{errors.otp}</p> : null}
      </div>

      <button type="submit" className="btn-primary w-full" disabled={isSubmitting}>
        {isSubmitting ? <Spinner label="Verifying..." className="text-white" /> : "Verify phone"}
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
