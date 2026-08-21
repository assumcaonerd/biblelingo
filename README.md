# BibleLingo

Aprenda inglês lendo, ouvindo e praticando a **World English Bible (WEB)**. Combina leitura contextual, pronúncia, vocabulário, revisão espaçada e gamificação leve.

Licença: **[MIT](LICENSE)** · Conteúdo bíblico: WEB (domínio público)

## Estrutura do monorepo

| Pasta | Função | Detalhes |
| --- | --- | --- |
| [`frontend/`](frontend/README.md) | UI React 18 + Vite 5 + TypeScript | Login, leitura, áudio, quiz, dashboard |
| [`api/`](api/README.md) | FastAPI + JWT + SQLite | HTTP, auth, persistência |
| [`app/domain/`](app/domain/) | Domínio puro em Python | Progresso, vocabulário, quiz (sem I/O) |
| [`tests/`](tests/) | `unittest` | API, integração do fluxo, dashboard |
| [`data/`](data/) | WEB samples + dicionários | JSON versionado (leve) |

## Requisitos mínimos

**Opção A — Docker (recomendado para experimentar rápido)**

- Docker + Docker Compose

**Opção B — nativo**

- **Python** >= 3.12
- **Node.js** >= 18

## Subir com Docker (um comando)

```bash
docker compose up --build
```

| Serviço | URL |
| --- | --- |
| App | http://127.0.0.1:3000 |
| API | http://127.0.0.1:8000 |
| Docs | http://127.0.0.1:8000/docs |

- Nginx do frontend faz proxy de `/api` → container `api` (mesmo contrato do Vite).
- SQLite persiste no volume `biblelingo_data`.
- Opcional: `cp .env.example .env` e ajuste `BIBLELINGO_SECRET_KEY` antes do up.

Parar: `docker compose down` (mantém o volume). Remover dados: `docker compose down -v`.

## Subir nativo (dois terminais)

**Terminal 1 — API** (na raiz):

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # opcional em development
uvicorn api.main:app --reload
```

**Terminal 2 — Frontend:**

```bash
cd frontend
npm ci
cp .env.example .env        # opcional
npm run dev
```

- App: http://127.0.0.1:5173  
- API: http://127.0.0.1:8000  

Variáveis: [`.env.example`](.env.example), [`api/.env.example`](api/.env.example), [`frontend/.env.example`](frontend/.env.example).

## Fluxo pedagógico

| Etapa | Comportamento |
| --- | --- |
| Conta | Registro, login e revalidação JWT em `/v1/me` |
| Leitura | Gênesis 1 / Salmos 23, áudio por versículo ou capítulo |
| Vocabulário | `POST /v1/vocabulary/seed` (idempotente) |
| Prática | `GET /v1/reviews/due` + `POST /v1/reviews/answer` |
| Progresso | XP, streak, dashboard (`GET /v1/dashboard`) |

## Conteúdo disponível

| Lição | Conteúdo |
| --- | --- |
| Gênesis 1 | Sample WEB + dicionário base |
| Salmos 23 | `data/psalms_sample.json` + `data/dictionary_psalms23.json` |

Traduções: português, espanhol, inglês, árabe e hebraico.

## API principal

| Método | Rota | Auth |
| --- | --- | --- |
| POST | `/v1/auth/register` | público |
| POST | `/v1/auth/login` | público |
| GET | `/v1/me` | JWT |
| GET | `/v1/dashboard` | JWT |
| POST | `/v1/vocabulary/seed` | JWT |
| GET | `/v1/reviews/due` | JWT |
| POST | `/v1/reviews/answer` | JWT |
| GET | `/v1/chapters/{book}/{chapter}` | público |
| GET | `/health` | público |

## Testes e CI

```bash
python -m compileall app api tests main.py
python -m unittest discover -s tests -v
cd frontend && npm ci && npm run build
```

GitHub Actions (`.github/workflows/ci.yml`) roda isso em todo push/PR na `main`.

## Produção

Ver [`PRODUCTION_RUNBOOK.md`](PRODUCTION_RUNBOOK.md). Em production: `BIBLELINGO_SECRET_KEY` forte (≥ 32 chars), CORS sem `*`, SQLite em disco persistente.

## Contribuição

1. Leia o README da camada que for alterar (`frontend/` ou `api/`).
2. Mantenha testes verdes e o build do frontend passando.
3. Não versionar `.env`, segredos ou backups.

## Licença e conteúdo

Código sob [MIT](LICENSE). Textos da World English Bible em domínio público — confirme a fonte antes de distribuir novos capítulos.
