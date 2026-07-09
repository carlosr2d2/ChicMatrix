"use client";

import { FormEvent, useState } from "react";

import { Alert } from "@/components/auth/Alert";
import { Spinner } from "@/components/auth/Spinner";
import { validateOtp, validatePhone } from "@/lib/validation";

type PhoneLoginFormProps = {
  onRequestOtp: (phone: string) => Promise<{ message: string; otp_code?: string | null }>;
  onSubmitOtp: (phone: string, otpCode: string) => Promise<void>;
};

export function PhoneLoginForm({ onRequestOtp, onSubmitOtp }: PhoneLoginFormProps) {
  const [phone, setPhone] = useState("");
  const [otpCode, setOtpCode] = useState("");
  const [otpSent, setOtpSent] = useState(false);
  const [errors, setErrors] = useState<Record<string, string | null>>({});
  const [feedback, setFeedback] = useState<{ type: "success" | "error"; message: string } | null>(
    null,
  );
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleRequestOtp = async () => {
    const phoneError = validatePhone(phone);
    setErrors({ phone: phoneError });
    if (phoneError) return;

    setIsSubmitting(true);
    setFeedback(null);
    try {
      const result = await onRequestOtp(phone);
      setOtpSent(true);
      setFeedback({ type: "success", message: result.message });
      if (result.otp_code) {
        setOtpCode(result.otp_code);
      }
    } catch (error) {
      setFeedback({
        type: "error",
        message: error instanceof Error ? error.message : "Could not send OTP",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

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
      await onSubmitOtp(phone, otpCode);
    } catch (error) {
      setFeedback({
        type: "error",
        message: error instanceof Error ? error.message : "Login failed",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5" noValidate>
      <div>
        <label htmlFor="login-phone" className="block text-sm text-stone-600 mb-2">
          Phone number
        </label>
        <div className="flex gap-2">
          <input
            id="login-phone"
            type="tel"
            value={phone}
            onChange={(event) => setPhone(event.target.value)}
            placeholder="+573001234567"
            className="flex-1 border border-sand bg-white px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-ink"
            autoComplete="tel"
            aria-invalid={Boolean(errors.phone)}
            required
          />
          <button
            type="button"
            onClick={handleRequestOtp}
            className="btn-outline whitespace-nowrap px-4"
            disabled={isSubmitting}
          >
            Send OTP
          </button>
        </div>
        {errors.phone ? <p className="mt-2 text-sm text-red-600" role="alert">{errors.phone}</p> : null}
      </div>

      {otpSent ? (
        <div className="animate-fade-in">
          <label htmlFor="login-otp" className="block text-sm text-stone-600 mb-2">
            Verification code
          </label>
          <input
            id="login-otp"
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
      ) : null}

      <button type="submit" className="btn-primary w-full" disabled={isSubmitting || !otpSent}>
        {isSubmitting ? <Spinner label="Signing in..." className="text-white" /> : "Sign in with OTP"}
      </button>

      {feedback ? (
        <Alert variant={feedback.type === "success" ? "success" : "error"}>{feedback.message}</Alert>
      ) : null}
    </form>
  );
}
