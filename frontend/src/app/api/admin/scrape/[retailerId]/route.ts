import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { getServerApiUrl } from "@/lib/config";

type RouteContext = {
  params: { retailerId: string };
};

export async function POST(_request: Request, context: RouteContext) {
  const accessToken = cookies().get("chicmatrix_access_token")?.value;
  if (!accessToken) {
    return NextResponse.json({ detail: "Not authenticated" }, { status: 401 });
  }

  const retailerId = context.params.retailerId;
  if (!/^\d+$/.test(retailerId)) {
    return NextResponse.json({ detail: "Invalid retailer id" }, { status: 400 });
  }

  const response = await fetch(`${getServerApiUrl()}/scrape/${retailerId}`, {
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
