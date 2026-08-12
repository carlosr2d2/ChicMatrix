"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { Alert } from "@/components/auth/Alert";
import { Spinner } from "@/components/auth/Spinner";
import { ProfileForm } from "@/components/profile/ProfileForm";
import { authKeys } from "@/lib/query-keys";
import {
  fetchFashionProfile,
  isProfileComplete,
  updateFashionProfile,
} from "@/lib/profile";
import { clearSession } from "@/lib/session";

const profileKeys = {
  me: ["profile", "me"] as const,
};

export function ProfilePageClient() {
  const router = useRouter();
  const queryClient = useQueryClient();

  const {
    data: profile,
    isLoading,
    error,
  } = useQuery({
    queryKey: profileKeys.me,
    queryFn: fetchFashionProfile,
  });

  const saveMutation = useMutation({
    mutationFn: updateFashionProfile,
    onSuccess: (updated) => {
      queryClient.setQueryData(profileKeys.me, updated);
      queryClient.invalidateQueries({ queryKey: authKeys.me });
    },
  });

  const handleLogout = async () => {
    await clearSession();
    router.push("/login");
    router.refresh();
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-cream">
        <Spinner label="Loading profile…" />
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-cream px-6">
        <div className="max-w-md w-full space-y-4">
          <Alert variant="error">
            {error instanceof Error ? error.message : "Could not load profile"}
          </Alert>
          <Link href="/login?next=/profile" className="btn-primary inline-flex">
            Sign in
          </Link>
        </div>
      </div>
    );
  }

  const complete = isProfileComplete(profile);

  return (
    <div className="min-h-screen bg-cream">
      <header className="border-b border-sand/60 bg-white/80 backdrop-blur-sm">
        <div className="max-w-3xl mx-auto px-6 py-5 flex items-center justify-between gap-4">
          <Link href="/" className="font-display text-xl tracking-[0.2em] uppercase font-light">
            ChicMatrix
          </Link>
          <div className="flex items-center gap-3">
            <Link href="/recommendations" className="text-sm text-stone-500 hover:text-ink">
              Recommendations
            </Link>
            <Link href="/dashboard" className="text-sm text-stone-500 hover:text-ink">
              Dashboard
            </Link>
            <button type="button" onClick={handleLogout} className="btn-outline text-xs">
              Sign out
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-6 py-12 animate-slide-up">
        <p className="text-sm tracking-[0.3em] uppercase text-stone-500 mb-3">Fashion profile</p>
        <h1 className="section-title mb-4">Your silhouette & style</h1>
        <p className="text-stone-600 font-light mb-6 max-w-2xl">
          Biometrics, preferred colors/brands, and occasions feed the recommendation engine.
        </p>

        <div className="mb-8">
          <Alert variant={complete ? "success" : "info"}>
            {complete
              ? "Profile looks complete. You can refine it anytime."
              : "Add height, weight, colors or brands, and occasions for better matches."}
          </Alert>
        </div>

        <ProfileForm
          profile={profile}
          onSave={async (payload) => saveMutation.mutateAsync(payload)}
        />

        <div className="mt-8">
          <Link href="/recommendations" className="btn-outline inline-flex text-xs">
            View recommendations
          </Link>
        </div>
      </main>
    </div>
  );
}
