# BibleLingo

Aprenda inglês lendo e ouvindo a Bíblia (World English Bible).

Clientes da mesma camada de domínio:

- **CLI** — `python main.py`
- **API** — FastAPI + JWT + SQLite
- **Frontend** — React (Vite): login → leitura → áudio → quiz → dashboard

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

Todo push/PR em `main`:

- Backend: `compileall`, JSON em `data/`, `unittest`
- Frontend: `npm ci`/`install` + `npm run build`

## Fluxo

1. Conta / login (JWT revalidado em `/v1/me`)
2. Dashboard (`GET /v1/dashboard`) — XP, streak, meta diária, acerto, atividade
3. Ler Gênesis 1 (áudio por versículo e capítulo inteiro)
4. Seed idempotente (`POST /v1/vocabulary/seed`)
5. Praticar (`GET /v1/reviews/due` + `POST /v1/reviews/answer`) com áudio da palavra
6. Progresso atualizado

## Áudio

Pronúncia no frontend via **Web Speech API** (`en-US`):

- Leitor: botão por versículo e “Ouvir capítulo”
- Prática: “Ouvir palavra” / “Ouvir versículo”
- Falha não bloqueia o quiz (mensagem discreta)

## API (resumo)

| Método | Rota | Auth |
| --- | --- | --- |
| POST | `/v1/auth/register` | público |
| POST | `/v1/auth/login` | público |
| GET | `/v1/me` | JWT |
| GET | `/v1/dashboard` | JWT |
| GET | `/v1/progress` | JWT |
| POST | `/v1/vocabulary/seed` | JWT |
| GET | `/v1/reviews/due` | JWT |
| POST | `/v1/reviews/answer` | JWT |
| GET | `/v1/chapters/{book}/{chapter}` | público |
| GET | `/health` | público |

## Testes

```bash
python -m unittest discover -s tests -v
```

## Licença

WEB em domínio público. Consulte atribuições antes de distribuir novos capítulos.
