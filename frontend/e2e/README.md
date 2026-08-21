# Testes E2E (Playwright)

Cobrem o fluxo real no browser: **criar conta → dashboard → ler Gênesis 1 → seed → prática**.

Os testes rodam em **paralelo** (`fullyParallel: true`). Cada caso cria um usuário com e-mail único e contexto de browser isolado.

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

Paralelismo local (ex.: 4 workers):

```bash
PLAYWRIGHT_WORKERS=4 npm run test:e2e
```

Sequencial (debug):

```bash
npx playwright test --workers=1
```

UI interativa:

```bash
npm run test:e2e:ui
```

## Variáveis

| Variável | Padrão |
| --- | --- |
| `PLAYWRIGHT_BASE_URL` | `http://127.0.0.1:5173` |
| `PLAYWRIGHT_API_URL` | `http://127.0.0.1:8000` |
| `PLAYWRIGHT_WORKERS` | default do Playwright (local); `2` no CI |
| `PLAYWRIGHT_SKIP_WEBSERVER` | se definido, não sobe o Vite |

## CI

O job `e2e` sobe a API, instala Chromium e executa com **2 workers** para equilibrar velocidade e carga no SQLite.
