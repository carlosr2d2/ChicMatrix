import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { getServerApiUrl } from "@/lib/config";

export async function POST(request: Request) {
  const accessToken = cookies().get("chicmatrix_access_token")?.value;
  if (!accessToken) {
    return NextResponse.json({ detail: "Not authenticated" }, { status: 401 });
  }

  const { searchParams } = new URL(request.url);
  const upstream = new URL(`${getServerApiUrl()}/scrape/images/backfill`);
  const retailerId = searchParams.get("retailer_id");
  const limit = searchParams.get("limit");
  if (retailerId) upstream.searchParams.set("retailer_id", retailerId);
  if (limit) upstream.searchParams.set("limit", limit);

  const response = await fetch(upstream.toString(), {
    method: "POST",
    headers: { Authorization: `Bearer ${accessToken}` },
    cache: "no-store",
  });

  const body = await response.text();
  return new NextResponse(body, {
    status: response.status,
    headers: { "Content-Type": "application/json" },
  });
}
