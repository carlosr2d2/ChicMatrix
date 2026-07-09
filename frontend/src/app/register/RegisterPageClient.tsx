"use client";

import Link from "next/link";
import { useState } from "react";

import { AuthLayout } from "@/components/auth/AuthLayout";
import { EmailRegisterForm } from "@/components/auth/EmailRegisterForm";
import { MethodTabs } from "@/components/auth/MethodTabs";
import { PhoneRegisterForm } from "@/components/auth/PhoneRegisterForm";
import { SocialLoginButtons } from "@/components/auth/SocialLoginButtons";
import { Alert } from "@/components/auth/Alert";
import {
  useRegisterEmailMutation,
  useRegisterPhoneMutation,
  useSocialAuthMutation,
  useLoginMutation,
} from "@/hooks/useAuthMutations";
import { isTokenResponse } from "@/lib/auth";
import { saveSession } from "@/lib/session";
import { useRouter } from "next/navigation";

export function RegisterPageClient() {
  const router = useRouter();
  const [consent, setConsent] = useState(false);
  const [socialError, setSocialError] = useState<string | null>(null);

  const registerEmailMutation = useRegisterEmailMutation();
  const registerPhoneMutation = useRegisterPhoneMutation();
  const socialAuthMutation = useSocialAuthMutation();
  const loginMutation = useLoginMutation();

  const handleSocialRegister = async (provider: "google" | "apple", idToken: string) => {
    setSocialError(null);
    try {
      await socialAuthMutation.mutateAsync({
        provider,
        id_token: idToken,
        consent_accepted: true,
      });
      const loginResult = await loginMutation.mutateAsync({
        method: "social",
        provider,
        id_token: idToken,
      });
      if (isTokenResponse(loginResult)) {
        await saveSession(loginResult);
        router.push("/dashboard");
        router.refresh();
      }
    } catch (error) {
      setSocialError(error instanceof Error ? error.message : "Social registration failed");
    }
  };

  return (
    <AuthLayout
      title="Create your account"
      subtitle="Join ChicMatrix to receive personalized style recommendations."
      footer={
        <p>
          Already have an account?{" "}
          <Link href="/login" className="text-ink underline underline-offset-4">
            Sign in
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
        <EmailRegisterForm
          onSubmit={async (values) => {
            const result = await registerEmailMutation.mutateAsync(values);
            setConsent(values.consent_accepted);
            return result;
          }}
        />
        <PhoneRegisterForm
          onSubmit={async (values) => {
            const result = await registerPhoneMutation.mutateAsync(values);
            setConsent(values.consent_accepted);
            return result;
          }}
        />
        <div className="space-y-4">
          <ConsentNotice consent={consent} onConsentChange={setConsent} />
          <SocialLoginButtons
            mode="register"
            consentAccepted={consent}
            onSuccess={handleSocialRegister}
            isLoading={socialAuthMutation.isPending || loginMutation.isPending}
          />
          {socialError ? <Alert variant="error">{socialError}</Alert> : null}
        </div>
      </MethodTabs>
    </AuthLayout>
  );
}

function ConsentNotice({
  consent,
  onConsentChange,
}: {
  consent: boolean;
  onConsentChange: (value: boolean) => void;
}) {
  return (
    <label className="flex items-start gap-3 text-sm text-stone-600 cursor-pointer">
      <input
        type="checkbox"
        checked={consent}
        onChange={(event) => onConsentChange(event.target.checked)}
        className="mt-1 h-4 w-4 rounded border-sand text-ink focus:ring-ink"
      />
      <span className="font-light leading-relaxed">
        I consent to the processing of my personal data for social account creation.
      </span>
    </label>
  );
}
