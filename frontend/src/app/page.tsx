import Image from "next/image";

import { Header, FeaturedGrid, StatusBanner } from "@/components/HomeSections";
import { getHealth } from "@/lib/api";
import { processSteps } from "@/lib/data";

export default async function Home() {
  const health = await getHealth();

  return (
    <div className="min-h-screen">
      <Header />

      <section className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-6 py-24 md:py-32 grid md:grid-cols-2 gap-16 items-center">
          <div>
            <p className="text-sm tracking-[0.3em] uppercase text-stone-500 mb-6">
              Personal Fashion Intelligence
            </p>
            <h1 className="section-title mb-6 leading-tight">
              Style curated<br />to your silhouette
            </h1>
            <p className="text-stone-600 text-lg leading-relaxed mb-10 max-w-md font-light">
              Discover pieces that match your proportions, lifestyle, and aesthetic —
              with live price comparison across premium retailers.
            </p>
            <div className="flex flex-wrap gap-4">
              <button className="btn-primary">Get recommendations</button>
              <button className="btn-outline">Explore catalog</button>
            </div>
          </div>
          <div className="relative aspect-[4/5] max-h-[600px]">
            <Image
              src="https://images.unsplash.com/photo-1483985988355-763728e1935b?w=900&q=80"
              alt="Fashion editorial"
              fill
              className="object-cover"
              priority
              sizes="(max-width: 768px) 100vw, 50vw"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-ink/20 to-transparent" />
          </div>
        </div>
      </section>

      <FeaturedGrid />

      <section id="how-it-works" className="py-24 border-t border-sand/60">
        <div className="max-w-7xl mx-auto px-6">
          <p className="text-sm tracking-[0.3em] uppercase text-stone-500 mb-3 text-center">Process</p>
          <h2 className="section-title text-center mb-16">How ChicMatrix works</h2>
          <div className="grid md:grid-cols-3 gap-12">
            {processSteps.map((item) => (
              <div key={item.step} className="text-center">
                <span className="text-4xl font-display font-light text-sand block mb-4">{item.step}</span>
                <h3 className="text-lg font-medium mb-3 tracking-wide">{item.title}</h3>
                <p className="text-stone-600 font-light leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <StatusBanner health={health} />

      <footer className="border-t border-sand/60 py-10">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-stone-500">
          <span className="font-display tracking-[0.15em] uppercase">ChicMatrix</span>
          <span>© 2026 ChicMatrix. All rights reserved.</span>
        </div>
      </footer>
    </div>
  );
}
