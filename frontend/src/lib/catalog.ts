import { getApiUrl } from "@/lib/config";
import { parseApiError } from "@/lib/errors";

export type LatestPrice = {
  amount: number;
  currency: string;
  scraped_at: string;
};

export type ProductListItem = {
  id: number;
  name: string;
  description: string | null;
  image_url: string | null;
  product_url?: string | null;
  category: string | null;
  brand: string | null;
  color: string | null;
  retailer_id: number;
  retailer_name: string | null;
  latest_price: LatestPrice | null;
  style_tags?: Array<{
    code: string;
    label_es: string;
    score: number;
    model_version: string;
  }>;
};

export type ProductListResponse = {
  items: ProductListItem[];
  total: number;
};

export type Retailer = {
  id: number;
  name: string;
  base_url: string;
  is_active: boolean;
};

export type RetailerListResponse = {
  items: Retailer[];
  total: number;
};

export type ScrapeResponse = {
  retailer_id: number;
  task_id: string;
  status: string;
  message: string;
};

export const catalogKeys = {
  products: ["catalog", "products"] as const,
  retailers: ["catalog", "retailers"] as const,
};

async function parseJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(parseApiError(detail));
  }
  return response.json() as Promise<T>;
}

export async function fetchProducts(apiUrl?: string): Promise<ProductListResponse> {
  const baseUrl = apiUrl ?? getApiUrl();
  const response = await fetch(`${baseUrl}/products?limit=24`, { cache: "no-store" });
  return parseJson<ProductListResponse>(response);
}

export async function fetchRetailers(apiUrl?: string): Promise<RetailerListResponse> {
  const baseUrl = apiUrl ?? getApiUrl();
  const response = await fetch(`${baseUrl}/retailers`, { cache: "no-store" });
  return parseJson<RetailerListResponse>(response);
}

export async function enqueueScrape(retailerId: number): Promise<ScrapeResponse> {
  const response = await fetch(`/api/admin/scrape/${retailerId}`, { method: "POST" });
  return parseJson<ScrapeResponse>(response);
}

export function formatPrice(latest: LatestPrice | null): string {
  if (!latest) return "Price unavailable";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: latest.currency,
    maximumFractionDigits: 0,
  }).format(latest.amount);
}

export const PLACEHOLDER_IMAGE =
  "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=800&q=80";
