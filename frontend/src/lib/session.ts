import { parseApiError } from "@/lib/errors";

export type SessionPayload = {
  access_token: string;
  refresh_token: string;
  expires_in?: number;
  user_id?: string;
};

export async function saveSession(tokens: SessionPayload): Promise<void> {
  const response = await fetch("/api/auth/session", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(tokens),
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(parseApiError(detail));
  }
}

export async function clearSession(): Promise<void> {
  const response = await fetch("/api/auth/session", { method: "DELETE" });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(parseApiError(detail));
  }
}

export type UserProfile = {
  id: string;
  email: string | null;
  phone: string | null;
  name: string | null;
  verified: boolean;
  role: string;
  social_provider: string | null;
};

export async function fetchCurrentUser(): Promise<UserProfile> {
  const response = await fetch("/api/auth/me");
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(parseApiError(detail));
  }
  return response.json() as Promise<UserProfile>;
}
