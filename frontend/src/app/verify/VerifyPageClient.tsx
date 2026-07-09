"use client";

import { useSearchParams } from "next/navigation";
import { Suspense } from "react";

import { AuthLayout } from "@/components/auth/AuthLayout";
import { MethodTabs } from "@/components/auth/MethodTabs";
import { VerifyEmailForm } from "@/components/auth/VerifyEmailForm";
import { VerifyPhoneForm } from "@/components/auth/VerifyPhoneForm";
import { useVerifyEmailMutation, useVerifyPhoneMutation } from "@/hooks/useAuthMutations";

function VerifyPageContent() {
  const searchParams = useSearchParams();
  const initialToken = searchParams.get("token") ?? "";
  const initialPhone = searchParams.get("phone") ?? "";
  const initialOtp = searchParams.get("otp") ?? "";

  const verifyEmailMutation = useVerifyEmailMutation();
  const verifyPhoneMutation = useVerifyPhoneMutation();

  return (
    <AuthLayout
      title="Verify your account"
      subtitle="Confirm your email or phone to unlock personalized recommendations."
    >
      <MethodTabs
        tabs={[
          { id: "email", label: "Email" },
          { id: "phone", label: "Phone" },
        ]}
      >
        <VerifyEmailForm
          initialToken={initialToken}
          onSubmit={async (token) => {
            const result = await verifyEmailMutation.mutateAsync(token);
            return { message: result.message };
          }}
        />
        <VerifyPhoneForm
          initialPhone={initialPhone}
          initialOtp={initialOtp}
          onSubmit={async (phone, otpCode) => {
            const result = await verifyPhoneMutation.mutateAsync({ phone, otp_code: otpCode });
            return { message: result.message };
          }}
        />
      </MethodTabs>
    </AuthLayout>
  );
}

export function VerifyPageClient() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-cream" />}>
      <VerifyPageContent />
    </Suspense>
  );
}
