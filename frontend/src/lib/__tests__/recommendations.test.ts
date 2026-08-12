import {
  fetchMyRecommendations,
  formatRecommendationPrice,
} from "@/lib/recommendations";

describe("recommendations helpers", () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  it("fetches recommendations via BFF", async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        user_id: "u1",
        recommendations: [],
      }),
    }) as jest.Mock;

    const result = await fetchMyRecommendations();
    expect(result.recommendations).toEqual([]);
    expect(global.fetch).toHaveBeenCalledWith(
      "/api/recommend/me",
      expect.objectContaining({ cache: "no-store" }),
    );
  });

  it("surfaces API errors", async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: false,
      text: async () => JSON.stringify({ detail: "Not authenticated" }),
    }) as jest.Mock;

    await expect(fetchMyRecommendations()).rejects.toThrow(/Not authenticated/i);
  });

  it("formats best price", () => {
    expect(
      formatRecommendationPrice({
        retailer_id: 1,
        retailer_name: "Maison Noir",
        amount: 289,
        currency: "USD",
        scraped_at: "2026-01-01",
      }),
    ).toBe("$289");
    expect(formatRecommendationPrice(null)).toBe("Price unavailable");
  });
});
