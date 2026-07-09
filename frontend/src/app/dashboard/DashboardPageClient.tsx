"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { Alert } from "@/components/auth/Alert";
import { Spinner } from "@/components/auth/Spinner";
import { authKeys } from "@/lib/query-keys";
import { clearSession, fetchCurrentUser } from "@/lib/session";

export function DashboardPageClient() {
  const router = useRouter();
  const { data: user, isLoading, error } = useQuery({
    queryKey: authKeys.me,
    queryFn: fetchCurrentUser,
  });

  const handleLogout = async () => {
    await clearSession();
    router.push("/login");
    router.refresh();
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-cream">
        <Spinner label="Loading your profile..." />
      </div>
    );
  }

  if (error || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-cream px-6">
        <div className="max-w-md w-full space-y-4">
          <Alert variant="error">
            {error instanceof Error ? error.message : "Could not load your profile"}
          </Alert>
          <Link href="/login" className="btn-primary inline-flex">
            Sign in
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-cream">
      <header className="border-b border-sand/60 bg-white/80 backdrop-blur-sm">
        <div className="max-w-5xl mx-auto px-6 py-5 flex items-center justify-between gap-4">
          <Link href="/" className="font-display text-xl tracking-[0.2em] uppercase font-light">
            ChicMatrix
          </Link>
          <button type="button" onClick={handleLogout} className="btn-outline text-xs">
            Sign out
          </button>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-12 animate-slide-up">
        <p className="text-sm tracking-[0.3em] uppercase text-stone-500 mb-3">Dashboard</p>
        <h1 className="section-title mb-4">
          Hello{user.name ? `, ${user.name}` : ""}
        </h1>
        <p className="text-stone-600 font-light mb-10 max-w-2xl">
          Your account is verified and ready. Explore curated recommendations tailored to your
          profile and live price comparisons across premium retailers.
        </p>

        <div className="grid md:grid-cols-2 gap-6">
          <section className="bg-white border border-sand/80 p-6">
            <h2 className="text-sm tracking-[0.2em] uppercase text-stone-500 mb-4">Account</h2>
            <dl className="space-y-3 text-sm">
              <div>
                <dt className="text-stone-500">Email</dt>
                <dd>{user.email ?? "—"}</dd>
              </div>
              <div>
                <dt className="text-stone-500">Phone</dt>
                <dd>{user.phone ?? "—"}</dd>
              </div>
              <div>
                <dt className="text-stone-500">Role</dt>
                <dd className="capitalize">{user.role}</dd>
              </div>
              <div>
                <dt className="text-stone-500">Status</dt>
                <dd>{user.verified ? "Verified" : "Pending verification"}</dd>
              </div>
            </dl>
          </section>

          <section className="bg-white border border-sand/80 p-6">
            <h2 className="text-sm tracking-[0.2em] uppercase text-stone-500 mb-4">Next steps</h2>
            <ul className="space-y-3 text-sm text-stone-600 font-light">
              <li>Complete your fashion profile for better recommendations.</li>
              <li>Browse the curated collection on the homepage.</li>
              <li>Track live prices from connected retailers.</li>
            </ul>
            <Link href="/" className="btn-primary inline-flex mt-6 text-xs">
              Explore collection
            </Link>
          </section>
        </div>
      </main>
    </div>
  );
}
