"use client";

import Image from "next/image";
import { useEffect, useState } from "react";

type ProductImageProps = {
  src: string | null | undefined;
  alt: string;
  sizes?: string;
  /** Eager-load above-the-fold images (PDP hero / first grid cards). */
  priority?: boolean;
  /** thumb = grid cards; hero = product detail. */
  variant?: "thumb" | "hero";
};

function MissingImagePlaceholder({ alt }: { alt: string }) {
  return (
    <div
      className="absolute inset-0 flex flex-col items-center justify-center gap-2 bg-sand px-4 text-center"
      role="img"
      aria-label={`${alt} — producto sin imagen`}
    >
      <span className="text-[10px] tracking-[0.25em] uppercase text-stone-400">Sin imagen</span>
      <span className="text-xs text-stone-500 font-light leading-snug line-clamp-3">{alt}</span>
    </div>
  );
}

function shouldBypassOptimizer(src: string): boolean {
  // Scraped retailer hosts are often slow through /_next/image (extra hop).
  // Load them directly; keep optimizing Unsplash demos.
  try {
    const host = new URL(src).hostname;
    return host !== "images.unsplash.com" && !host.endsWith(".unsplash.com");
  } catch {
    return true;
  }
}

export function ProductImage({
  src,
  alt,
  sizes = "(max-width: 768px) 50vw, 25vw",
  priority = false,
  variant = "thumb",
}: ProductImageProps) {
  const initial = src?.trim() ? src.trim() : null;
  const [failed, setFailed] = useState(false);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    setFailed(false);
    setLoaded(false);
  }, [initial]);

  if (!initial || failed) {
    return <MissingImagePlaceholder alt={alt} />;
  }

  const quality = variant === "hero" ? 72 : 55;
  const unoptimized = shouldBypassOptimizer(initial);

  return (
    <>
      {!loaded ? (
        <div className="absolute inset-0 bg-sand animate-pulse" aria-hidden="true" />
      ) : null}
      <Image
        src={initial}
        alt={alt}
        fill
        priority={priority}
        quality={quality}
        unoptimized={unoptimized}
        sizes={sizes}
        className={`object-cover transition-all duration-500 group-hover:scale-105 ${
          loaded ? "opacity-100" : "opacity-0"
        }`}
        onLoad={() => setLoaded(true)}
        onError={() => setFailed(true)}
      />
    </>
  );
}
