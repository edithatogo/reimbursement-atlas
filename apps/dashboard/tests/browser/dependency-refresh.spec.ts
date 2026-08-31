import { expect, test } from "@playwright/test";

test("compatible Cosmograph refresh renders graph data without page errors", async ({
  page,
  browserName,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto("/", { waitUntil: "domcontentloaded" });
  if (browserName === "firefox") {
    const fallback = page.getByRole("region", {
      name: "Graph renderer fallback",
    });
    await expect(fallback).toBeVisible();
    await expect(fallback).toContainText(
      /The generated graph contains [1-9]\d* nodes and [1-9]\d* edges/,
    );
  } else {
    await expect(
      page.getByText(/Loaded \d+ nodes and \d+ edges/),
    ).toBeVisible();
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
