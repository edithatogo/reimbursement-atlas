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
    screenshot: "only-on-failure",
    trace: "retain-on-failure",
  },
  projects: [
    {
      name: "desktop-chromium",
      use: { ...devices["Desktop Chrome"] },
    },
    {
      name: "mobile-chromium",
      use: { ...devices["Pixel 5"] },
    },
    {
      name: "desktop-firefox",
      use: { ...devices["Desktop Firefox"], browserName: "firefox" },
    },
    {
      name: "desktop-webkit",
      use: { ...devices["Desktop Safari"], browserName: "webkit" },
    },
  ],
  webServer: {
    command: "npm run preview -- --host 127.0.0.1",
    url: "http://127.0.0.1:4321",
    reuseExistingServer: !process.env.CI,
    timeout: 30_000,
  },
});
