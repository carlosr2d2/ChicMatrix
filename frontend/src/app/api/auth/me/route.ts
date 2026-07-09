import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { getServerApiUrl } from "@/lib/config";

export async function GET() {
  const accessToken = cookies().get("chicmatrix_access_token")?.value;

  if (!accessToken) {
    return NextResponse.json({ detail: "Not authenticated" }, { status: 401 });
  }

  const response = await fetch(`${getServerApiUrl()}/auth/me`, {
    headers: { Authorization: `Bearer ${accessToken}` },
    cache: "no-store",
  });

  const body = await response.text();
  return new NextResponse(body, {
    status: response.status,
    headers: { "Content-Type": "application/json" },
  });
}
