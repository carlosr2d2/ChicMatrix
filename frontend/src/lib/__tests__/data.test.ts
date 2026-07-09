import { featuredProducts, processSteps } from "@/lib/data";

describe("data exports", () => {
  it("exposes featured products", () => {
    expect(featuredProducts.length).toBeGreaterThan(0);
    expect(featuredProducts[0]).toMatchObject({
      id: expect.any(Number),
      name: expect.any(String),
      brand: expect.any(String),
      price: expect.any(String),
      image: expect.any(String),
    });
  });

  it("exposes onboarding process steps", () => {
    expect(processSteps).toHaveLength(3);
    expect(processSteps[0].step).toBe("01");
    expect(processSteps[2].title).toBe("Recommend");
  });
});
