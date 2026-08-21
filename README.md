# BibleLingo

O BibleLingo é um aplicativo para estudar inglês por meio da leitura da **World English Bible (WEB)**. A pessoa lê um capítulo, ouve o inglês, salva palavras no vocabulário e pratica com um quiz curto.

Há dois clientes da mesma camada de domínio:

- **CLI** (`python main.py`) — terminal interativo.
- **API** (`uvicorn api.main:app`) — FastAPI com autenticação JWT.

## O que já funciona

| Área | Comportamento atual |
| --- | --- |
| Leitura | Gênesis 1 e formatação de versículos. |
| Vocabulário | Origem, revisões, acertos, erros e próxima data. |
| Revisão espaçada | Intervalos 1, 3, 7, 14 e 30 dias. |
| Quiz / revisão API | Opções únicas, validação no servidor, XP atômico. |
| Áudio | edge-tts com cache (opcional). |
| Gamificação | XP, níveis, streak e percentual até o próximo nível. |
| Idiomas | pt, es, en, ar, he (RTL). |
| Domínio puro | `app/domain/` sem input/print/persistência. |
| Persistência | SQLite com WAL e transações. |
| **Autenticação** | Cadastro, login, JWT Bearer, `/v1/me`. |

## CLI

```bash
git clone https://github.com/assumcaonerd/biblelingo.git
cd biblelingo
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## API FastAPI

```bash
pip install -r requirements.txt
uvicorn api.main:app --reload
```

Docs: http://127.0.0.1:8000/docs

### Autenticação

| Método | Rota | Descrição |
| --- | --- | --- |
| POST | `/v1/auth/register` | Cria conta e devolve token |
| POST | `/v1/auth/login` | Login e token |
| GET | `/v1/me` | Perfil do usuário autenticado |

Rotas protegidas (progresso e revisão) exigem:

```http
Authorization: Bearer <access_token>
```

### Outras rotas

| Método | Rota | Auth |
| --- | --- | --- |
| GET | `/health` | público |
| GET | `/v1/chapters` | público |
| GET | `/v1/chapters/{book}/{chapter}` | público |
| GET | `/v1/progress` | JWT |
| POST | `/v1/reviews/answer` | JWT |

### Exemplo rápido

```bash
# Registrar
curl -X POST http://127.0.0.1:8000/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"voce@email.com","password":"secreta123","native_language":"pt"}'

# Usar o access_token retornado
TOKEN=...

curl http://127.0.0.1:8000/v1/progress \
  -H "Authorization: Bearer $TOKEN"

curl -X POST http://127.0.0.1:8000/v1/reviews/answer \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"word":"light","selected":"luz","native_lang":"pt","idempotency_key":"demo-1"}'
```

Em produção defina `BIBLELINGO_SECRET_KEY` (chave forte para JWT).

Banco padrão: `data/biblelingo.db` (ou `BIBLELINGO_DB_PATH`).

## Testes

```bash
python -m unittest discover -s tests -v
```

## Estrutura

```text
biblelingo/
├── app/domain/          # regras puras
├── api/
│   ├── auth.py          # bcrypt + JWT
│   ├── database.py      # SQLite + tabela users
│   ├── dependencies.py  # get_current_user / get_user_id
│   ├── repositories/    # users, progress, vocabulary, review
│   ├── schemas/
│   └── routes/          # auth, progress, chapters, reviews
├── tests/
└── main.py              # CLI
```

## Próximos passos

1. Vertical slice do frontend (login → leitura → quiz → progresso)
2. Áudio e preferências pela API
3. CI, migrações versionadas, observabilidade e deploy

## Licença e conteúdo

A WEB é domínio público. Consulte atribuições antes de distribuir novos capítulos.
