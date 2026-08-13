import { parseApiError } from "@/lib/errors";

export type FashionProfile = {
  id: string;
  email: string | null;
  phone: string | null;
  name: string | null;
  verified: boolean;
  role: string;
  social_provider: string | null;
  age: number | null;
  sex: string | null;
  height_cm: number | null;
  weight_kg: number | null;
  body_proportions: Record<string, unknown> | null;
  preferences: {
    colors?: string[];
    brands?: string[];
    styles?: string[];
    [key: string]: unknown;
  } | null;
  habits: {
    occasions?: string[];
    lifestyle?: string;
    [key: string]: unknown;
  } | null;
};

export type FashionProfileUpdate = {
  name?: string | null;
  age?: number | null;
  sex?: string | null;
  height_cm?: number | null;
  weight_kg?: number | null;
  preferences?: {
    colors?: string[];
    brands?: string[];
    styles?: string[];
  };
  habits?: {
    occasions?: string[];
    lifestyle?: string;
  };
};

export async function fetchFashionProfile(): Promise<FashionProfile> {
  const response = await fetch("/api/users/me");
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(parseApiError(detail));
  }
  return response.json() as Promise<FashionProfile>;
}

export async function updateFashionProfile(
  payload: FashionProfileUpdate,
): Promise<FashionProfile> {
  const response = await fetch("/api/users/me/profile", {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(parseApiError(detail));
  }
  return response.json() as Promise<FashionProfile>;
}

export function listToCsv(values?: string[] | null): string {
  return (values ?? []).join(", ");
}

export function csvToList(value: string): string[] {
  return value
    .split(",")
    .map((part) => part.trim())
    .filter(Boolean);
}

export function isProfileComplete(profile: FashionProfile): boolean {
  const hasIdentity = profile.age != null && Boolean(profile.sex);
  const hasBiometrics = profile.height_cm != null && profile.weight_kg != null;
  const hasPreferences =
    (profile.preferences?.colors?.length ?? 0) > 0 ||
    (profile.preferences?.brands?.length ?? 0) > 0 ||
    (profile.preferences?.styles?.length ?? 0) > 0;
  const hasHabits = (profile.habits?.occasions?.length ?? 0) > 0;
  return hasIdentity && hasBiometrics && hasPreferences && hasHabits;
}
