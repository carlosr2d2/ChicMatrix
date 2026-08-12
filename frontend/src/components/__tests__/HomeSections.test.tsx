import { render, screen } from "@testing-library/react";

import { Header, StatusBanner } from "@/components/HomeSections";

describe("Header", () => {
  it("renders brand and navigation links", () => {
    render(<Header />);

    expect(screen.getByText("ChicMatrix")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Collection" })).toHaveAttribute("href", "#collection");
    expect(screen.getByRole("link", { name: "Sign in" })).toHaveAttribute("href", "/login");
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
