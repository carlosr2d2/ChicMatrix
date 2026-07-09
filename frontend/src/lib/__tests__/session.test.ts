import { clearSession, fetchCurrentUser, saveSession } from "@/lib/session";

describe("session helpers", () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  it("saves session via API route", async () => {
    global.fetch = jest.fn().mockResolvedValue({ ok: true }) as jest.Mock;

    await saveSession({
      access_token: "access",
      refresh_token: "refresh",
      expires_in: 1800,
      user_id: "uuid-1",
      token_type: "bearer",
      role: "user",
      permissions: [],
    });

    expect(global.fetch).toHaveBeenCalledWith(
      "/api/auth/session",
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("fetches current user profile", async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        id: "uuid-1",
        email: "user@chicmatrix.app",
        phone: null,
        name: "User",
        verified: true,
        role: "user",
        social_provider: null,
      }),
    }) as jest.Mock;

    const user = await fetchCurrentUser();
    expect(user.email).toBe("user@chicmatrix.app");
  });

  it("clears session", async () => {
    global.fetch = jest.fn().mockResolvedValue({ ok: true }) as jest.Mock;
    await clearSession();
    expect(global.fetch).toHaveBeenCalledWith("/api/auth/session", { method: "DELETE" });
  });
});
