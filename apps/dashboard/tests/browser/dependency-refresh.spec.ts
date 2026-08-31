import { expect, test } from "@playwright/test";

test("compatible Cosmograph refresh mounts a canvas without page errors", async ({
  page,
  browserName,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto("/", { waitUntil: "domcontentloaded" });
  await expect(page.getByText(/Loaded \d+ nodes and \d+ edges/)).toBeVisible();
  if (browserName === "firefox") {
    await expect(
      page.getByRole("region", { name: "Graph renderer fallback" }),
    ).toBeVisible();
  } else {
    const canvas = page.locator(".graph-visual canvas").first();
    await expect(canvas).toBeVisible();
    await expect
      .poll(() =>
        canvas.evaluate((element) => (element as HTMLCanvasElement).width),
      )
      .toBeGreaterThan(0);
  }
  await expect(page.locator("details.graph-alternative")).toBeVisible();
  expect(errors).toEqual([]);
});
