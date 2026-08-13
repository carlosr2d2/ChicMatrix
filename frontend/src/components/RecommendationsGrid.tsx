"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";

import { Alert } from "@/components/auth/Alert";
import { ProductImage } from "@/components/ProductImage";
import { StyleChips } from "@/components/StyleChips";
import {
  formatRecommendationPrice,
  fetchMyRecommendations,
  recommendationKeys,
  type RecommendationItem,
} from "@/lib/recommendations";

function RecommendationCard({ item }: { item: RecommendationItem }) {
  const { product, score, reasons, best_price, prices } = item;
  const otherPrices = prices.filter((p) => p.retailer_id !== best_price?.retailer_id);

  return (
    <article className="group">
      <div className="relative aspect-[3/4] overflow-hidden bg-sand mb-4">
        <ProductImage src={product.image_url} alt={product.name} />
      </div>
      <div className="flex items-baseline justify-between gap-2 mb-1">
        <p className="text-xs tracking-widest uppercase text-stone-500">
          {product.brand ?? "ChicMatrix"}
        </p>
        <p className="text-xs text-stone-400 tabular-nums">Match {score.toFixed(1)}</p>
      </div>
      <h3 className="text-sm font-medium mb-1">{product.name}</h3>
      <p className="text-sm text-stone-600 mb-2">{formatRecommendationPrice(best_price)}</p>
      <StyleChips
        className="mb-2"
        tags={(product.style_tags ?? []).map((tag) => ({
          code: tag.code,
          label: tag.label_es,
          score: tag.score,
        }))}
      />
      {best_price ? (
        <p className="text-xs text-stone-500 mb-2">Best at {best_price.retailer_name}</p>
      ) : null}
      {reasons.length > 0 ? (
        <ul className="space-y-1 mb-2">
          {reasons.slice(0, 2).map((reason) => (
            <li key={reason} className="text-xs text-stone-500 font-light leading-snug">
              {reason}
            </li>
          ))}
        </ul>
      ) : null}
      {otherPrices.length > 0 ? (
        <p className="text-xs text-stone-400 font-light">
          Also {otherPrices.length} other retailer{otherPrices.length === 1 ? "" : "s"}
        </p>
      ) : null}
    </article>
  );
}

function LoadingGrid() {
  return (
    <div
      className="grid grid-cols-2 lg:grid-cols-4 gap-6 md:gap-8"
      aria-label="Loading recommendations"
    >
      {Array.from({ length: 4 }).map((_, index) => (
        <div key={index} className="animate-pulse">
          <div className="aspect-[3/4] bg-sand mb-4" />
          <div className="h-3 bg-sand w-1/2 mb-2" />
          <div className="h-4 bg-sand w-3/4 mb-2" />
          <div className="h-3 bg-sand w-1/3" />
        </div>
      ))}
    </div>
  );
}

export function RecommendationsGrid() {
  const { data, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: recommendationKeys.me,
    queryFn: fetchMyRecommendations,
  });

  const items = data?.recommendations ?? [];

  return (
    <section>
      <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-6 mb-10">
        <div>
          <p className="text-sm tracking-[0.3em] uppercase text-stone-500 mb-3">For you</p>
          <h2 className="section-title">Personalized picks</h2>
          <p className="text-sm text-stone-500 mt-3 font-light">
            Ranked by your profile · {items.length} piece{items.length === 1 ? "" : "s"}
          </p>
        </div>
        <button
          type="button"
          className="btn-outline text-xs"
          onClick={() => refetch()}
          disabled={isFetching}
        >
          {isFetching ? "Refreshing…" : "Refresh picks"}
        </button>
      </div>

      {isLoading ? <LoadingGrid /> : null}

      {isError ? (
        <Alert variant="error">
          {error instanceof Error ? error.message : "Could not load recommendations"}
        </Alert>
      ) : null}

      {!isLoading && !isError && items.length === 0 ? (
        <div className="py-12 animate-fade-in space-y-4">
          <Alert variant="info">
            No matches yet. Complete your fashion profile and wait for an admin to populate the
            catalog.
          </Alert>
          <div className="flex flex-wrap gap-3">
            <Link href="/profile" className="btn-primary inline-flex text-xs">
              Edit fashion profile
            </Link>
            <Link href="/#collection" className="btn-outline inline-flex text-xs">
              Browse collection
            </Link>
          </div>
        </div>
      ) : null}

      {!isLoading && !isError && items.length > 0 ? (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 md:gap-8 animate-fade-in">
          {items.map((item) => (
            <RecommendationCard key={item.product.id} item={item} />
          ))}
        </div>
      ) : null}
    </section>
  );
}
