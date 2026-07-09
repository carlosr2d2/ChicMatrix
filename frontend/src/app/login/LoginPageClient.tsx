"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";

import { AuthLayout } from "@/components/auth/AuthLayout";
import { EmailLoginForm } from "@/components/auth/EmailLoginForm";
import { MethodTabs } from "@/components/auth/MethodTabs";
import { PhoneLoginForm } from "@/components/auth/PhoneLoginForm";
import { SocialLoginButtons } from "@/components/auth/SocialLoginButtons";
import { Alert } from "@/components/auth/Alert";
import { useLoginMutation } from "@/hooks/useAuthMutations";
import { isTokenResponse } from "@/lib/auth";
import { saveSession } from "@/lib/session";

export function LoginPageClient() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const nextPath = searchParams.get("next") || "/dashboard";
  const [socialError, setSocialError] = useState<string | null>(null);
  const loginMutation = useLoginMutation();

  const completeLogin = async (tokens: {
    access_token: string;
    refresh_token: string;
    expires_in: number;
    user_id: string;
    token_type?: string;
    role?: string;
    permissions?: string[];
  }) => {
    await saveSession(tokens);
    router.push(nextPath);
    router.refresh();
  };

  return (
    <AuthLayout
      title="Welcome back"
      subtitle="Sign in to access your personalized fashion dashboard."
      footer={
        <p>
          New to ChicMatrix?{" "}
          <Link href="/register" className="text-ink underline underline-offset-4">
            Create an account
          </Link>
        </p>
      }
    >
      <MethodTabs
        tabs={[
          { id: "email", label: "Email" },
          { id: "phone", label: "Phone" },
          { id: "social", label: "Social" },
        ]}
      >
        <EmailLoginForm
          onSubmit={async (values) => {
            const result = await loginMutation.mutateAsync({
              method: "email",
              ...values,
            });
            if (!isTokenResponse(result)) {
              throw new Error("Unexpected login response");
            }
            await completeLogin(result);
          }}
        />
        <PhoneLoginForm
          onRequestOtp={async (phone) => {
            const result = await loginMutation.mutateAsync({ method: "phone", phone });
            if (isTokenResponse(result)) {
              throw new Error("Unexpected token response before OTP");
            }
            return result;
          }}
          onSubmitOtp={async (phone, otpCode) => {
            const result = await loginMutation.mutateAsync({
              method: "phone",
              phone,
              otp_code: otpCode,
            });
            if (!isTokenResponse(result)) {
              throw new Error("Invalid OTP or login failed");
            }
            await completeLogin(result);
          }}
        />
        <div className="space-y-4">
          <SocialLoginButtons
            mode="login"
            consentAccepted
            isLoading={loginMutation.isPending}
            onSuccess={async (provider, idToken) => {
              setSocialError(null);
              try {
                const result = await loginMutation.mutateAsync({
                  method: "social",
                  provider,
                  id_token: idToken,
                });
                if (!isTokenResponse(result)) {
                  throw new Error("Social login failed");
                }
                await completeLogin(result);
              } catch (error) {
                setSocialError(error instanceof Error ? error.message : "Social login failed");
              }
            }}
          />
          {socialError ? <Alert variant="error">{socialError}</Alert> : null}
        </div>
      </MethodTabs>
    </AuthLayout>
  );
}
