import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";

import { RecommendationsGrid } from "@/components/RecommendationsGrid";

const sampleResponse = {
  user_id: "user-1",
  recommendations: [
    {
      product: {
        id: 1,
        name: "Linen Shirt",
        description: null,
        image_url: "https://images.unsplash.com/photo-1.jpg",
        category: "office",
        brand: "Urban Loom",
        color: "beige",
        retailer_id: 1,
      },
      score: 4.5,
      reasons: ["Preferred brand: Urban Loom", "Matches preferred color: beige"],
      prices: [
        {
          retailer_id: 1,
          retailer_name: "Urban Loom",
          amount: 120,
          currency: "USD",
          scraped_at: "2026-01-01T00:00:00Z",
        },
      ],
      best_price: {
        retailer_id: 1,
        retailer_name: "Urban Loom",
        amount: 120,
        currency: "USD",
        scraped_at: "2026-01-01T00:00:00Z",
      },
    },
  ],
};

function renderWithQuery(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(<QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>);
}

describe("RecommendationsGrid", () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  it("renders personalized picks from API", async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => sampleResponse,
    }) as jest.Mock;

    renderWithQuery(<RecommendationsGrid />);

    expect(await screen.findByText("Linen Shirt")).toBeInTheDocument();
    expect(screen.getByText("$120")).toBeInTheDocument();
    expect(screen.getByText(/Best at Urban Loom/i)).toBeInTheDocument();
    expect(screen.getByText(/Preferred brand: Urban Loom/i)).toBeInTheDocument();
    expect(screen.getByText(/Match 4.5/i)).toBeInTheDocument();
  });

  it("falls back to retailer name when brand is missing", async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        user_id: "user-1",
        recommendations: [
          {
            ...sampleResponse.recommendations[0],
            product: {
              ...sampleResponse.recommendations[0].product,
              brand: null,
            },
            best_price: {
              retailer_id: 4,
              retailer_name: "Practice Boutique",
              amount: 500,
              currency: "INR",
              scraped_at: "2026-01-01T00:00:00Z",
            },
          },
        ],
      }),
    }) as jest.Mock;

    renderWithQuery(<RecommendationsGrid />);

    expect(await screen.findByText("Linen Shirt")).toBeInTheDocument();
    expect(screen.getByText("Practice Boutique")).toBeInTheDocument();
  });

  it("shows empty guidance when there are no matches", async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ user_id: "user-1", recommendations: [] }),
    }) as jest.Mock;

    renderWithQuery(<RecommendationsGrid />);

    expect(await screen.findByText(/No matches yet/i)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Edit fashion profile/i })).toHaveAttribute(
      "href",
      "/profile",
    );
  });
});
