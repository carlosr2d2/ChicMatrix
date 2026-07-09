import { expect, test } from "@playwright/test";

function emailField(page: import("@playwright/test").Page) {
  return page.getByRole("textbox", { name: "Email" });
}

function passwordField(page: import("@playwright/test").Page) {
  return page.getByRole("textbox", { name: "Password" });
}

function registerConsentCheckbox(page: import("@playwright/test").Page) {
  return page.getByRole("checkbox", { name: /GDPR/i });
}

test.describe("Auth UI", () => {
  test("register page renders all methods", async ({ page }) => {
    await page.goto("/register");
    await expect(page.getByRole("heading", { name: "Create your account" })).toBeVisible();
    await expect(page.getByRole("tab", { name: "Email" })).toBeVisible();
    await expect(page.getByRole("tab", { name: "Phone" })).toBeVisible();
    await expect(page.getByRole("tab", { name: "Social" })).toBeVisible();
    await expect(emailField(page)).toBeVisible();
  });

  test("login page renders email form", async ({ page }) => {
    await page.goto("/login");
    await expect(page.getByRole("heading", { name: "Welcome back" })).toBeVisible();
    await expect(emailField(page)).toBeVisible();
    await expect(passwordField(page)).toBeVisible();
  });

  test("verify page renders email and phone panels", async ({ page }) => {
    await page.goto("/verify");
    await expect(page.getByRole("heading", { name: "Verify your account" })).toBeVisible();
    await expect(page.getByRole("textbox", { name: "Email verification token" })).toBeVisible();
    await page.getByRole("tab", { name: "Phone" }).click();
    await expect(page.getByRole("textbox", { name: "Phone number" })).toBeVisible();
    await expect(page.getByRole("textbox", { name: "OTP code" })).toBeVisible();
  });

  test("shows validation errors on empty email register", async ({ page }) => {
    await page.goto("/register");
    await page.getByRole("button", { name: "Create account" }).click();
    await expect(page.getByText("Email is required")).toBeVisible();
    await expect(page.getByText("Consent is required")).toBeVisible();
  });
});

test.describe("Auth flow", () => {
  test.skip(!process.env.E2E_WITH_BACKEND, "Set E2E_WITH_BACKEND=true to run full API flow");

  test("email register, verify, login and reach dashboard", async ({ page }) => {
    test.setTimeout(90_000);

    const email = `playwright.${Date.now()}@chicmatrix.app`;
    const password = "SecurePass123";

    await page.goto("/register");
    await emailField(page).fill(email);
    await page.locator("#register-password").fill(password);
    await registerConsentCheckbox(page).check();

    const registerResponsePromise = page.waitForResponse(
      (response) =>
        response.url().includes("/register/email") && response.request().method() === "POST",
      { timeout: 20_000 },
    );

    await page.getByRole("button", { name: "Create account" }).click();

    const registerResponse = await registerResponsePromise;
    const registerBody = await registerResponse.json();
    expect(
      registerResponse.status(),
      `Register failed: ${JSON.stringify(registerBody)}`,
    ).toBe(201);

    const token = registerBody.verification_token as string | null | undefined;
    expect(token, "EMAIL_DEBUG should return verification_token in CI").toBeTruthy();

    await page.goto(`/verify?token=${encodeURIComponent(token!)}`);
    const verifyResponsePromise = page.waitForResponse(
      (response) =>
        response.url().includes("/verify/email") && response.request().method() === "POST",
      { timeout: 15_000 },
    );
    await page.getByRole("button", { name: "Verify email" }).click();
    const verifyResponse = await verifyResponsePromise;
    expect(verifyResponse.status()).toBe(200);

    await page.goto("/login");
    await emailField(page).fill(email);
    await page.locator("#login-password").fill(password);

    const loginResponsePromise = page.waitForResponse(
      (response) => response.url().includes("/login") && response.request().method() === "POST",
      { timeout: 15_000 },
    );
    await page.getByRole("button", { name: "Sign in" }).click();
    const loginResponse = await loginResponsePromise;
    expect(loginResponse.status()).toBe(200);

    await expect(page).toHaveURL(/\/dashboard/, { timeout: 15_000 });
    await expect(page.getByRole("heading", { name: /Hello/i })).toBeVisible({ timeout: 15_000 });
    await expect(page.getByText(email)).toBeVisible();
  });
});
