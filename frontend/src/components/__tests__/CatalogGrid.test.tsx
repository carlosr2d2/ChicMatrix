import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";

import { CatalogGrid } from "@/components/CatalogGrid";

const sampleProducts = {
  items: [
    {
      id: 1,
      name: "Structured Wool Blazer",
      description: null,
      image_url: "https://images.unsplash.com/photo-1.jpg",
      category: "evening",
      brand: "Maison Noir",
      color: null,
      retailer_id: 1,
      retailer_name: "Maison Noir",
      latest_price: { amount: 289, currency: "USD", scraped_at: "2026-01-01T00:00:00Z" },
    },
  ],
  total: 1,
};

function renderWithQuery(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(<QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>);
}

describe("CatalogGrid", () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  it("renders products from API", async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => sampleProducts,
    }) as jest.Mock;

    renderWithQuery(<CatalogGrid />);

    expect(await screen.findByText("Structured Wool Blazer")).toBeInTheDocument();
    expect(screen.getByText("$289")).toBeInTheDocument();
    expect(screen.getByText(/1 items/i)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /Update prices/i })).not.toBeInTheDocument();
  });

  it("shows empty state without customer scrape actions", async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ items: [], total: 0 }),
    }) as jest.Mock;

    renderWithQuery(<CatalogGrid />);

    expect(await screen.findByText(/administrator must run scrapes/i)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /Run first scrape/i })).not.toBeInTheDocument();
  });
});
