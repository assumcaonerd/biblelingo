import { expect, type APIRequestContext } from "@playwright/test";

/** E-mail único por worker/teste — evita colisão em execução paralela. */
export function uniqueEmail(prefix = "e2e"): string {
  const rand = Math.random().toString(36).slice(2, 8);
  return `${prefix}.${Date.now()}.${rand}@example.com`;
}

export async function assertApiHealthy(request: APIRequestContext): Promise<void> {
  const api = process.env.PLAYWRIGHT_API_URL ?? "http://127.0.0.1:8000";
  const health = await request.get(`${api}/health`);
  expect(
    health.ok(),
    `API indisponível em ${api}/health — suba com: uvicorn api.main:app --reload`
  ).toBeTruthy();
}
