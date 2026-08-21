import { defineConfig, devices } from "@playwright/test";

const FRONTEND_URL = process.env.PLAYWRIGHT_BASE_URL ?? "http://127.0.0.1:5173";
const API_URL = process.env.PLAYWRIGHT_API_URL ?? "http://127.0.0.1:8000";

/**
 * E2E exige API + frontend no ar.
 * Local:  terminal 1 → uvicorn api.main:app --reload
 *         terminal 2 → npm run dev
 *         npm run test:e2e
 *
 * CI: o job sobe ambos antes do Playwright.
 */
export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  reporter: process.env.CI ? "github" : "list",
  timeout: 60_000,
  expect: { timeout: 15_000 },
  use: {
    baseURL: FRONTEND_URL,
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  webServer: process.env.PLAYWRIGHT_SKIP_WEBSERVER
    ? undefined
    : [
        {
          command: "npm run dev -- --host 127.0.0.1 --port 5173",
          url: FRONTEND_URL,
          reuseExistingServer: !process.env.CI,
          timeout: 120_000,
        },
      ],
  metadata: {
    apiUrl: API_URL,
  },
});
