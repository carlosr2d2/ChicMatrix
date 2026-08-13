"use client";

import Image from "next/image";
import { useState } from "react";

type ProductImageProps = {
  src: string | null | undefined;
  alt: string;
  sizes?: string;
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

export function ProductImage({ src, alt, sizes = "(max-width: 768px) 50vw, 25vw" }: ProductImageProps) {
  const initial = src?.trim() ? src.trim() : null;
  const [failed, setFailed] = useState(false);

  if (!initial || failed) {
    return <MissingImagePlaceholder alt={alt} />;
  }

  return (
    <Image
      src={initial}
      alt={alt}
      fill
      className="object-cover transition-transform duration-700 group-hover:scale-105"
      sizes={sizes}
      onError={() => setFailed(true)}
    />
  );
}
