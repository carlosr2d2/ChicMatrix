import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { getServerApiUrl } from "@/lib/config";

const ACCESS_COOKIE = "chicmatrix_access_token";
const REFRESH_COOKIE = "chicmatrix_refresh_token";
const USER_COOKIE = "chicmatrix_user_id";

function cookieOptions(maxAge: number) {
  return {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax" as const,
    path: "/",
    maxAge,
  };
}

export async function POST(request: Request) {
  const body = (await request.json()) as {
    access_token: string;
    refresh_token: string;
    expires_in?: number;
    user_id?: string;
  };

  if (!body.access_token || !body.refresh_token) {
    return NextResponse.json({ detail: "Missing tokens" }, { status: 400 });
  }

  const accessMaxAge = body.expires_in ?? 60 * 30;
  const refreshMaxAge = 60 * 60 * 24 * 7;
  const cookieStore = cookies();

  cookieStore.set(ACCESS_COOKIE, body.access_token, cookieOptions(accessMaxAge));
  cookieStore.set(REFRESH_COOKIE, body.refresh_token, cookieOptions(refreshMaxAge));

  if (body.user_id) {
    cookieStore.set("chicmatrix_user_id", body.user_id, {
      ...cookieOptions(refreshMaxAge),
      httpOnly: false,
    });
  }

  return NextResponse.json({ ok: true });
}

export async function DELETE() {
  const cookieStore = cookies();
  const refreshToken = cookieStore.get(REFRESH_COOKIE)?.value;

  if (refreshToken) {
    try {
      await fetch(`${getServerApiUrl()}/login/logout`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
    } catch {
      // best-effort logout on backend
    }
  }

  cookieStore.delete(ACCESS_COOKIE);
  cookieStore.delete(REFRESH_COOKIE);
  cookieStore.delete(USER_COOKIE);

  return NextResponse.json({ ok: true });
}
