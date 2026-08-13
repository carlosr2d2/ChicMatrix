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

export type ImageBackfillResponse = {
  task_id: string;
  status: string;
  message: string;
  pending_estimate: number;
  retailer_id: number | null;
  limit: number;
};

export type FetchProductsParams = {
  limit?: number;
  offset?: number;
  style?: string | null;
  retailerId?: number | null;
};

export const catalogKeys = {
  products: (params: FetchProductsParams = {}) =>
    ["catalog", "products", params] as const,
  product: (id: number) => ["catalog", "product", id] as const,
  retailers: ["catalog", "retailers"] as const,
};

async function parseJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(parseApiError(detail));
  }
  return response.json() as Promise<T>;
}

export async function fetchProducts(
  params: FetchProductsParams = {},
  apiUrl?: string,
): Promise<ProductListResponse> {
  const baseUrl = apiUrl ?? getApiUrl();
  const search = new URLSearchParams();
  search.set("limit", String(params.limit ?? 24));
  search.set("offset", String(params.offset ?? 0));
  if (params.style) search.set("style", params.style);
  if (params.retailerId) search.set("retailer_id", String(params.retailerId));
  const response = await fetch(`${baseUrl}/products?${search.toString()}`, {
    cache: "no-store",
  });
  return parseJson<ProductListResponse>(response);
}

export async function fetchProduct(
  productId: number,
  apiUrl?: string,
): Promise<ProductListItem> {
  const baseUrl = apiUrl ?? getApiUrl();
  const response = await fetch(`${baseUrl}/products/${productId}`, {
    cache: "no-store",
  });
  return parseJson<ProductListItem>(response);
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

export async function enqueueImageBackfill(params?: {
  retailerId?: number;
  limit?: number;
}): Promise<ImageBackfillResponse> {
  const search = new URLSearchParams();
  if (params?.retailerId != null) search.set("retailer_id", String(params.retailerId));
  if (params?.limit != null) search.set("limit", String(params.limit));
  const qs = search.toString();
  const response = await fetch(`/api/admin/images/backfill${qs ? `?${qs}` : ""}`, {
    method: "POST",
  });
  return parseJson<ImageBackfillResponse>(response);
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
