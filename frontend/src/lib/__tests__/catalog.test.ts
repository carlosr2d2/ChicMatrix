import {
  enqueueScrape,
  fetchProducts,
  fetchRetailers,
  formatPrice,
} from "@/lib/catalog";

describe("catalog API client", () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  it("fetches products", async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ items: [], total: 0 }),
    }) as jest.Mock;

    const result = await fetchProducts("http://api.test");
    expect(result.total).toBe(0);
    expect(global.fetch).toHaveBeenCalledWith(
      "http://api.test/products?limit=24",
      expect.objectContaining({ cache: "no-store" }),
    );
  });

  it("fetches retailers", async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ items: [{ id: 1, name: "Shop", base_url: "x", is_active: true }], total: 1 }),
    }) as jest.Mock;

    const result = await fetchRetailers("http://api.test");
    expect(result.total).toBe(1);
  });

  it("enqueues scrape task via admin BFF", async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ retailer_id: 1, task_id: "t1", status: "enqueued", message: "ok" }),
    }) as jest.Mock;

    const result = await enqueueScrape(1);
    expect(result.status).toBe("enqueued");
    expect(global.fetch).toHaveBeenCalledWith(
      "/api/admin/scrape/1",
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("formats latest price", () => {
    expect(formatPrice({ amount: 289, currency: "USD", scraped_at: "2026-01-01" })).toBe("$289");
    expect(formatPrice(null)).toBe("Price unavailable");
  });
});
