import React from "react";
import { fireEvent, render, screen } from "@testing-library/react";

import { ProductImage } from "@/components/ProductImage";

describe("ProductImage", () => {
  it("shows missing-image placeholder when src is empty", () => {
    render(<ProductImage src={null} alt="Pleated Silk Blouse" />);
    expect(screen.getByText("Sin imagen")).toBeInTheDocument();
    expect(screen.getByText("Pleated Silk Blouse")).toBeInTheDocument();
  });

  it("falls back to placeholder when the image fails to load", () => {
    render(
      <div className="relative h-40 w-32">
        <ProductImage src="https://example.com/broken.jpg" alt="Pleated Silk Blouse" />
      </div>,
    );

    const image = screen.getByRole("img", { name: "Pleated Silk Blouse" });
    fireEvent.error(image);

    expect(screen.getByText("Sin imagen")).toBeInTheDocument();
  });

  it("renders with priority for hero images", () => {
    render(
      <div className="relative h-40 w-32">
        <ProductImage
          src="https://images.unsplash.com/photo-1.jpg"
          alt="Hero piece"
          priority
          variant="hero"
        />
      </div>,
    );
    expect(screen.getByRole("img", { name: "Hero piece" })).toBeInTheDocument();
  });
});
