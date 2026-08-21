# Testes E2E (Playwright)

Cobrem o fluxo real no browser: **criar conta → dashboard → ler Gênesis 1 → seed → prática**.

## Pré-requisitos

1. API no ar:

```bash
# na raiz do monorepo
uvicorn api.main:app --reload
```

2. Dependências do frontend + browser:

```bash
cd frontend
npm install
npx playwright install chromium
```

## Rodar

```bash
cd frontend
npm run test:e2e
```

O Playwright sobe o Vite (`npm run dev`) automaticamente, a menos que já exista servidor em `:5173`.

UI interativa:

```bash
npm run test:e2e:ui
```

## Variáveis

| Variável | Padrão |
| --- | --- |
| `PLAYWRIGHT_BASE_URL` | `http://127.0.0.1:5173` |
| `PLAYWRIGHT_API_URL` | `http://127.0.0.1:8000` |
| `PLAYWRIGHT_SKIP_WEBSERVER` | se definido, não sobe o Vite |

## CI

O job `e2e` no GitHub Actions sobe a API, instala Chromium e executa a suíte após os jobs backend e frontend.
