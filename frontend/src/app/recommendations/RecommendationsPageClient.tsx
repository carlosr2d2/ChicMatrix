"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";

import { RecommendationsGrid } from "@/components/RecommendationsGrid";
import { clearSession } from "@/lib/session";

export function RecommendationsPageClient() {
  const router = useRouter();

  const handleLogout = async () => {
    await clearSession();
    router.push("/login");
    router.refresh();
  };

  return (
    <div className="min-h-screen bg-cream">
      <header className="border-b border-sand/60 bg-white/80 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6 py-5 flex items-center justify-between gap-4">
          <Link href="/" className="font-display text-xl tracking-[0.2em] uppercase font-light">
            ChicMatrix
          </Link>
          <div className="flex items-center gap-3">
            <Link href="/profile" className="text-sm text-stone-500 hover:text-ink">
              Profile
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

      <main className="max-w-7xl mx-auto px-6 py-12 animate-slide-up">
        <p className="text-sm tracking-[0.3em] uppercase text-stone-500 mb-3">Recommendations</p>
        <h1 className="section-title mb-4">Styled for your silhouette</h1>
        <p className="text-stone-600 font-light mb-10 max-w-2xl">
          Pieces ranked from your biometrics, preferred colors and brands, and occasions — with
          live price comparison across retailers.
        </p>

        <RecommendationsGrid />
      </main>
    </div>
  );
}
