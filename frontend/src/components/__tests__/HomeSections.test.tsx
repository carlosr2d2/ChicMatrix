import { render, screen } from "@testing-library/react";

import { Header, FeaturedGrid, StatusBanner } from "@/components/HomeSections";

describe("Header", () => {
  it("renders brand and navigation links", () => {
    render(<Header />);

    expect(screen.getByText("ChicMatrix")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Collection" })).toHaveAttribute("href", "#collection");
    expect(screen.getByRole("link", { name: "Sign in" })).toHaveAttribute("href", "/login");
  });
});

describe("FeaturedGrid", () => {
  it("renders featured products", () => {
    render(<FeaturedGrid />);

    expect(screen.getByText("Featured pieces")).toBeInTheDocument();
    expect(screen.getByText("Structured Wool Blazer")).toBeInTheDocument();
    expect(screen.getAllByText("Maison Noir").length).toBeGreaterThan(0);
    expect(screen.getByText("$289")).toBeInTheDocument();
  });
});

describe("StatusBanner", () => {
  it("shows operational status when API is healthy", () => {
    render(<StatusBanner health={{ status: "ok" }} />);
    expect(screen.getByText("Operational")).toBeInTheDocument();
  });

  it("shows connecting state when API is unavailable", () => {
    render(<StatusBanner health={null} />);
    expect(screen.getByText("Connecting...")).toBeInTheDocument();
  });
});
