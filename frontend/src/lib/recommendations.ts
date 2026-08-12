import { parseApiError } from "@/lib/errors";

export type RecommendationProduct = {
  id: number;
  name: string;
  description: string | null;
  image_url: string | null;
  category: string | null;
  brand: string | null;
  color: string | null;
  retailer_id: number;
};

export type PriceComparison = {
  retailer_id: number;
  retailer_name: string;
  amount: number;
  currency: string;
  scraped_at: string;
};

export type RecommendationItem = {
  product: RecommendationProduct;
  score: number;
  reasons: string[];
  prices: PriceComparison[];
  best_price: PriceComparison | null;
};

export type RecommendationResponse = {
  user_id: string;
  recommendations: RecommendationItem[];
};

export const recommendationKeys = {
  me: ["recommendations", "me"] as const,
};

export async function fetchMyRecommendations(): Promise<RecommendationResponse> {
  const response = await fetch("/api/recommend/me", { cache: "no-store" });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(parseApiError(detail));
  }
  return response.json() as Promise<RecommendationResponse>;
}

export function formatRecommendationPrice(price: PriceComparison | null): string {
  if (!price) return "Price unavailable";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: price.currency,
    maximumFractionDigits: 0,
  }).format(price.amount);
}
