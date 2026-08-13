"use client";

import { useQuery } from "@tanstack/react-query";

import { Alert } from "@/components/auth/Alert";
import { ProductImage } from "@/components/ProductImage";
import { StyleChips } from "@/components/StyleChips";
import {
  catalogKeys,
  fetchProducts,
  formatPrice,
} from "@/lib/catalog";

function ProductCard({
  name,
  brand,
  imageUrl,
  priceLabel,
  retailerName,
  styleTags,
}: {
  name: string;
  brand: string | null;
  imageUrl: string | null;
  priceLabel: string;
  retailerName: string | null;
  styleTags: Array<{ code: string; label_es: string; score: number }>;
}) {
  return (
    <article className="group">
      <div className="relative aspect-[3/4] overflow-hidden bg-sand mb-4">
        <ProductImage src={imageUrl} alt={name} />
      </div>
      <p className="text-xs tracking-widest uppercase text-stone-500 mb-1">
        {brand ?? retailerName ?? "ChicMatrix"}
      </p>
      <h3 className="text-sm font-medium mb-1">{name}</h3>
      <p className="text-sm text-stone-600 mb-2">{priceLabel}</p>
      <StyleChips
        tags={styleTags.map((tag) => ({
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
  const { data, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: catalogKeys.products,
    queryFn: () => fetchProducts(),
  });

  const products = data?.items ?? [];

  return (
    <section id="collection" className="bg-white py-24">
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-6 mb-14">
          <div>
            <p className="text-sm tracking-[0.3em] uppercase text-stone-500 mb-3">Curated</p>
            <h2 className="section-title">Featured pieces</h2>
            <p className="text-sm text-stone-500 mt-3 font-light">
              Catalog updated by system scrapes · {data?.total ?? 0} items
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

        {isLoading ? <LoadingGrid /> : null}

        {isError ? (
          <Alert variant="error">
            {error instanceof Error ? error.message : "Could not load catalog"}
          </Alert>
        ) : null}

        {!isLoading && !isError && products.length === 0 ? (
          <div className="text-center py-16 animate-fade-in">
            <p className="text-stone-600 font-light">
              No products in the catalog yet. An administrator must run scrapes to populate the
              collection.
            </p>
          </div>
        ) : null}

        {!isLoading && !isError && products.length > 0 ? (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 md:gap-8 animate-fade-in">
            {products.map((product) => (
              <ProductCard
                key={product.id}
                name={product.name}
                brand={product.brand}
                imageUrl={product.image_url}
                priceLabel={formatPrice(product.latest_price)}
                retailerName={product.retailer_name}
                styleTags={product.style_tags ?? []}
              />
            ))}
          </div>
        ) : null}
      </div>
    </section>
  );
}
