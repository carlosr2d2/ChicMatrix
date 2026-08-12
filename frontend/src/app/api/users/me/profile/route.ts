import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { getServerApiUrl } from "@/lib/config";

export async function PATCH(request: Request) {
  const accessToken = cookies().get("chicmatrix_access_token")?.value;
  if (!accessToken) {
    return NextResponse.json({ detail: "Not authenticated" }, { status: 401 });
  }

  const payload = await request.text();
  const response = await fetch(`${getServerApiUrl()}/users/me/profile`, {
    method: "PATCH",
    headers: {
      Authorization: `Bearer ${accessToken}`,
      "Content-Type": "application/json",
    },
    body: payload,
    cache: "no-store",
  });

  const body = await response.text();
  return new NextResponse(body, {
    status: response.status,
    headers: { "Content-Type": "application/json" },
  });
}
