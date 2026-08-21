# BibleLingo — API

Backend FastAPI: autenticação JWT, progresso, vocabulário, revisão espaçada e dashboard.

O núcleo de regras fica em [`app/domain/`](../app/domain/) (sem `print`/`input`). Esta pasta (`api/`) expõe HTTP, SQLite e autenticação.

## Tecnologias

- Python >= 3.12
- FastAPI + Pydantic
- SQLite (transacional, WAL)
- JWT (`python-jose` + `passlib[bcrypt]`)

## Requisitos

- **Python** >= 3.12

## Instalação e execução

Os comandos rodam **a partir da raiz do monorepo** (é de lá que o pacote `api` e `app` são importados):

```bash
# na raiz do repositório
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # opcional em development
uvicorn api.main:app --reload
```

- API: http://127.0.0.1:8000  
- Docs interativas: http://127.0.0.1:8000/docs  
- Health: http://127.0.0.1:8000/health  

## Variáveis de ambiente

Veja [`.env.example`](../.env.example) na raiz. Principais:

| Variável | Uso |
| --- | --- |
| `BIBLELINGO_ENV` | `development`, `test` ou `production` |
| `BIBLELINGO_SECRET_KEY` | Segredo JWT (**obrigatório** e forte em production) |
| `BIBLELINGO_TOKEN_HOURS` | Validade do token |
| `BIBLELINGO_CORS_ORIGINS` | Origens permitidas (sem `*` em production) |
| `BIBLELINGO_DB_PATH` | Caminho do SQLite (padrão `data/biblelingo.db`) |

## Endpoints principais

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

## Testes

Na raiz, com o venv ativo:

```bash
python -m unittest discover -s tests -v
```

A suíte cobre autenticação, isolamento entre usuários, seed idempotente, revisão idempotente, dashboard e o fluxo completo ler → seed → due → answer → progresso.

## Produção

Consulte [`PRODUCTION_RUNBOOK.md`](../PRODUCTION_RUNBOOK.md) na raiz. Não versionar `.env`, tokens ou backups.
