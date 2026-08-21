import { defineConfig, devices } from "@playwright/test";

const FRONTEND_URL = process.env.PLAYWRIGHT_BASE_URL ?? "http://127.0.0.1:5173";
const API_URL = process.env.PLAYWRIGHT_API_URL ?? "http://127.0.0.1:8000";

/**
 * Workers paralelos: cada teste usa e-mail único e contexto isolado.
 * A API SQLite aguenta concorrência moderada (WAL + busy_timeout).
 *
 * Local:  uvicorn api.main:app --reload  +  npm run test:e2e
 * CI: job sobe a API e o Vite via webServer.
 */
export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  // CI: 2 workers para não saturar SQLite; local: default do Playwright
  workers: process.env.CI ? 2 : process.env.PLAYWRIGHT_WORKERS
    ? Number(process.env.PLAYWRIGHT_WORKERS)
    : undefined,
  reporter: process.env.CI ? [["github"], ["list"]] : "list",
  timeout: 60_000,
  expect: { timeout: 15_000 },
  use: {
    baseURL: FRONTEND_URL,
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    // Contexto limpo por teste (sem cookies/storage compartilhados)
    storageState: undefined,
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  webServer: process.env.PLAYWRIGHT_SKIP_WEBSERVER
    ? undefined
    : {
        command: "npm run dev -- --host 127.0.0.1 --port 5173",
        url: FRONTEND_URL,
        reuseExistingServer: !process.env.CI,
        timeout: 120_000,
      },
  metadata: {
    apiUrl: API_URL,
  },
});
