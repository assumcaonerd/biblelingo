import { test, expect } from "@playwright/test";

/**
 * Fluxo pedagógico ponta a ponta:
 * registrar → dashboard → ler → seed → praticar (se houver fila).
 *
 * Pré-requisito: API em http://127.0.0.1:8000 respondendo /health.
 */

test.beforeAll(async ({ request }) => {
  const api = process.env.PLAYWRIGHT_API_URL ?? "http://127.0.0.1:8000";
  const health = await request.get(`${api}/health`);
  expect(
    health.ok(),
    `API indisponível em ${api}/health — suba com: uvicorn api.main:app --reload`
  ).toBeTruthy();
});

test("registrar, ver dashboard e abrir leitor", async ({ page }) => {
  const email = `e2e.${Date.now()}@example.com`;
  const password = "secret123";

  await page.goto("/auth");
  await expect(page.getByRole("heading", { name: "BibleLingo" })).toBeVisible();

  await page.getByRole("button", { name: "Criar conta" }).click();
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Senha").fill(password);
  await page.getByRole("button", { name: "Criar conta" }).click();

  await expect(page).toHaveURL(/\/$/);
  await expect(page.getByRole("heading", { name: /Olá/i })).toBeVisible({
    timeout: 20_000,
  });
  await expect(page.getByText(/Seu resumo de aprendizagem/i)).toBeVisible();

  await page.getByRole("link", { name: /Ler Gênesis 1/i }).click();
  await expect(page).toHaveURL(/\/read/);
  await expect(page.getByRole("heading", { name: /Genesis 1/i })).toBeVisible();
  await expect(page.getByText(/In the beginning/i)).toBeVisible();
});

test("seed do capítulo e tela de prática", async ({ page }) => {
  const email = `e2e.practice.${Date.now()}@example.com`;
  const password = "secret123";

  await page.goto("/auth");
  await page.getByRole("button", { name: "Criar conta" }).click();
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Senha").fill(password);
  await page.getByRole("button", { name: "Criar conta" }).click();
  await expect(page.getByRole("heading", { name: /Olá/i })).toBeVisible({
    timeout: 20_000,
  });

  await page.goto("/read");
  await expect(page.getByRole("heading", { name: /Genesis 1/i })).toBeVisible();

  await page.getByRole("button", { name: /Praticar palavras deste capítulo/i }).click();

  // Seed + redirect para /review
  await expect(page).toHaveURL(/\/review/, { timeout: 30_000 });

  // Ou há perguntas, ou mensagem de fila vazia (ambos válidos após seed)
  const pratica = page.getByRole("heading", { name: /Prática/i });
  const vazia = page.getByText(/Nenhuma palavra para revisar agora/i);
  await expect(pratica.or(vazia)).toBeVisible({ timeout: 20_000 });
});
