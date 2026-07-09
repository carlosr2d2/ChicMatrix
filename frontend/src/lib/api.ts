export type HealthStatus = {
  status: string;
  service: string;
};

export async function getHealth(apiUrl?: string): Promise<HealthStatus | null> {
  const baseUrl = apiUrl ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

  try {
    const res = await fetch(`${baseUrl}/health`, { next: { revalidate: 30 } });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}
