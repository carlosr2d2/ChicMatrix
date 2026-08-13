/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
  images: {
    // Scraped retailer CDNs vary; allow any https host for product imagery.
    remotePatterns: [
      { protocol: "https", hostname: "images.unsplash.com" },
      { protocol: "https", hostname: "automationexercise.com" },
      { protocol: "https", hostname: "**.automationexercise.com" },
      { protocol: "https", hostname: "**" },
      // Local API media cache (product images on disk)
      { protocol: "http", hostname: "localhost", port: "8001" },
      { protocol: "http", hostname: "127.0.0.1", port: "8001" },
    ],
    formats: ["image/avif", "image/webp"],
    minimumCacheTTL: 60 * 60 * 24,
    deviceSizes: [640, 750, 828, 1080, 1200],
    imageSizes: [96, 128, 256, 384],
  },
};

module.exports = nextConfig;
