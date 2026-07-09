import Image from "next/image";
import Link from "next/link";

type AuthLayoutProps = {
  title: string;
  subtitle: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
};

export function AuthLayout({ title, subtitle, children, footer }: AuthLayoutProps) {
  return (
    <div className="min-h-screen grid lg:grid-cols-2">
      <div className="relative hidden lg:block">
        <Image
          src="https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=1200&q=80"
          alt="Fashion editorial"
          fill
          className="object-cover"
          priority
          sizes="50vw"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-ink/50 via-ink/20 to-transparent" />
        <div className="absolute bottom-12 left-12 right-12 text-white">
          <p className="text-xs tracking-[0.35em] uppercase text-white/70 mb-4">ChicMatrix</p>
          <h2 className="font-display text-4xl font-light leading-tight">
            Curated style,<br />tailored to you
          </h2>
        </div>
      </div>

      <div className="flex flex-col min-h-screen bg-cream">
        <header className="px-6 py-6 flex items-center justify-between">
          <Link href="/" className="font-display text-xl tracking-[0.2em] uppercase font-light">
            ChicMatrix
          </Link>
          <Link href="/" className="text-sm text-stone-500 hover:text-ink transition-colors">
            Back to home
          </Link>
        </header>

        <main className="flex-1 flex items-center justify-center px-6 py-8">
          <div className="w-full max-w-md animate-slide-up">
            <div className="mb-8">
              <h1 className="section-title text-3xl mb-3">{title}</h1>
              <p className="text-stone-600 font-light">{subtitle}</p>
            </div>
            {children}
          </div>
        </main>

        {footer ? (
          <footer className="px-6 py-6 text-center text-sm text-stone-500">{footer}</footer>
        ) : null}
      </div>
    </div>
  );
}
