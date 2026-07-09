import {
  isTokenResponse,
  login,
  logout,
  refreshTokens,
  registerEmail,
  verifyEmail,
} from "@/lib/auth";

describe("auth API client", () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  it("registers a user by email", async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        user_id: "uuid-1",
        email: "user@chicmatrix.app",
        verified: false,
        message: "Registration successful",
        verification_token: "token-abc",
      }),
    }) as jest.Mock;

    const result = await registerEmail("http://api.test", {
      email: "user@chicmatrix.app",
      password: "SecurePass123",
      consent_accepted: true,
    });

    expect(result.verification_token).toBe("token-abc");
    expect(global.fetch).toHaveBeenCalledWith(
      "http://api.test/register/email",
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("verifies email tokens", async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        user_id: "uuid-1",
        email: "user@chicmatrix.app",
        verified: true,
        message: "Email verified",
      }),
    }) as jest.Mock;

    const result = await verifyEmail("http://api.test", { token: "token-abc" });
    expect(result.verified).toBe(true);
  });

  it("logs in with email credentials", async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        access_token: "access",
        refresh_token: "refresh",
        token_type: "bearer",
        expires_in: 1800,
        user_id: "uuid-1",
        role: "user",
        permissions: ["read:profile"],
      }),
    }) as jest.Mock;

    const result = await login("http://api.test", {
      method: "email",
      email: "user@chicmatrix.app",
      password: "SecurePass123",
    });

    expect(isTokenResponse(result)).toBe(true);
    if (isTokenResponse(result)) {
      expect(result.access_token).toBe("access");
    }
  });

  it("requests phone OTP during login", async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        message: "OTP sent",
        otp_code: "123456",
      }),
    }) as jest.Mock;

    const result = await login("http://api.test", {
      method: "phone",
      phone: "+573001234567",
    });

    expect(isTokenResponse(result)).toBe(false);
    if (!isTokenResponse(result)) {
      expect(result.otp_code).toBe("123456");
    }
  });

  it("refreshes tokens", async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        access_token: "new-access",
        refresh_token: "new-refresh",
        token_type: "bearer",
        expires_in: 1800,
        user_id: "uuid-1",
        role: "user",
        permissions: ["read:profile"],
      }),
    }) as jest.Mock;

    const result = await refreshTokens("http://api.test", "refresh");
    expect(result.refresh_token).toBe("new-refresh");
  });

  it("logs out successfully", async () => {
    global.fetch = jest.fn().mockResolvedValue({ ok: true }) as jest.Mock;
    await expect(logout("http://api.test", "refresh")).resolves.toBeUndefined();
  });

  it("throws when API returns an error", async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: false,
      status: 401,
      text: async () => "Invalid credentials",
    }) as jest.Mock;

    await expect(
      login("http://api.test", {
        method: "email",
        email: "user@chicmatrix.app",
        password: "wrong",
      }),
    ).rejects.toThrow("Invalid credentials");
  });
});
