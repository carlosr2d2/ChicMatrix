import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        ink: "#1a1a1a",
        stone: {
          DEFAULT: "#8a8580",
          400: "#a8a39e",
          500: "#8a8580",
          600: "#6b6661",
          800: "#3d3a37",
        },
        sand: "#e8e4df",
        cream: "#f7f5f2",
      },
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
        display: ["var(--font-lato)", "Georgia", "serif"],
      },
    },
  },
  plugins: [],
};

export default config;
