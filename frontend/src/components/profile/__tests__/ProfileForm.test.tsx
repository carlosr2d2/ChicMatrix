import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { ProfileForm } from "@/components/profile/ProfileForm";
import type { FashionProfile } from "@/lib/profile";

const baseProfile: FashionProfile = {
  id: "uuid-1",
  email: "user@chicmatrix.app",
  phone: null,
  name: "Alex",
  verified: true,
  role: "user",
  social_provider: null,
  height_cm: 172,
  weight_kg: 68,
  body_proportions: null,
  preferences: { colors: ["black"], brands: ["Maison Noir"] },
  habits: { occasions: ["office"], lifestyle: "urban" },
};

describe("ProfileForm", () => {
  it("submits updated fashion profile values", async () => {
    const user = userEvent.setup();
    const onSave = jest.fn().mockResolvedValue({
      ...baseProfile,
      height_cm: 175,
      preferences: { colors: ["navy"], brands: ["Urban Loom"] },
    });

    render(<ProfileForm profile={baseProfile} onSave={onSave} />);

    await user.clear(screen.getByLabelText("Height (cm)"));
    await user.type(screen.getByLabelText("Height (cm)"), "175");
    await user.clear(screen.getByLabelText("Preferred colors"));
    await user.type(screen.getByLabelText("Preferred colors"), "navy");
    await user.clear(screen.getByLabelText("Preferred brands"));
    await user.type(screen.getByLabelText("Preferred brands"), "Urban Loom");
    await user.click(screen.getByRole("button", { name: "Save profile" }));

    expect(onSave).toHaveBeenCalledWith(
      expect.objectContaining({
        height_cm: 175,
        preferences: { colors: ["navy"], brands: ["Urban Loom"], styles: [] },
      }),
    );
    expect(await screen.findByText(/Profile saved/i)).toBeInTheDocument();
  });

  it("toggles preferred styles into the save payload", async () => {
    const user = userEvent.setup();
    const onSave = jest.fn().mockResolvedValue(baseProfile);

    render(<ProfileForm profile={baseProfile} onSave={onSave} />);

    await user.click(screen.getByRole("button", { name: "Formales" }));
    await user.click(screen.getByRole("button", { name: "Save profile" }));

    expect(onSave).toHaveBeenCalledWith(
      expect.objectContaining({
        preferences: expect.objectContaining({ styles: ["formal"] }),
      }),
    );
  });
});
