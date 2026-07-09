export function getApiUrl(): string {
  return process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8001";
}

/** Server-side API URL (Next.js route handlers, SSR). Use Docker service name in containers. */
export function getServerApiUrl(): string {
  return process.env.API_INTERNAL_URL ?? getApiUrl();
}

export function isSocialAuthDebug(): boolean {
  return process.env.NEXT_PUBLIC_SOCIAL_AUTH_DEBUG === "true";
}

export function getGoogleClientId(): string | undefined {
  return process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || undefined;
}
