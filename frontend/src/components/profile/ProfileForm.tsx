"use client";

import { FormEvent, useEffect, useState } from "react";

import { Alert } from "@/components/auth/Alert";
import { Spinner } from "@/components/auth/Spinner";
import {
  FashionProfile,
  FashionProfileUpdate,
  csvToList,
  listToCsv,
} from "@/lib/profile";
import { STYLE_OPTIONS } from "@/lib/styles";

type ProfileFormProps = {
  profile: FashionProfile;
  onSave: (payload: FashionProfileUpdate) => Promise<FashionProfile>;
};

export function ProfileForm({ profile, onSave }: ProfileFormProps) {
  const [name, setName] = useState(profile.name ?? "");
  const [heightCm, setHeightCm] = useState(
    profile.height_cm != null ? String(profile.height_cm) : "",
  );
  const [weightKg, setWeightKg] = useState(
    profile.weight_kg != null ? String(profile.weight_kg) : "",
  );
  const [colors, setColors] = useState(listToCsv(profile.preferences?.colors));
  const [brands, setBrands] = useState(listToCsv(profile.preferences?.brands));
  const [styles, setStyles] = useState<string[]>(profile.preferences?.styles ?? []);
  const [occasions, setOccasions] = useState(listToCsv(profile.habits?.occasions));
  const [lifestyle, setLifestyle] = useState(
    typeof profile.habits?.lifestyle === "string" ? profile.habits.lifestyle : "",
  );
  const [feedback, setFeedback] = useState<{ type: "success" | "error"; message: string } | null>(
    null,
  );
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    setName(profile.name ?? "");
    setHeightCm(profile.height_cm != null ? String(profile.height_cm) : "");
    setWeightKg(profile.weight_kg != null ? String(profile.weight_kg) : "");
    setColors(listToCsv(profile.preferences?.colors));
    setBrands(listToCsv(profile.preferences?.brands));
    setStyles(profile.preferences?.styles ?? []);
    setOccasions(listToCsv(profile.habits?.occasions));
    setLifestyle(typeof profile.habits?.lifestyle === "string" ? profile.habits.lifestyle : "");
  }, [profile]);

  const toggleStyle = (code: string) => {
    setStyles((current) =>
      current.includes(code) ? current.filter((item) => item !== code) : [...current, code],
    );
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setFeedback(null);

    const height = heightCm.trim() ? Number(heightCm) : null;
    const weight = weightKg.trim() ? Number(weightKg) : null;

    if (height != null && (Number.isNaN(height) || height < 100 || height > 250)) {
      setFeedback({ type: "error", message: "Height must be between 100 and 250 cm" });
      return;
    }
    if (weight != null && (Number.isNaN(weight) || weight < 30 || weight > 300)) {
      setFeedback({ type: "error", message: "Weight must be between 30 and 300 kg" });
      return;
    }

    const payload: FashionProfileUpdate = {
      name: name.trim() || null,
      height_cm: height,
      weight_kg: weight,
      preferences: {
        colors: csvToList(colors),
        brands: csvToList(brands),
        styles,
      },
      habits: {
        occasions: csvToList(occasions),
        lifestyle: lifestyle.trim() || undefined,
      },
    };

    setIsSubmitting(true);
    try {
      await onSave(payload);
      setFeedback({
        type: "success",
        message: "Profile saved. Recommendations will use these preferences.",
      });
    } catch (error) {
      setFeedback({
        type: "error",
        message: error instanceof Error ? error.message : "Could not save profile",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-8" noValidate>
      <section className="bg-white border border-sand/80 p-6 space-y-5">
        <h2 className="text-sm tracking-[0.2em] uppercase text-stone-500">Identity</h2>
        <div>
          <label htmlFor="profile-name" className="block text-sm text-stone-600 mb-2">
            Display name
          </label>
          <input
            id="profile-name"
            type="text"
            value={name}
            onChange={(event) => setName(event.target.value)}
            className="w-full border border-sand bg-cream px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-ink"
            autoComplete="name"
          />
        </div>
      </section>

      <section className="bg-white border border-sand/80 p-6 space-y-5">
        <h2 className="text-sm tracking-[0.2em] uppercase text-stone-500">Biometrics</h2>
        <div className="grid sm:grid-cols-2 gap-5">
          <div>
            <label htmlFor="profile-height" className="block text-sm text-stone-600 mb-2">
              Height (cm)
            </label>
            <input
              id="profile-height"
              type="number"
              inputMode="decimal"
              min={100}
              max={250}
              step="0.1"
              value={heightCm}
              onChange={(event) => setHeightCm(event.target.value)}
              className="w-full border border-sand bg-cream px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-ink"
            />
          </div>
          <div>
            <label htmlFor="profile-weight" className="block text-sm text-stone-600 mb-2">
              Weight (kg)
            </label>
            <input
              id="profile-weight"
              type="number"
              inputMode="decimal"
              min={30}
              max={300}
              step="0.1"
              value={weightKg}
              onChange={(event) => setWeightKg(event.target.value)}
              className="w-full border border-sand bg-cream px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-ink"
            />
          </div>
        </div>
      </section>

      <section className="bg-white border border-sand/80 p-6 space-y-5">
        <h2 className="text-sm tracking-[0.2em] uppercase text-stone-500">Preferences</h2>
        <div>
          <p className="block text-sm text-stone-600 mb-3" id="profile-styles-label">
            Preferred styles
          </p>
          <div
            className="flex flex-wrap gap-2"
            role="group"
            aria-labelledby="profile-styles-label"
          >
            {STYLE_OPTIONS.map((option) => {
              const selected = styles.includes(option.code);
              return (
                <button
                  key={option.code}
                  type="button"
                  onClick={() => toggleStyle(option.code)}
                  aria-pressed={selected}
                  className={
                    selected
                      ? "text-xs tracking-[0.15em] uppercase px-3 py-2 bg-ink text-cream border border-ink"
                      : "text-xs tracking-[0.15em] uppercase px-3 py-2 bg-cream text-stone-600 border border-sand"
                  }
                >
                  {option.labelEs}
                </button>
              );
            })}
          </div>
        </div>
        <div>
          <label htmlFor="profile-colors" className="block text-sm text-stone-600 mb-2">
            Preferred colors
          </label>
          <input
            id="profile-colors"
            type="text"
            value={colors}
            onChange={(event) => setColors(event.target.value)}
            placeholder="black, beige, navy"
            className="w-full border border-sand bg-cream px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-ink"
            aria-describedby="profile-colors-help"
          />
          <p id="profile-colors-help" className="mt-2 text-sm text-stone-500 font-light">
            Comma-separated list
          </p>
        </div>
        <div>
          <label htmlFor="profile-brands" className="block text-sm text-stone-600 mb-2">
            Preferred brands
          </label>
          <input
            id="profile-brands"
            type="text"
            value={brands}
            onChange={(event) => setBrands(event.target.value)}
            placeholder="Maison Noir, Urban Loom"
            className="w-full border border-sand bg-cream px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-ink"
          />
        </div>
      </section>

      <section className="bg-white border border-sand/80 p-6 space-y-5">
        <h2 className="text-sm tracking-[0.2em] uppercase text-stone-500">Lifestyle</h2>
        <div>
          <label htmlFor="profile-occasions" className="block text-sm text-stone-600 mb-2">
            Occasions
          </label>
          <input
            id="profile-occasions"
            type="text"
            value={occasions}
            onChange={(event) => setOccasions(event.target.value)}
            placeholder="office, casual, evening"
            className="w-full border border-sand bg-cream px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-ink"
          />
        </div>
        <div>
          <label htmlFor="profile-lifestyle" className="block text-sm text-stone-600 mb-2">
            Lifestyle note
          </label>
          <input
            id="profile-lifestyle"
            type="text"
            value={lifestyle}
            onChange={(event) => setLifestyle(event.target.value)}
            placeholder="urban professional"
            className="w-full border border-sand bg-cream px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-ink"
          />
        </div>
      </section>

      <button type="submit" className="btn-primary" disabled={isSubmitting}>
        {isSubmitting ? <Spinner label="Saving…" className="text-white" /> : "Save profile"}
      </button>

      {feedback ? (
        <Alert variant={feedback.type === "success" ? "success" : "error"}>
          {feedback.message}
        </Alert>
      ) : null}
    </form>
  );
}
