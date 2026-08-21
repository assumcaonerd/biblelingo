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

O Vite faz proxy de `/api` para a API em `:8000`. CORS também está liberado para o dev server.

## Fluxo do vertical slice

1. Criar conta ou entrar
2. Ver dashboard (nível, XP, streak)
3. Ler Gênesis 1
4. Praticar palavras (respostas vão para `POST /v1/reviews/answer`)
5. Voltar ao dashboard e ver o progresso atualizado

## API (resumo)

| Método | Rota | Auth |
| --- | --- | --- |
| POST | `/v1/auth/register` | público |
| POST | `/v1/auth/login` | público |
| GET | `/v1/me` | JWT |
| GET | `/v1/progress` | JWT |
| POST | `/v1/reviews/answer` | JWT |
| GET | `/v1/chapters/{book}/{chapter}` | público |
| GET | `/health` | público |

Docs: http://127.0.0.1:8000/docs

## CLI

```bash
python main.py
```

## Testes

```bash
python -m unittest discover -s tests -v
```

## Estrutura

```text
biblelingo/
├── app/domain/       # regras puras
├── api/              # FastAPI + SQLite + JWT
├── frontend/         # React + Vite
├── tests/
└── main.py           # CLI
```

## Próximos passos

- `GET /v1/reviews/due` alimentando o quiz pelo servidor
- Áudio no frontend
- CI, migrações versionadas e deploy

## Licença

WEB em domínio público. Consulte atribuições antes de distribuir novos capítulos.
