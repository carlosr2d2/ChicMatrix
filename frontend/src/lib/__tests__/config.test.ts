import { getApiUrl, getGoogleClientId, getServerApiUrl, isSocialAuthDebug } from "@/lib/config";

describe("config", () => {
  const originalEnv = process.env;

  beforeEach(() => {
    process.env = { ...originalEnv };
  });

  afterAll(() => {
    process.env = originalEnv;
  });

  it("returns default API URL", () => {
    delete process.env.NEXT_PUBLIC_API_URL;
    expect(getApiUrl()).toBe("http://localhost:8001");
  });

  it("reads social debug flag", () => {
    process.env.NEXT_PUBLIC_SOCIAL_AUTH_DEBUG = "true";
    expect(isSocialAuthDebug()).toBe(true);
  });

  it("reads google client id when configured", () => {
    process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID = "google-client";
    expect(getGoogleClientId()).toBe("google-client");
  });

  it("uses internal API URL on the server", () => {
    process.env.API_INTERNAL_URL = "http://backend:8000";
    expect(getServerApiUrl()).toBe("http://backend:8000");
  });
});
