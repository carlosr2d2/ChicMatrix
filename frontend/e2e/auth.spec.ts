import { expect, test } from "@playwright/test";

function emailField(page: import("@playwright/test").Page) {
  return page.getByRole("textbox", { name: "Email" });
}

function passwordField(page: import("@playwright/test").Page) {
  return page.getByRole("textbox", { name: "Password" });
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
    const email = `playwright.${Date.now()}@chicmatrix.app`;

    await page.goto("/register");
    await emailField(page).fill(email);
    await page.locator("#register-password").fill("SecurePass123");
    await page.getByRole("checkbox").first().check();
    await page.getByRole("button", { name: "Create account" }).click();

    const successAlert = page.getByRole("status").filter({ hasText: /registration|successful/i });
    const errorAlert = page.getByRole("alert");
    await expect(successAlert.or(errorAlert)).toBeVisible({ timeout: 15_000 });

    if (await errorAlert.isVisible()) {
      const errorText = await errorAlert.textContent();
      throw new Error(`Registration failed: ${errorText}`);
    }

    const tokenBlock = page.getByRole("status").locator("code");
    await expect(tokenBlock).toBeVisible({ timeout: 5_000 });
    const token = (await tokenBlock.textContent())?.trim();
    expect(token).toBeTruthy();

    await page.goto(`/verify?token=${encodeURIComponent(token!)}`);
    await page.getByRole("button", { name: "Verify email" }).click();
    await expect(page.getByText(/verified/i)).toBeVisible({ timeout: 10_000 });

    await page.goto("/login");
    await emailField(page).fill(email);
    await page.locator("#login-password").fill("SecurePass123");
    await page.getByRole("button", { name: "Sign in" }).click();

    await expect(page).toHaveURL(/\/dashboard/, { timeout: 15_000 });
    await expect(page.getByRole("heading", { name: /Hello/i })).toBeVisible();
    await expect(page.getByText(email)).toBeVisible();
  });
});
