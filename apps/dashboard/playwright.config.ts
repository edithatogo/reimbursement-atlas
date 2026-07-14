import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/browser",
  timeout: 30_000,
  fullyParallel: true,
  outputDir: "../test-results",
  reporter: [["list"], ["html", { open: "never", outputFolder: "../playwright-report" }]],
  use: {
    baseURL: "http://127.0.0.1:4321",
    browserName: "chromium",
    ...devices["Desktop Chrome"],
    screenshot: "only-on-failure",
    trace: "retain-on-failure",
  },
  webServer: {
    command: "npm run preview -- --host 127.0.0.1",
    url: "http://127.0.0.1:4321",
    reuseExistingServer: !process.env.CI,
    timeout: 30_000,
  },
});
