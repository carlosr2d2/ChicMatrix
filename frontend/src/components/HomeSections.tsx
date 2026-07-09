import Image from "next/image";
import Link from "next/link";

import { featuredProducts } from "@/lib/data";

export function Header() {
  return (
    <header className="border-b border-sand/60 bg-white/80 backdrop-blur-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 py-5 flex items-center justify-between">
        <Link href="/" className="font-display text-2xl tracking-[0.2em] uppercase font-light">
          ChicMatrix
        </Link>
        <nav className="hidden md:flex items-center gap-10 text-sm tracking-wide text-stone-600">
          <Link href="#collection" className="hover:text-ink transition-colors">Collection</Link>
          <Link href="#how-it-works" className="hover:text-ink transition-colors">How it works</Link>
          <Link href="#status" className="hover:text-ink transition-colors">Status</Link>
        </nav>
        <button className="btn-primary text-xs">Sign in</button>
      </div>
    </header>
  );
}

export function FeaturedGrid() {
  return (
    <section id="collection" className="bg-white py-24">
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex items-end justify-between mb-14">
          <div>
            <p className="text-sm tracking-[0.3em] uppercase text-stone-500 mb-3">Curated</p>
            <h2 className="section-title">Featured pieces</h2>
          </div>
          <span className="text-sm text-stone-500 hidden md:block">Updated via live scraping</span>
        </div>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 md:gap-8">
          {featuredProducts.map((product) => (
            <article key={product.id} className="group cursor-pointer">
              <div className="relative aspect-[3/4] overflow-hidden bg-sand mb-4">
                <Image
                  src={product.image}
                  alt={product.name}
                  fill
                  className="object-cover transition-transform duration-700 group-hover:scale-105"
                  sizes="(max-width: 768px) 50vw, 25vw"
                />
              </div>
              <p className="text-xs tracking-widest uppercase text-stone-500 mb-1">{product.brand}</p>
              <h3 className="text-sm font-medium mb-1">{product.name}</h3>
              <p className="text-sm text-stone-600">{product.price}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

type StatusBannerProps = {
  health: { status: string } | null;
};

export function StatusBanner({ health }: StatusBannerProps) {
  const isOperational = health?.status === "ok";

  return (
    <section id="status" className="bg-ink text-white py-16">
      <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-6">
        <div>
          <p className="text-xs tracking-[0.3em] uppercase text-stone-400 mb-2">System status</p>
          <p className="text-lg font-light">
            API:{" "}
            <span className={isOperational ? "text-green-400" : "text-amber-400"}>
              {isOperational ? "Operational" : "Connecting..."}
            </span>
          </p>
        </div>
        <p className="text-stone-400 text-sm font-light">
          FastAPI · PostgreSQL · Redis · Celery
        </p>
      </div>
    </section>
  );
}
