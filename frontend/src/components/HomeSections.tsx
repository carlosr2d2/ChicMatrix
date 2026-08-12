import Link from "next/link";

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
        <Link href="/login" className="btn-primary text-xs">
          Sign in
        </Link>
      </div>
    </header>
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
