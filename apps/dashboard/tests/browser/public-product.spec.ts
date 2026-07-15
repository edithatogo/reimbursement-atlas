import { expect, test } from "@playwright/test";

const routes = [
  "/",
  "/analyses/",
  "/automation/",
  "/crosswalks/",
  "/demonstrators/",
  "/ontologies/",
  "/readiness/",
  "/roadmap/",
  "/sources/",
];

for (const route of routes) {
  test(`renders public route ${route}`, async ({ page }, testInfo) => {
    const consoleErrors: string[] = [];
    const pageErrors: string[] = [];
    page.on("console", (message) => {
      if (message.type() === "error") consoleErrors.push(message.text());
    });
    page.on("pageerror", (error) => pageErrors.push(error.message));

    const response = await page.goto(route, { waitUntil: "networkidle" });
    expect(response?.status()).toBe(200);
    await expect(page.locator("html[lang]")).toHaveCount(1);
    await expect(page.locator("h1")).toHaveCount(1);
    await expect(page).toHaveTitle(/Reimbursement Atlas/);

    const screenshot = await page.screenshot({ fullPage: true, scale: "css" });
    expect(screenshot.byteLength).toBeGreaterThan(1_000);
    expect(screenshot.byteLength).toBeLessThan(3_000_000);
    await testInfo.attach("route-screenshot", {
      body: screenshot,
      contentType: "image/png",
    });

    expect(consoleErrors).toEqual([]);
    expect(pageErrors).toEqual([]);
  });
}
