"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { Alert } from "@/components/auth/Alert";
import { ProductImage } from "@/components/ProductImage";
import { StyleChips } from "@/components/StyleChips";
import {
  catalogKeys,
  fetchProducts,
  formatPrice,
  type ProductListItem,
} from "@/lib/catalog";
import { STYLE_OPTIONS } from "@/lib/styles";

const PAGE_SIZE = 24;

function ProductCard({
  product,
  priority = false,
}: {
  product: ProductListItem;
  priority?: boolean;
}) {
  return (
    <article className="group">
      <Link href={`/products/${product.id}`} className="block focus:outline-none focus-visible:ring-1 focus-visible:ring-ink">
        <div className="relative aspect-[3/4] overflow-hidden bg-sand mb-4">
          <ProductImage src={product.image_url} alt={product.name} priority={priority} />
        </div>
        <p className="text-xs tracking-widest uppercase text-stone-500 mb-1">
          {product.brand ?? product.retailer_name ?? "ChicMatrix"}
        </p>
        <h3 className="text-sm font-medium mb-1 group-hover:underline underline-offset-4 decoration-stone-300">
          {product.name}
        </h3>
        <p className="text-sm text-stone-600 mb-2">{formatPrice(product.latest_price)}</p>
      </Link>
      <StyleChips
        tags={(product.style_tags ?? []).map((tag) => ({
          code: tag.code,
          label: tag.label_es,
        }))}
      />
    </article>
  );
}

function LoadingGrid() {
  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 md:gap-8" aria-label="Loading catalog">
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

export function CatalogGrid() {
  const [style, setStyle] = useState<string | null>(null);
  const [visibleCount, setVisibleCount] = useState(PAGE_SIZE);

  const queryParams = useMemo(
    () => ({ limit: visibleCount, offset: 0, style }),
    [style, visibleCount],
  );

  const { data, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: catalogKeys.products(queryParams),
    queryFn: () => fetchProducts(queryParams),
  });

  const products = data?.items ?? [];
  const total = data?.total ?? 0;
  const canLoadMore = products.length < total;

  return (
    <section id="collection" className="bg-white py-24">
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-6 mb-10">
          <div>
            <p className="text-sm tracking-[0.3em] uppercase text-stone-500 mb-3">Curated</p>
            <h2 className="section-title">Featured pieces</h2>
            <p className="text-sm text-stone-500 mt-3 font-light">
              Catalog updated by system scrapes · {total} items
              {style ? ` · ${style}` : ""}
            </p>
          </div>
          <button
            type="button"
            className="btn-outline text-xs"
            onClick={() => refetch()}
            disabled={isFetching}
          >
            {isFetching ? "Refreshing…" : "Refresh list"}
          </button>
        </div>

        <div className="flex flex-wrap gap-2 mb-12" role="group" aria-label="Filter by style">
          <button
            type="button"
            className={`text-[10px] tracking-[0.15em] uppercase px-3 py-1.5 border transition-colors ${
              style === null
                ? "border-ink bg-ink text-cream"
                : "border-sand text-stone-600 hover:border-stone-400"
            }`}
            onClick={() => {
              setStyle(null);
              setVisibleCount(PAGE_SIZE);
            }}
          >
            All
          </button>
          {STYLE_OPTIONS.map((option) => (
            <button
              key={option.code}
              type="button"
              className={`text-[10px] tracking-[0.15em] uppercase px-3 py-1.5 border transition-colors ${
                style === option.code
                  ? "border-ink bg-ink text-cream"
                  : "border-sand text-stone-600 hover:border-stone-400"
              }`}
              onClick={() => {
                setStyle(option.code);
                setVisibleCount(PAGE_SIZE);
              }}
            >
              {option.labelEs}
            </button>
          ))}
        </div>

        {isLoading ? <LoadingGrid /> : null}

        {isError ? (
          <Alert variant="error">
            {error instanceof Error ? error.message : "Could not load catalog"}
          </Alert>
        ) : null}

        {!isLoading && !isError && products.length === 0 ? (
          <div className="text-center py-16 animate-fade-in">
            <p className="text-stone-600 font-light">
              {style
                ? "No products match this style yet. Try another filter or run a scrape."
                : "No products in the catalog yet. An administrator must run scrapes to populate the collection."}
            </p>
          </div>
        ) : null}

        {!isLoading && !isError && products.length > 0 ? (
          <>
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 md:gap-8 animate-fade-in">
              {products.map((product, index) => (
                <ProductCard key={product.id} product={product} priority={index < 4} />
              ))}
            </div>
            {canLoadMore ? (
              <div className="mt-12 text-center">
                <button
                  type="button"
                  className="btn-outline text-xs"
                  onClick={() => setVisibleCount((count) => count + PAGE_SIZE)}
                  disabled={isFetching}
                >
                  {isFetching ? "Loading…" : "Load more"}
                </button>
              </div>
            ) : null}
          </>
        ) : null}
      </div>
    </section>
  );
}
