# BibleLingo

O BibleLingo é um aplicativo para estudar inglês por meio da leitura da **World English Bible (WEB)**. A pessoa lê um capítulo, ouve o inglês, salva palavras no vocabulário e pratica com um quiz curto.

Há dois clientes da mesma camada de domínio:

- **CLI** (`python main.py`) — terminal interativo.
- **API** (`uvicorn api.main:app`) — FastAPI para futuros frontends.

## O que já funciona

| Área | Comportamento atual |
| --- | --- |
| Leitura | Carrega Gênesis 1 e formata versículos. |
| Vocabulário | Origem, revisões, acertos, erros e próxima data de revisão. |
| Revisão espaçada | Intervalos de 1, 3, 7, 14 e 30 dias; erros voltam para hoje. |
| Quiz | Opções únicas no idioma escolhido, com contexto bíblico e distratores únicos. |
| Áudio | `edge-tts` com cache, de forma opcional e não bloqueante. |
| Gamificação | XP, níveis, streak diário, bônus de streak e percentual até o próximo nível. |
| Idiomas | Português, espanhol, inglês, árabe e hebraico, com suporte a RTL. |
| Domínio puro | `app/domain/` concentra as regras sem `input()`, `print()` ou persistência. |
| Persistência da API | SQLite com WAL, migração de JSON legado e transações explícitas. |
| Revisão da API | `POST /v1/reviews/answer` atômico e idempotente por chave. |

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

Documentação interativa: <http://127.0.0.1:8000/docs>.

| Método | Rota | Descrição |
| --- | --- | --- |
| GET | `/health` | Status do serviço. |
| GET | `/v1/progress` | XP, nível, streak e progresso até o próximo nível. |
| GET | `/v1/chapters` | Lista de livros disponíveis. |
| GET | `/v1/chapters/{book}/{chapter}` | Versículos do capítulo, por exemplo `/v1/chapters/genesis/1`. |
| POST | `/v1/reviews/answer` | Valida a tradução no servidor e registra a revisão atomicamente. |

A API aceita o header opcional `X-User-ID`. Enquanto não há autenticação formal, o valor padrão é `default`; os dados de progresso, vocabulário e eventos são isolados por esse identificador.

O banco padrão é `data/biblelingo.db`. Para testes ou execução em outro ambiente, use `BIBLELINGO_DB_PATH` para apontar para um arquivo SQLite diferente. Os arquivos do banco e do WAL são ignorados pelo Git.

### Exemplo de revisão

```bash
curl -X POST http://127.0.0.1:8000/v1/reviews/answer \
  -H 'Content-Type: application/json' \
  -H 'X-User-ID: demo' \
  -d '{
    "word": "light",
    "selected": "luz",
    "native_lang": "pt",
    "idempotency_key": "demo-light-001"
  }'
```

A mesma requisição com a mesma `idempotency_key` retorna o resultado já processado sem conceder XP novamente. A resposta correta concede 10 XP; respostas erradas registram a revisão sem XP e mantêm a próxima revisão para hoje.

## Testes

```bash
python -m unittest discover -s tests -v
```

A suíte cobre os contratos puros de domínio e os endpoints da API, incluindo startup do banco, health, capítulos, progresso, respostas corretas e erradas, idempotência, ausência de XP duplicado e isolamento entre usuários.

## Estrutura

```text
biblelingo/
├── app/
│   ├── domain/           # regras puras de XP, vocabulário e quiz
│   ├── progress.py       # adaptador CLI
│   ├── vocabulary.py
│   ├── quiz.py
│   ├── bible_loader.py
│   ├── parser.py
│   ├── audio.py
│   ├── languages.py
│   └── rtl.py
├── api/
│   ├── main.py           # aplicação FastAPI e startup SQLite
│   ├── database.py       # schema, conexão e inicialização SQLite
│   ├── dependencies.py   # isolamento lógico por X-User-ID
│   ├── schemas/          # contratos Pydantic
│   ├── repositories/     # persistência SQLite e conteúdo WEB
│   └── routes/           # health, progresso, capítulos e revisão
├── data/
├── tests/
├── main.py               # CLI
├── requirements.txt
└── WEB_MIGRATION_ROADMAP.md
```

## Próximos passos

1. Autenticação formal e emissão de identidade confiável por usuário.
2. Vertical slice do frontend: login, leitura, quiz e progresso.
3. Áudio e preferências de idioma expostos pela API.
4. CI, observabilidade, migrações versionadas e deploy.

## Licença e conteúdo

A WEB é domínio público. Consulte atribuições antes de distribuir novos capítulos ou traduções.
