import {
  csvToList,
  isProfileComplete,
  listToCsv,
  type FashionProfile,
} from "@/lib/profile";

describe("profile helpers", () => {
  it("converts lists to csv and back", () => {
    expect(listToCsv(["black", "beige"])).toBe("black, beige");
    expect(csvToList("black, beige , navy")).toEqual(["black", "beige", "navy"]);
    expect(csvToList("  ")).toEqual([]);
  });

  it("detects incomplete profiles", () => {
    const incomplete: FashionProfile = {
      id: "1",
      email: "a@b.c",
      phone: null,
      name: null,
      verified: true,
      role: "user",
      social_provider: null,
      age: null,
      sex: null,
      height_cm: null,
      weight_kg: null,
      body_proportions: null,
      preferences: null,
      habits: null,
    };
    expect(isProfileComplete(incomplete)).toBe(false);
  });

  it("detects complete profiles", () => {
    const complete: FashionProfile = {
      id: "1",
      email: "a@b.c",
      phone: null,
      name: "Alex",
      verified: true,
      role: "user",
      social_provider: null,
      age: 28,
      sex: "female",
      height_cm: 172,
      weight_kg: 68,
      body_proportions: null,
      preferences: { colors: ["black"], brands: ["Maison Noir"] },
      habits: { occasions: ["office"] },
    };
    expect(isProfileComplete(complete)).toBe(true);
  });
});
