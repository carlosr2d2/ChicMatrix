import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";

import { DashboardPageClient } from "@/app/dashboard/DashboardPageClient";

jest.mock("next/navigation", () => ({
  useRouter: () => ({ push: jest.fn(), refresh: jest.fn() }),
}));

function renderWithQuery(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(<QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>);
}

describe("DashboardPageClient", () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  it("links into the product loop for customers", async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        id: "u1",
        email: "demo@chicmatrix.app",
        name: "Alex Rivera",
        role: "user",
        verified: true,
      }),
    }) as jest.Mock;

    renderWithQuery(<DashboardPageClient />);

    expect(await screen.findByRole("heading", { name: /Hello, Alex Rivera/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /View recommendations/i })).toHaveAttribute(
      "href",
      "/recommendations",
    );
    expect(screen.getByRole("link", { name: /Edit fashion profile/i })).toHaveAttribute(
      "href",
      "/profile",
    );
    expect(screen.queryByRole("link", { name: /Admin scrapes/i })).not.toBeInTheDocument();
  });

  it("shows admin scrape CTA for admins", async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        id: "a1",
        email: "admin@chicmatrix.app",
        name: "System Admin",
        role: "admin",
        verified: true,
      }),
    }) as jest.Mock;

    renderWithQuery(<DashboardPageClient />);

    expect(await screen.findByRole("link", { name: /Admin scrapes/i })).toHaveAttribute(
      "href",
      "/admin",
    );
  });
});
