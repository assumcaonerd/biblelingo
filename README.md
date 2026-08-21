# BibleLingo

Aprenda inglês lendo, ouvindo e praticando a **World English Bible (WEB)**. O BibleLingo combina leitura contextual, pronúncia em inglês, vocabulário pessoal, revisão espaçada e gamificação leve em uma única experiência.

A arquitetura mantém uma camada de domínio compartilhada por três clientes: o **CLI** (`python main.py`), a **API** FastAPI com JWT e SQLite transacional, e o **frontend** React/Vite com login, leitura, áudio, quiz e dashboard.

## Conteúdo disponível

Cada lição é composta por texto WEB, contexto bíblico preservado no vocabulário e traduções completas para português, espanhol, inglês, árabe e hebraico. O carregador modular mescla `data/dictionary.json` com arquivos adicionais no formato `data/dictionary_*.json`.

| Lição | Conteúdo | Prática |
| --- | --- | --- |
| Gênesis 1 | Sample WEB para desenvolvimento e testes | Seed idempotente e revisão contextual |
| Salmos 23 | Seis versículos WEB em `data/psalms_sample.json` | 54 entradas traduzidas em `data/dictionary_psalms23.json` |

A expansão de capítulos é deliberadamente controlada: cada novo capítulo deve incluir o sample WEB, as traduções nos cinco idiomas, os testes de API/domínio e a opção correspondente no leitor.

## Fluxo pedagógico

| Etapa | Comportamento |
| --- | --- |
| Conta | Registro, login e revalidação JWT em `/v1/me` |
| Leitura | Seleção de Gênesis 1 ou Salmos 23, com áudio por versículo ou capítulo |
| Vocabulário | Seed no servidor, com origem e contexto do primeiro aparecimento da palavra |
| Prática | Perguntas de múltipla escolha vindas de `GET /v1/reviews/due` |
| Revisão | Resposta atômica e idempotente em `POST /v1/reviews/answer` |
| Progresso | XP, níveis, streak diário, bônus de streak e dashboard de atividade |

## Subir em desenvolvimento

Na raiz do projeto, instale as dependências e inicie a API:

```bash
pip install -r requirements.txt
uvicorn api.main:app --reload
```

Em outro terminal, inicie o frontend:

```bash
cd frontend
npm ci
npm run dev
```

Abra <http://127.0.0.1:5173>. A API fica disponível em <http://127.0.0.1:8000>, com documentação interativa em `/docs`.

## Áudio e acessibilidade

A pronúncia no frontend usa a **Web Speech API** com voz `en-US`, sem depender de uma chamada ao backend. O leitor oferece “Ouvir capítulo” e um botão por versículo; a prática oferece áudio da palavra, do versículo e repetição após a resposta. Se o navegador não oferecer uma voz compatível, a falha é apresentada discretamente e o quiz continua funcionando.

As traduções de árabe e hebraico preservam o suporte a RTL na camada de apresentação do CLI. A camada de domínio não contém I/O de terminal nem lógica específica de direção de texto.

## API principal

| Método | Rota | Autenticação |
| --- | --- | --- |
| POST | `/v1/auth/register` | Pública |
| POST | `/v1/auth/login` | Pública |
| GET | `/v1/me` | JWT |
| GET | `/v1/dashboard` | JWT |
| GET | `/v1/progress` | JWT |
| POST | `/v1/vocabulary/seed` | JWT |
| GET | `/v1/reviews/due` | JWT |
| POST | `/v1/reviews/answer` | JWT |
| GET | `/v1/chapters/{book}/{chapter}` | Pública |
| GET | `/health` | Pública |
| GET | `/health/ready` | Pública |

O endpoint de seed processa o capítulo no servidor e é idempotente. O endpoint de resposta usa uma chave de idempotência por usuário e pergunta, evitando duplicação de XP ou de revisão quando uma requisição é repetida.

## Produção e segurança

A configuração de produção exige `BIBLELINGO_SECRET_KEY` com pelo menos 32 caracteres, CORS explícito sem `*`, expiração de token válida e um caminho persistente para o SQLite. O startup falha rapidamente quando a configuração é insegura; `/health/ready` verifica também a disponibilidade funcional do banco.

O procedimento operacional completo de inicialização, backup online, restauração atômica, permissões e verificações está em [`PRODUCTION_RUNBOOK.md`](PRODUCTION_RUNBOOK.md). Não armazene segredos, tokens ou backups no repositório.

## CI, testes e build

O workflow de CI verifica a compilação Python, os JSONs de conteúdo, a suíte `unittest` e o build do frontend. Para reproduzir localmente:

```bash
python -m compileall app api tests main.py
python -m unittest discover -s tests -v
cd frontend && npm ci && npm run build
```

A cobertura inclui autenticação, isolamento entre usuários, seed idempotente, revisão idempotente, opções de quiz sem placeholders, possessivos ingleses, contexto bíblico estável, dicionários modulares, Salmos 23 e endurecimento de produção.

## Licença e conteúdo

O projeto usa a World English Bible como fonte de conteúdo público. Antes de distribuir novos livros ou capítulos, confirme a licença da fonte e mantenha os arquivos de conteúdo e testes correspondentes versionados no repositório.
