"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { Alert } from "@/components/auth/Alert";
import { Spinner } from "@/components/auth/Spinner";
import { catalogKeys, enqueueImageBackfill, enqueueScrape, fetchRetailers } from "@/lib/catalog";
import { authKeys } from "@/lib/query-keys";
import { clearSession, fetchCurrentUser } from "@/lib/session";

export function AdminPageClient() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const {
    data: user,
    isLoading: userLoading,
    error: userError,
  } = useQuery({
    queryKey: authKeys.me,
    queryFn: fetchCurrentUser,
  });

  const {
    data: retailers,
    isLoading: retailersLoading,
    error: retailersError,
  } = useQuery({
    queryKey: catalogKeys.retailers,
    queryFn: () => fetchRetailers(),
    enabled: user?.role === "admin",
  });

  const scrapeOne = useMutation({
    mutationFn: (retailerId: number) => enqueueScrape(retailerId),
    onSuccess: (result) => {
      setError(null);
      setMessage(result.message);
      queryClient.invalidateQueries({ queryKey: catalogKeys.products });
    },
    onError: (err) => {
      setMessage(null);
      setError(err instanceof Error ? err.message : "Could not enqueue scrape");
    },
  });

  const scrapeAll = useMutation({
    mutationFn: async () => {
      const items = retailers?.items ?? [];
      if (items.length === 0) {
        throw new Error("No active retailers configured");
      }
      return Promise.all(items.map((retailer) => enqueueScrape(retailer.id)));
    },
    onSuccess: (results) => {
      setError(null);
      setMessage(`Queued scrapes for ${results.length} retailer(s). Workers will update the catalog.`);
      queryClient.invalidateQueries({ queryKey: catalogKeys.products });
    },
    onError: (err) => {
      setMessage(null);
      setError(err instanceof Error ? err.message : "Could not enqueue scrapes");
    },
  });

  const backfillImages = useMutation({
    mutationFn: () => enqueueImageBackfill({ limit: 500 }),
    onSuccess: (result) => {
      setError(null);
      setMessage(result.message);
      queryClient.invalidateQueries({ queryKey: catalogKeys.products });
    },
    onError: (err) => {
      setMessage(null);
      setError(err instanceof Error ? err.message : "Could not enqueue image backfill");
    },
  });

  const handleLogout = async () => {
    await clearSession();
    router.push("/login");
    router.refresh();
  };

  if (userLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-cream">
        <Spinner label="Loading admin…" />
      </div>
    );
  }

  if (userError || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-cream px-6">
        <div className="max-w-md w-full space-y-4">
          <Alert variant="error">
            {userError instanceof Error ? userError.message : "Not authenticated"}
          </Alert>
          <Link href="/login?next=/admin" className="btn-primary inline-flex">
            Sign in
          </Link>
        </div>
      </div>
    );
  }

  if (user.role !== "admin") {
    return (
      <div className="min-h-screen flex items-center justify-center bg-cream px-6">
        <div className="max-w-md w-full space-y-4">
          <Alert variant="error">Admin role required to manage scrapes.</Alert>
          <Link href="/dashboard" className="btn-outline inline-flex">
            Back to dashboard
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
          <div className="flex items-center gap-3">
            <Link href="/dashboard" className="text-sm text-stone-500 hover:text-ink">
              Dashboard
            </Link>
            <button type="button" onClick={handleLogout} className="btn-outline text-xs">
              Sign out
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-12 animate-slide-up">
        <p className="text-sm tracking-[0.3em] uppercase text-stone-500 mb-3">Administration</p>
        <h1 className="section-title mb-4">Catalog scrapes</h1>
        <p className="text-stone-600 font-light mb-10 max-w-2xl">
          Only system administrators can enqueue scrape jobs. Workers process them asynchronously
          and update products and prices for all customers. Use image backfill to cache remote
          product photos locally without re-scraping listings. Celery Beat also runs daily scrapes
          and image backfill on a UTC schedule (see README).
        </p>

        <div className="flex flex-wrap gap-3 mb-8">
          <button
            type="button"
            className="btn-primary text-xs"
            onClick={() => scrapeAll.mutate()}
            disabled={scrapeAll.isPending || retailersLoading}
          >
            {scrapeAll.isPending ? (
              <Spinner label="Queuing…" className="text-white" />
            ) : (
              "Scrape all retailers"
            )}
          </button>
          <button
            type="button"
            className="btn-outline text-xs"
            onClick={() => backfillImages.mutate()}
            disabled={backfillImages.isPending}
          >
            {backfillImages.isPending ? (
              <Spinner label="Queuing…" />
            ) : (
              "Backfill product images"
            )}
          </button>
          <Link href="/#collection" className="btn-outline text-xs">
            View public catalog
          </Link>
        </div>

        {message ? <div className="mb-6"><Alert variant="success">{message}</Alert></div> : null}
        {error ? <div className="mb-6"><Alert variant="error">{error}</Alert></div> : null}
        {retailersError ? (
          <div className="mb-6">
            <Alert variant="error">
              {retailersError instanceof Error
                ? retailersError.message
                : "Could not load retailers"}
            </Alert>
          </div>
        ) : null}

        {retailersLoading ? <Spinner label="Loading retailers…" /> : null}

        {!retailersLoading && retailers ? (
          <div className="space-y-3">
            {retailers.items.map((retailer) => (
              <div
                key={retailer.id}
                className="bg-white border border-sand/80 px-5 py-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4"
              >
                <div>
                  <p className="font-medium">{retailer.name}</p>
                  <p className="text-sm text-stone-500 font-light">{retailer.base_url}</p>
                </div>
                <button
                  type="button"
                  className="btn-outline text-xs"
                  onClick={() => scrapeOne.mutate(retailer.id)}
                  disabled={scrapeOne.isPending}
                >
                  Enqueue scrape
                </button>
              </div>
            ))}
          </div>
        ) : null}
      </main>
    </div>
  );
}
