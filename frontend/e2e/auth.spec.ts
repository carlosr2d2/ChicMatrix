import { expect, test } from "@playwright/test";

test.describe("Auth UI", () => {
  test("register page renders all methods", async ({ page }) => {
    await page.goto("/register");
    await expect(page.getByRole("heading", { name: "Create your account" })).toBeVisible();
    await expect(page.getByRole("tab", { name: "Email" })).toBeVisible();
    await expect(page.getByRole("tab", { name: "Phone" })).toBeVisible();
    await expect(page.getByRole("tab", { name: "Social" })).toBeVisible();
    await expect(page.getByLabel("Email")).toBeVisible();
  });

  test("login page renders email form", async ({ page }) => {
    await page.goto("/login");
    await expect(page.getByRole("heading", { name: "Welcome back" })).toBeVisible();
    await expect(page.getByLabel("Email")).toBeVisible();
    await expect(page.getByLabel("Password")).toBeVisible();
  });

  test("verify page renders email and phone panels", async ({ page }) => {
    await page.goto("/verify");
    await expect(page.getByRole("heading", { name: "Verify your account" })).toBeVisible();
    await expect(page.getByLabel("Email verification token")).toBeVisible();
    await page.getByRole("tab", { name: "Phone" }).click();
    await expect(page.getByLabel("Phone number")).toBeVisible();
    await expect(page.getByLabel("OTP code")).toBeVisible();
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
    await page.getByLabel("Email").fill(email);
    await page.getByLabel("Password", { exact: true }).fill("SecurePass123");
    await page.getByRole("checkbox").first().check();
    await page.getByRole("button", { name: "Create account" }).click();

    const tokenBlock = page.locator("code").first();
    await expect(tokenBlock).toBeVisible({ timeout: 15_000 });
    const token = (await tokenBlock.textContent())?.trim();
    expect(token).toBeTruthy();

    await page.goto(`/verify?token=${encodeURIComponent(token!)}`);
    await page.getByRole("button", { name: "Verify email" }).click();
    await expect(page.getByText(/verified/i)).toBeVisible({ timeout: 10_000 });

    await page.goto("/login");
    await page.getByLabel("Email").fill(email);
    await page.getByLabel("Password").fill("SecurePass123");
    await page.getByRole("button", { name: "Sign in" }).click();

    await expect(page).toHaveURL(/\/dashboard/, { timeout: 15_000 });
    await expect(page.getByRole("heading", { name: /Hello/i })).toBeVisible();
    await expect(page.getByText(email)).toBeVisible();
  });
});
