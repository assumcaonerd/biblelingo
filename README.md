# BibleLingo

Aprenda inglês lendo e ouvindo a Bíblia (World English Bible).

Clientes da mesma camada de domínio:

- **CLI** — `python main.py`
- **API** — FastAPI + JWT + SQLite
- **Frontend** — React (Vite) com login → leitura → quiz → progresso

## Subir tudo (desenvolvimento)

Terminal 1 — API:

```bash
pip install -r requirements.txt
uvicorn api.main:app --reload
```

Terminal 2 — Frontend:

```bash
cd frontend
npm install
npm run dev
```

Abra http://127.0.0.1:5173

## CI

Todo push e pull request em `main` dispara GitHub Actions:

- **Backend:** `compileall`, validação dos JSONs em `data/`, `unittest`
- **Frontend:** `npm install` / `npm ci` e `npm run build`

## Sessão JWT

O frontend revalida o token com `GET /v1/me` ao carregar.

| Situação | Comportamento |
| --- | --- |
| Token válido | Dashboard normal |
| 401 | Limpa sessão e pede login |
| API fora | Mantém sessão local e avisa |

## Fluxo do vertical slice

1. Criar conta ou entrar
2. Dashboard (nível, XP, streak)
3. Ler Gênesis 1
4. Praticar palavras via `GET /v1/reviews/due` + `POST /v1/reviews/answer`
5. Ver progresso atualizado

## API (resumo)

| Método | Rota | Auth |
| --- | --- | --- |
| POST | `/v1/auth/register` | público |
| POST | `/v1/auth/login` | público |
| GET | `/v1/me` | JWT |
| GET | `/v1/progress` | JWT |
| GET | `/v1/reviews/due` | JWT |
| POST | `/v1/reviews/answer` | JWT |
| GET | `/v1/chapters/{book}/{chapter}` | público |
| GET | `/health` | público |

Docs: http://127.0.0.1:8000/docs

## Testes

```bash
python -m unittest discover -s tests -v
```

## Próximos passos (auditoria)

1. ~~CI/CD~~
2. ~~Sessão JWT robusta~~
3. Seed idempotente por capítulo (leitura → vocabulário → prática)
4. Áudio no frontend
5. Dashboard com meta diária
6. Expansão controlada de capítulos
7. Produção (segredo forte, HTTPS, backups)

## Licença

WEB em domínio público. Consulte atribuições antes de distribuir novos capítulos.
