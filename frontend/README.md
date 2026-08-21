# BibleLingo — Frontend

Interface web do BibleLingo: login, leitura bíblica, áudio, prática de vocabulário e dashboard.

## Tecnologias

- React 18 + TypeScript
- Vite 5
- React Router 6
- Vitest (testes do cliente HTTP)
- Web Speech API (`en-US`) para pronúncia no navegador

## Requisitos

- **Node.js** >= 18

## Instalação e execução

A API precisa estar rodando em `http://127.0.0.1:8000` (veja o [README da API](../api/README.md) ou a raiz do monorepo).

```bash
cd frontend
npm ci   # ou: npm install
cp .env.example .env   # opcional — o proxy do Vite já aponta /api para :8000
npm run dev
```

Abra http://127.0.0.1:5173

### Variáveis de ambiente

| Variável | Padrão | Descrição |
| --- | --- | --- |
| `VITE_API_URL` | `/api` | Base das chamadas HTTP. Em dev, o Vite faz proxy de `/api` para a API. |

## Scripts

| Comando | Função |
| --- | --- |
| `npm run dev` | Servidor de desenvolvimento |
| `npm run build` | Typecheck (`tsc`) + build de produção |
| `npm run preview` | Serve o build localmente |
| `npm test` | Vitest (uma passagem) |
| `npm run test:watch` | Vitest em modo watch |
| `npm run lint` | ESLint |

## Tipos e mocks

- Contratos: [`src/types/api.ts`](src/types/api.ts) (espelho de `api/schemas/`)
- Fixtures tipadas: [`src/test/fixtures.ts`](src/test/fixtures.ts)
- Exemplo: [`src/api.test.ts`](src/api.test.ts)

## Estrutura útil

```text
src/
  api.ts              # Cliente HTTP tipado
  api.test.ts         # Testes Vitest com fetch mockado
  auth.tsx            # Sessão JWT + revalidação /v1/me
  types/api.ts        # Contratos TS ↔ Pydantic
  test/fixtures.ts    # Payloads de mock
  components/         # SpeakButton, etc.
  pages/              # Auth, Dashboard, Reader, Review
```

## Contribuição

1. `npm test` e `npm run build` devem passar.
2. Não comite `.env` — use apenas `.env.example`.
3. Novos endpoints: atualize `types/api.ts` e, se fizer sentido, `test/fixtures.ts`.
