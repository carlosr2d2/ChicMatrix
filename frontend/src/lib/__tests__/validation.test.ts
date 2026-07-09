import { parseApiError } from "@/lib/errors";
import { validateEmail, validateOtp, validatePassword, validatePhone } from "@/lib/validation";

describe("validation helpers", () => {
  it("validates email format", () => {
    expect(validateEmail("")).toBe("Email is required");
    expect(validateEmail("invalid")).toBe("Enter a valid email address");
    expect(validateEmail("user@chicmatrix.app")).toBeNull();
  });

  it("validates password length", () => {
    expect(validatePassword("short")).toContain("at least");
    expect(validatePassword("SecurePass123")).toBeNull();
  });

  it("validates phone E.164 format", () => {
    expect(validatePhone("300123")).toContain("E.164");
    expect(validatePhone("+573001234567")).toBeNull();
  });

  it("validates otp code", () => {
    expect(validateOtp("12")).toContain("6 digits");
    expect(validateOtp("123456")).toBeNull();
  });
});

describe("parseApiError", () => {
  it("parses FastAPI string detail", () => {
    expect(parseApiError('{"detail":"Invalid credentials"}')).toBe("Invalid credentials");
  });

  it("returns raw text for non-json errors", () => {
    expect(parseApiError("Server unavailable")).toBe("Server unavailable");
  });
});
