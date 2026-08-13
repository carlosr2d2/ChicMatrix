"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";

import { Alert } from "@/components/auth/Alert";
import { ProductImage } from "@/components/ProductImage";
import { StyleChips } from "@/components/StyleChips";
import { catalogKeys, fetchProduct, formatPrice } from "@/lib/catalog";

type ProductPageClientProps = {
  productId: number;
};

export function ProductPageClient({ productId }: ProductPageClientProps) {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: catalogKeys.product(productId),
    queryFn: () => fetchProduct(productId),
    enabled: Number.isFinite(productId) && productId > 0,
  });

  return (
    <main className="min-h-screen bg-cream">
      <div className="max-w-6xl mx-auto px-6 py-16 md:py-24">
        <Link
          href="/#collection"
          className="text-xs tracking-[0.2em] uppercase text-stone-500 hover:text-ink transition-colors"
        >
          ← Back to collection
        </Link>

        {!Number.isFinite(productId) || productId <= 0 ? (
          <div className="mt-10">
            <Alert variant="error">Invalid product</Alert>
          </div>
        ) : null}

        {isLoading ? (
          <div className="mt-12 grid md:grid-cols-2 gap-10 animate-pulse" aria-label="Loading product">
            <div className="aspect-[3/4] bg-sand" />
            <div className="space-y-4 pt-4">
              <div className="h-3 bg-sand w-1/3" />
              <div className="h-8 bg-sand w-2/3" />
              <div className="h-4 bg-sand w-1/4" />
              <div className="h-20 bg-sand w-full" />
            </div>
          </div>
        ) : null}

        {isError ? (
          <div className="mt-10">
            <Alert variant="error">
              {error instanceof Error ? error.message : "Could not load product"}
            </Alert>
          </div>
        ) : null}

        {data ? (
          <div className="mt-12 grid md:grid-cols-2 gap-10 md:gap-16 animate-fade-in">
            <div className="relative aspect-[3/4] overflow-hidden bg-sand">
              <ProductImage src={data.image_url} alt={data.name} sizes="(max-width: 768px) 100vw, 50vw" />
            </div>
            <div>
              <p className="text-xs tracking-[0.25em] uppercase text-stone-500 mb-3">
                {data.brand ?? data.retailer_name ?? "ChicMatrix"}
              </p>
              <h1 className="font-display text-3xl md:text-4xl text-ink mb-4">{data.name}</h1>
              <p className="text-lg text-stone-700 mb-6">{formatPrice(data.latest_price)}</p>
              <StyleChips
                className="mb-8"
                tags={(data.style_tags ?? []).map((tag) => ({
                  code: tag.code,
                  label: tag.label_es,
                  score: tag.score,
                }))}
              />
              <dl className="space-y-3 text-sm text-stone-600 mb-8">
                {data.retailer_name ? (
                  <div className="flex gap-3">
                    <dt className="w-24 uppercase tracking-wider text-[10px] text-stone-400 pt-0.5">
                      Retailer
                    </dt>
                    <dd>{data.retailer_name}</dd>
                  </div>
                ) : null}
                {data.category ? (
                  <div className="flex gap-3">
                    <dt className="w-24 uppercase tracking-wider text-[10px] text-stone-400 pt-0.5">
                      Category
                    </dt>
                    <dd>{data.category}</dd>
                  </div>
                ) : null}
                {data.color ? (
                  <div className="flex gap-3">
                    <dt className="w-24 uppercase tracking-wider text-[10px] text-stone-400 pt-0.5">
                      Color
                    </dt>
                    <dd className="capitalize">{data.color}</dd>
                  </div>
                ) : null}
              </dl>
              {data.description ? (
                <p className="text-sm text-stone-600 font-light leading-relaxed mb-10">
                  {data.description}
                </p>
              ) : (
                <p className="text-sm text-stone-500 font-light mb-10">
                  No description available for this piece yet.
                </p>
              )}
              <div className="flex flex-wrap gap-3">
                {data.product_url ? (
                  <a
                    href={data.product_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-outline text-xs"
                  >
                    View at retailer
                  </a>
                ) : null}
                <Link href="/recommendations" className="btn-outline text-xs">
                  See recommendations
                </Link>
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </main>
  );
}
