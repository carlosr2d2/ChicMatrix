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
    ],
  },
};

module.exports = nextConfig;
