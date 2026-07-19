import AxeBuilder from "@axe-core/playwright";
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

const PERFORMANCE_BUDGET = {
  domContentLoadedMs: 5_000,
  transferredBytes: 8_000_000,
};

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
    if (route === "/") {
      const statusCards = page.locator(".status-card");
      await expect(statusCards).toHaveCount(3);
      for (let index = 0; index < await statusCards.count(); index += 1) {
        const card = statusCards.nth(index);
        const value = card.locator(".status-value");
        const description = card.locator(".status-description");
        await expect(value).toBeVisible();
        await expect(description).toBeVisible();
        const [valueBottom, descriptionTop] = await card.evaluate((element) => {
          const valueElement = element.querySelector<HTMLElement>(".status-value");
          const descriptionElement = element.querySelector<HTMLElement>(".status-description");
          if (!valueElement || !descriptionElement) {
            throw new Error("Status card is missing its value or description element");
          }
          return [
            valueElement.getBoundingClientRect().bottom,
            descriptionElement.getBoundingClientRect().top,
          ] as const;
        });
        expect(valueBottom).toBeLessThanOrEqual(descriptionTop);
      }
    }

    const accessibilityScan = await new AxeBuilder({ page }).analyze();
    expect(accessibilityScan.violations).toEqual([]);

    const performanceMetrics = await page.evaluate(() => {
      const navigation = performance.getEntriesByType("navigation")[0] as
        | PerformanceNavigationTiming
        | undefined;
      const resources = performance.getEntriesByType("resource") as PerformanceResourceTiming[];
      return {
        domContentLoadedMs: navigation?.domContentLoadedEventEnd ?? 0,
        transferredBytes: resources.reduce((total, resource) => total + resource.transferSize, 0),
      };
    });
    expect(performanceMetrics.domContentLoadedMs).toBeLessThanOrEqual(
      PERFORMANCE_BUDGET.domContentLoadedMs,
    );
    expect(performanceMetrics.transferredBytes).toBeLessThanOrEqual(
      PERFORMANCE_BUDGET.transferredBytes,
    );
    await testInfo.attach("performance-metrics", {
      body: JSON.stringify({ route, budget: PERFORMANCE_BUDGET, ...performanceMetrics }, null, 2),
      contentType: "application/json",
    });

    const screenshot = await page.screenshot({ fullPage: route !== "/", scale: "css" });
    expect(screenshot.byteLength).toBeGreaterThan(1_000);
    expect(screenshot.byteLength).toBeLessThan(4_000_000);
    await testInfo.attach("route-screenshot", {
      body: screenshot,
      contentType: "image/png",
    });

    expect(consoleErrors).toEqual([]);
    expect(pageErrors).toEqual([]);
  });
}

test("keeps the public search control keyboard reachable and functional", async ({ page }) => {
  await page.goto("/sources/", { waitUntil: "networkidle" });
  const firstTable = page.locator('section[data-table-section="true"]').first();
  const filter = firstTable.locator("input[data-table-filter]");
  const rows = firstTable.locator("tr[data-table-row]");
  await expect(filter).toBeVisible();
  await filter.focus();
  await expect(filter).toBeFocused();

  const token = (await rows.first().locator("td").first().innerText()).trim().slice(0, 6);
  expect(token).not.toBe("");
  await filter.fill(token);
  await expect(rows.filter({ visible: true })).toHaveCount(1);
  await filter.press("Tab");
  await expect(page.locator(":focus")).toHaveCount(1);
});

test("searches rows beyond the compact initial table view", async ({ page }) => {
  await page.goto("/sources/", { waitUntil: "networkidle" });
  const tables = page.locator('section[data-table-section="true"]');
  let targetTable = tables.first();
  const tableCount = await tables.count();
  for (let index = 0; index < tableCount; index += 1) {
    const candidate = tables.nth(index);
    if ((await candidate.locator("tr[data-table-row]").count()) > 8) {
      targetTable = candidate;
      break;
    }
  }
  const filter = targetTable.locator("input[data-table-filter]");
  const rows = targetTable.locator("tr[data-table-row]");
  expect(await rows.count()).toBeGreaterThan(8);
  const ninthRow = rows.nth(8);
  const token = (await ninthRow.locator("td").first().innerText()).trim().slice(0, 6);
  expect(token).not.toBe("");
  await filter.fill(token);
  await expect(ninthRow).toBeVisible();
});
