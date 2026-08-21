# BibleLingo

O BibleLingo é um aplicativo para estudar inglês por meio da leitura da **World English Bible (WEB)**. A pessoa lê um capítulo, ouve o inglês, salva palavras no vocabulário e pratica com um quiz curto.

Há dois clientes da mesma camada de domínio:
- **CLI** (`python main.py`) — terminal interativo
- **API** (`uvicorn api.main:app`) — FastAPI para futuros frontends

## O que já funciona

| Área | Comportamento atual |
| --- | --- |
| Leitura | Carrega Gênesis 1 e formata versículos. |
| Vocabulário | Origem, revisões, acertos, erros e próxima data de revisão. |
| Revisão espaçada | Intervalos 1, 3, 7, 14 e 30 dias; erros voltam para hoje. |
| Quiz | Opções únicas no idioma escolhido. |
| Áudio | edge-tts com cache (opcional). |
| Gamificação | XP, níveis, streak e percentual até o próximo nível. |
| Idiomas | pt, es, en, ar, he (com RTL). |
| Domínio puro | `app/domain/` sem input/print/JSON. |
| API | FastAPI com `/health`, `/v1/progress` e `/v1/chapters`. |

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

Documentação interativa: http://127.0.0.1:8000/docs

| Método | Rota | Descrição |
| --- | --- | --- |
| GET | `/health` | Status do serviço |
| GET | `/v1/progress` | XP, nível, streak e progresso até o próximo nível |
| GET | `/v1/chapters` | Lista de livros disponíveis |
| GET | `/v1/chapters/{book}/{chapter}` | Versículos do capítulo (ex: `/v1/chapters/genesis/1`) |

O domínio de regras permanece em `app/domain/`. Os repositórios da API ainda usam JSON local; na próxima fase viram SQLite/PostgreSQL sem mudar as rotas.

## Testes

```bash
python -m unittest discover -s tests -v
```

## Estrutura

```text
biblelingo/
├── app/
│   ├── domain/           # regras puras (XP, vocab, quiz)
│   ├── progress.py       # adaptador CLI
│   ├── vocabulary.py
│   ├── quiz.py
│   ├── bible_loader.py
│   ├── parser.py
│   ├── audio.py
│   ├── languages.py
│   └── rtl.py
├── api/
│   ├── main.py           # FastAPI app
│   ├── schemas/          # Pydantic
│   ├── repositories/     # persistência (JSON por enquanto)
│   └── routes/           # health, progress, chapters
├── data/
├── tests/
├── main.py               # CLI
└── requirements.txt
```

## Próximos passos

1. Migrações + SQLite (repositórios reais por usuário)
2. Sessão de revisão com `POST /v1/reviews/answer` atômico e idempotente
3. Autenticação
4. Vertical slice do frontend (login → leitura → quiz → progresso)

## Licença e conteúdo

A WEB é domínio público. Consulte atribuições antes de distribuir novos capítulos ou traduções.
