import AxeBuilder from "@axe-core/playwright";
import { expect, type Browser, type Page, test, type TestInfo } from "@playwright/test";

export const routes = [
  "/",
  "/analyses/",
  "/analyses/cognitive_vs_procedural_ratio/",
  "/automation/",
  "/crosswalks/",
  "/demonstrators/",
  "/ontologies/",
  "/readiness/",
  "/roadmap/",
  "/sources/",
  "/sources/au_mbs/",
];

const navLabelByRoute = new Map([
  ["/", "Graph"],
  ["/analyses/", "Analyses"],
  ["/analyses/cognitive_vs_procedural_ratio/", "Analyses"],
  ["/automation/", "Automation"],
  ["/crosswalks/", "Crosswalks"],
  ["/demonstrators/", "Demonstrators"],
  ["/ontologies/", "Ontologies"],
  ["/readiness/", "Readiness"],
  ["/roadmap/", "Roadmap"],
  ["/sources/", "Sources"],
  ["/sources/au_mbs/", "Sources"],
]);

const PERFORMANCE_BUDGET = {
  domContentLoadedMs: 5_000,
  transferredBytes: 8_000_000,
};

async function expectNoPageLevelHorizontalOverflow(page: Page) {
  const measurement = await page.evaluate(() => {
    const root = document.documentElement;
    const offenders = [...document.querySelectorAll<HTMLElement>("body *")]
      .filter((element) => {
        const bounds = element.getBoundingClientRect();
        return bounds.right > root.clientWidth + 1 || bounds.left < -1;
      })
      .slice(0, 10)
      .map((element) => ({
        tag: element.tagName.toLowerCase(),
        className: element.className,
        left: element.getBoundingClientRect().left,
        right: element.getBoundingClientRect().right,
      }));
    return {
      clientWidth: root.clientWidth,
      scrollWidth: root.scrollWidth,
      offenders,
    };
  });
  expect(
    measurement.scrollWidth,
    `Page-level overflow detected:\n${JSON.stringify(measurement, null, 2)}`,
  ).toBeLessThanOrEqual(measurement.clientWidth + 1);
}

for (const route of routes) {
  test(`renders public route ${route}`, async ({ browser, page }, testInfo) => {
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
    await expect(page.locator('nav a[aria-current="page"]')).toHaveText(
      navLabelByRoute.get(route) ?? "",
    );
    if (route === "/analyses/cognitive_vs_procedural_ratio/") {
      await expect(page.getByRole("heading", { level: 1 })).toHaveText(
        "Cognitive versus procedural reward index",
      );
    }
    await expectNoPageLevelHorizontalOverflow(page);
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
    const tables = page.locator("table");
    for (let index = 0; index < await tables.count(); index += 1) {
      await expect(tables.nth(index).locator("caption")).toHaveCount(1);
    }

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

    const screenshot = await page.screenshot({ fullPage: true, scale: "css" });
    expect(screenshot.byteLength).toBeGreaterThan(1_000);
    expect(screenshot.byteLength).toBeLessThan(4_000_000);
    await testInfo.attach("route-screenshot", {
      body: screenshot,
      contentType: "image/png",
    });
    await attachReviewContext(browser, page, route, testInfo);

    expect(consoleErrors).toEqual([]);
    expect(pageErrors).toEqual([]);
  });
}

async function attachReviewContext(
  browser: Browser,
  page: Page,
  route: string,
  testInfo: TestInfo,
) {
  await testInfo.attach("dashboard-review-context", {
    body: JSON.stringify({
      route,
      project: testInfo.project.name,
      viewport: page.viewportSize(),
      browser: browser.browserType().name(),
      browserVersion: browser.version(),
    }),
    contentType: "application/json",
  });
}

