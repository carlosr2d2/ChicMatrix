export type FeaturedProduct = {
  id: number;
  name: string;
  brand: string;
  price: string;
  image: string;
};

export const featuredProducts: FeaturedProduct[] = [
  {
    id: 1,
    name: "Structured Wool Blazer",
    brand: "Maison Noir",
    price: "$289",
    image: "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=800&q=80",
  },
  {
    id: 2,
    name: "Silk Midi Dress",
    brand: "Maison Noir",
    price: "$420",
    image: "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=800&q=80",
  },
  {
    id: 3,
    name: "Minimalist Wool Coat",
    brand: "Urban Loom",
    price: "$345",
    image: "https://images.unsplash.com/photo-1539533018447-63fcce2678e3?w=800&q=80",
  },
  {
    id: 4,
    name: "Cashmere Crewneck",
    brand: "Urban Loom",
    price: "$198",
    image: "https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=800&q=80",
  },
];

export const processSteps = [
  {
    step: "01",
    title: "Profile",
    desc: "Share your biometrics, style preferences, and lifestyle habits.",
  },
  {
    step: "02",
    title: "Scrape",
    desc: "Workers monitor retailer catalogs and track price history in real time.",
  },
  {
    step: "03",
    title: "Recommend",
    desc: "Our engine surfaces pieces that fit your body and budget.",
  },
];