test("supports skip navigation and visible keyboard focus", async ({ page }, testInfo) => {
  await page.goto("/", { waitUntil: "networkidle" });
  const skipLink = page.getByRole("link", { name: "Skip to main content" });
  if (testInfo.project.name === "desktop-webkit") {
    // Headless WebKit inherits macOS's optional link-tab preference. Explicit focus
    // still verifies the application focus target and keyboard activation path.
    await skipLink.focus();
  } else {
    await page.keyboard.press("Tab");
  }
  await expect(skipLink).toBeFocused();
  await skipLink.press("Enter");
  await expect(page.locator("#main-content")).toBeFocused();

  await page.goto("/", { waitUntil: "networkidle" });
  const graphNav = page.getByRole("navigation", { name: "Dashboard sections" }).getByRole("link", {
    name: "Graph",
  });
  if (testInfo.project.name === "desktop-webkit") {
    await graphNav.focus();
  } else {
    await page.keyboard.press("Tab");
    await page.keyboard.press("Tab");
  }
  await expect(graphNav).toBeFocused();
  const focusStyle = await graphNav.evaluate((element) => {
    const style = getComputedStyle(element);
    return { outlineStyle: style.outlineStyle, outlineWidth: style.outlineWidth };
  });
  expect(focusStyle.outlineStyle).not.toBe("none");
  expect(Number.parseFloat(focusStyle.outlineWidth)).toBeGreaterThan(0);
});

test("keeps the public search control keyboard reachable and announces result counts", async ({
  page,
}) => {
  await page.goto("/sources/", { waitUntil: "networkidle" });
  const firstTable = page.locator('section[data-table-section="true"]').first();
  const filter = firstTable.locator("input[data-table-filter]");
  const rows = firstTable.locator("tr[data-table-row]");
  const results = firstTable.locator('[role="status"][data-table-result-count]');
  await expect(filter).toBeVisible();
  await expect(results).toContainText(/^Showing the first \d+ of \d+ rows\.$/);
  await filter.focus();
  await expect(filter).toBeFocused();

  await filter.fill("au_mbs");
  const matchingRows = rows.filter({ visible: true });
  const matchingCount = await matchingRows.count();
  expect(matchingCount).toBeGreaterThan(0);
  await expect(results).toHaveText(
    `Showing ${matchingCount} matching ${matchingCount === 1 ? "row" : "rows"} of ${await rows.count()}.`,
  );
  await filter.press("Tab");
  await expect(page.locator(":focus")).toHaveCount(1);
  await filter.fill("no-such-dashboard-record");
  await expect(results).toHaveText(`Showing 0 matching rows of ${await rows.count()}.`);
  await filter.fill("");
  await expect(results).toContainText(/^Showing the first \d+ of \d+ rows\.$/);
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

test("provides a semantic graph alternative in every browser", async ({ page }) => {
  await page.goto("/", { waitUntil: "networkidle" });
  const alternative = page.locator("details.graph-alternative");
  await expect(alternative).toBeVisible();
  await alternative.locator("summary").focus();
  await expect(alternative.locator("summary")).toBeFocused();
  await alternative.locator("summary").press("Enter");
  await expect(alternative.getByRole("table", { name: /graph nodes/i })).toBeVisible();
  await expect(alternative.getByRole("link", { name: "complete node CSV" })).toHaveAttribute(
    "href",
    /data\/graph_nodes\.csv$/,
  );
  await expect(alternative.getByRole("link", { name: "complete relationship CSV" })).toHaveAttribute(
    "href",
    /data\/graph_edges\.csv$/,
  );
});

test("keeps tables local and page reflow bounded at 200% and 400% equivalents", async ({
  page,
}) => {
  for (const viewport of [
    { width: 640, height: 900, label: "200%" },
    { width: 320, height: 900, label: "400%" },
  ]) {
    await page.setViewportSize({ width: viewport.width, height: viewport.height });
    for (const route of [
      "/sources/",
      "/sources/au_mbs/",
      "/analyses/cognitive_vs_procedural_ratio/",
      "/readiness/",
    ]) {
      await page.goto(route, { waitUntil: "networkidle" });
      await expectNoPageLevelHorizontalOverflow(page);
      const tables = page.locator(".table-scroll");
      expect(
        await tables.count(),
        `${route} should retain table-local scrolling at the ${viewport.label} equivalent`,
      ).toBeGreaterThan(0);
    }
  }
});
