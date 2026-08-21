# Roteiro de migração do BibleLingo para FastAPI e frontend web

## Recomendação central

A migração não deve começar transformando o `main.py` em endpoints. O caminho mais seguro é separar primeiro as regras de negócio do terminal e, depois, expô-las por uma API. O terminal continuará funcionando como um cliente da mesma camada de domínio durante a transição; o frontend web será apenas outro cliente.

> O objetivo é manter uma única fonte de verdade para XP, streak, vocabulário, revisão espaçada, quiz e regras de conteúdo.

A arquitetura recomendada é um monorepo com três camadas: um backend FastAPI, um frontend React com TypeScript e um núcleo de domínio compartilhado conceitualmente pelo CLI e pela API. O backend deve ser responsável por autenticação, persistência, regras de sessão e integração com áudio; o frontend deve cuidar da experiência de leitura, revisão e visualização do progresso.

## 1. Refatorar o núcleo antes da web

O código atual já possui bons módulos, mas alguns deles ainda misturam regra de negócio, persistência JSON e saída no terminal. O primeiro passo é retirar `print()`, `input()` e caminhos fixos dos módulos de domínio.

| Situação atual | Destino recomendado |
| --- | --- |
| `app/progress.py` calcula XP e streak e também imprime mensagens | `domain/progress.py` retorna estados e eventos; a interface decide como exibir |
| `app/vocabulary.py` persiste diretamente em JSON | `domain/vocabulary.py` contém regras; um repositório separado salva em banco |
| `app/quiz.py` gera perguntas e lê respostas do terminal | `services/quiz_service.py` gera perguntas e recebe respostas por parâmetros |
| `app/audio.py` chama TTS e reprodutor local | `services/audio_service.py` gera ou recupera um artefato de áudio |
| `main.py` orquestra tudo com entrada interativa | `cli/main.py` vira um cliente do núcleo; `api/routes/*` vira outro cliente |

A API não deve importar funções que imprimem diretamente no terminal. Funções como `add_xp()` e `record_review()` devem retornar estruturas claras, por exemplo um evento de XP, a nova pontuação, o nível e o estado do streak. Isso facilita testes, serialização JSON e a criação de uma interface web consistente.

Uma estrutura inicial poderia ser:

```text
biblelingo/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/routes/
│   │   ├── core/                 # configuração, segurança e dependências
│   │   ├── domain/               # XP, streak, vocabulário e revisão
│   │   ├── models/               # modelos ORM
│   │   ├── schemas/              # contratos Pydantic
│   │   ├── repositories/         # acesso a dados
│   │   └── services/             # quiz, sessão, áudio e conteúdo
│   └── tests/
├── frontend/
│   └── src/
│       ├── api/
│       ├── components/
│       ├── pages/
│       ├── hooks/
│       └── i18n/
├── cli/
├── data/
└── docker-compose.yml
```

## 2. Migrar de JSON local para persistência por usuário

O JSON funciona bem no terminal individual, mas não é adequado para vários usuários, concorrência, histórico e recuperação de dados. Para desenvolvimento, SQLite é suficiente; para produção, PostgreSQL é a escolha mais segura. A troca deve ser feita por meio de repositórios, sem espalhar SQL pelo domínio.

O conteúdo bíblico e o dicionário devem ser tratados como dados de conteúdo, enquanto progresso e vocabulário devem ser dados do usuário. O importador deve ser idempotente: executar a carga de Gênesis 1 duas vezes não pode duplicar capítulos, versículos ou definições.

| Entidade | Campos essenciais | Observação |
| --- | --- | --- |
| `users` | `id`, `email`, `password_hash`, `native_language`, `created_at` | Nunca armazenar senha em texto puro |
| `chapters` | `id`, `book`, `chapter_number`, `translation` | Conteúdo versionado e identificável |
| `verses` | `id`, `chapter_id`, `verse_number`, `text` | Índice único por capítulo e número |
| `dictionary_entries` | `word`, `language`, `meaning`, `part_of_speech` | Permite traduções e glosses por idioma |
| `vocabulary_items` | `user_id`, `word`, `origin_verse_id`, `context`, `status` | Índice único por usuário e palavra |
| `review_states` | `vocabulary_item_id`, `streak`, `next_review_at`, `last_reviewed_at` | Estado atual do agendamento |
| `review_events` | `item_id`, `user_id`, `correct`, `answered_at` | Histórico para métricas e futuras melhorias |
| `progress` | `user_id`, `xp`, `level`, `current_streak`, `longest_streak`, `last_activity_date` | Uma linha por usuário |
| `study_sessions` | `user_id`, `started_at`, `finished_at`, `correct_count`, `new_words` | Resumo de cada sessão |

Use migrações versionadas desde o primeiro esquema. O banco de produção nunca deve depender de `create_all()` executado silenciosamente na inicialização; cada mudança de estrutura deve ser uma migração revisável.

## 3. Definir o contrato da API

Comece com uma API pequena e orientada às ações reais do produto. O frontend não deve montar regras de XP, escolher distratores nem calcular a próxima revisão; ele deve enviar intenções e exibir o estado devolvido pelo servidor.

| Método | Rota | Responsabilidade |
| --- | --- | --- |
| `GET` | `/health` | Verificar disponibilidade da aplicação |
| `POST` | `/v1/auth/register` | Criar conta e preferências iniciais |
| `POST` | `/v1/auth/login` | Obter sessão ou tokens |
| `GET` | `/v1/me` | Retornar perfil e idioma nativo |
| `GET` | `/v1/chapters` | Listar conteúdo disponível |
| `GET` | `/v1/chapters/{chapter_id}` | Retornar versículos e metadados |
| `POST` | `/v1/sessions` | Iniciar uma sessão de estudo |
| `GET` | `/v1/reviews/due` | Obter palavras vencidas para revisão |
| `POST` | `/v1/reviews/answer` | Registrar resposta e devolver feedback, XP e próxima revisão |
| `GET` | `/v1/vocabulary` | Listar vocabulário do usuário com filtros |
| `POST` | `/v1/vocabulary` | Salvar uma palavra a partir de um versículo |
| `GET` | `/v1/progress` | Retornar XP, nível, streak e progresso até a próxima meta |
| `GET` | `/v1/audio/{asset_id}` | Entregar áudio já armazenado ou iniciar geração controlada |

A resposta de `POST /v1/reviews/answer` deve ser atômica. Ela precisa validar se a pergunta pertence à sessão, registrar a tentativa, atualizar o estado de revisão, atualizar XP e streak quando aplicável e retornar o resultado final. Se o cliente repetir a mesma requisição por causa de uma falha de rede, uma chave de idempotência deve impedir que a mesma resposta conceda XP duas vezes.

Um retorno possível seria:

```json
{
  "correct": true,
  "correct_answer": "brightness that lets us see",
  "xp_awarded": 12,
  "level": 3,
  "progress_percent": 41,
  "streak": 4,
  "next_review_at": "2026-08-22",
  "feedback": "Good work. Review this word tomorrow."
}
```

O FastAPI deve expor contratos Pydantic de entrada e saída, versionar as rotas desde o começo e manter erros em um formato previsível. A documentação OpenAPI gerada automaticamente pode servir como contrato inicial entre backend e frontend.[1] [2]

## 4. Autenticação, segurança e privacidade

Para um MVP, implemente cadastro, login, logout, recuperação de senha e alteração do idioma nativo. O token ou sessão deve identificar o usuário em todas as operações de vocabulário, revisão e progresso; nunca aceite `user_id` enviado livremente pelo frontend.

A senha deve ser armazenada apenas como hash forte. Tokens devem ter expiração, rotação ou revogação adequada, e os segredos devem vir de variáveis de ambiente. Configure CORS apenas para os domínios do frontend, limite tentativas de login, valide o tamanho dos textos recebidos e não registre tokens ou dados sensíveis nos logs.

Também é necessário decidir uma política para o conteúdo bíblico e para o áudio. O texto, as traduções e os arquivos de áudio devem manter atribuição e licença claras. A importação de capítulos deve ser feita por um comando administrativo ou pipeline controlado, não por download silencioso durante uma requisição de usuário.

## 5. Transformar o quiz em uma experiência web

A primeira tela útil deve ser um painel simples com o streak atual, XP, nível, palavras vencidas e um botão de continuar estudando. A segunda deve ser o leitor: versículos visíveis, palavra selecionável, significado, pronúncia e ação para salvar no vocabulário. A terceira deve ser a sessão de revisão, com uma pergunta por vez, feedback imediato e progresso da sessão.

| Tela | Comportamento mínimo |
| --- | --- |
| Dashboard | Mostra streak, XP, nível, palavras vencidas e última sessão |
| Reader | Exibe capítulo, permite selecionar palavra e ouvir pronúncia |
| Word detail | Mostra significado, versículo de origem, histórico e próxima revisão |
| Review session | Apresenta pergunta, opções, feedback e avanço para a próxima |
| Progress | Exibe palavras aprendidas, acertos, erros e evolução do streak |
| Settings | Permite idioma nativo, áudio, velocidade e preferências de acessibilidade |

O frontend deve manter o estado de sessão no servidor. Pode usar cache local apenas para melhorar a experiência, nunca para decidir XP ou revisão. Todos os estados de carregamento, erro, ausência de palavras vencidas, expiração de sessão e indisponibilidade de áudio precisam ter uma resposta visual clara.

Árabe e hebraico devem ser tratados no nível da interface, com `dir="rtl"` por tela ou componente quando necessário, e não apenas com manipulação manual de strings. Os controles precisam continuar utilizáveis por teclado e leitores de tela.

## 6. Áudio sem bloquear a API

A geração de áudio é uma integração externa e não deve tornar a resposta do quiz lenta ou frágil. Para a primeira versão web, a opção mais simples é gerar o áudio sob demanda, calcular uma chave determinística baseada em texto, voz e velocidade, salvar o resultado em cache e devolver a URL do arquivo.

Quando o volume crescer, mova a geração para uma fila ou worker. O endpoint pode devolver `pending`, `ready` ou `unavailable`, e o frontend pode tentar novamente sem bloquear a sessão de estudo. Em produção, armazene os arquivos em storage compatível com S3 ou outro serviço persistente; o diretório local deve ser reservado ao desenvolvimento.

## 7. Plano incremental de implementação

A ordem abaixo reduz risco porque entrega valor em cada etapa e mantém o terminal funcionando durante a migração.

| Fase | Entrega | Critério de conclusão |
| --- | --- | --- |
| 0. Contrato | Refatorar domínio sem `input()`/`print()` e manter testes atuais | CLI continua funcionando e regras têm testes puros |
| 1. Backend local | FastAPI, schemas, rotas de conteúdo e banco SQLite | Swagger permite ler capítulo e dicionário |
| 2. Persistência | Modelos, repositórios e migrações | Usuário, progresso e vocabulário sobrevivem a reinicializações |
| 3. Revisão | Sessões, perguntas, respostas idempotentes e XP transacional | Uma resposta não pode duplicar XP nem revisão |
| 4. Autenticação | Cadastro, login, proteção de rotas e preferências | Dados de um usuário não aparecem para outro |
| 5. Frontend vertical slice | Login, dashboard, reader e uma sessão de quiz | Um usuário consegue completar uma sessão do início ao fim |
| 6. Áudio e RTL | Cache, player, loading/error states e telas RTL | Áudio indisponível não quebra a sessão; árabe/hebraico permanecem legíveis |
| 7. Qualidade | Testes de API, testes de frontend, lint, CI e migrações | Pull request executa verificações automaticamente |
| 8. Produção | Docker, PostgreSQL, storage, observabilidade e backups | Deploy reproduzível com segredos fora do código |

O primeiro vertical slice não deve tentar incluir todos os capítulos, leaderboard, amigos, notificações ou ranking. Ele deve provar apenas o ciclo essencial: entrar, ler um versículo, salvar uma palavra, responder uma questão, receber feedback e ver o progresso atualizado.

## 8. Testes e observabilidade

Mantenha os testes puros do domínio e acrescente testes de integração para as rotas. O backend deve testar autenticação, isolamento entre usuários, transação de resposta, idempotência, dados ausentes e datas de revisão. O frontend deve testar a sessão feliz e estados de erro; depois, um teste de navegador deve completar o fluxo principal.

Registre métricas sem expor conteúdo sensível: duração de sessão, taxa de conclusão, respostas corretas, palavras vencidas e falhas de áudio. Evite medir apenas logins e cliques; o indicador de sucesso é a pessoa completar sessões e retornar para revisar palavras difíceis.

## 9. O que não fazer agora

Não recomendo iniciar com microserviços, GraphQL, leaderboard, pagamentos, reconhecimento de fala ou uma reescrita completa do frontend. Essas decisões aumentariam a superfície operacional antes de provar que o ciclo de aprendizagem funciona para múltiplos usuários.

Também não recomendo manter `progress.json` e `vocabulary.json` como fonte de verdade depois que a autenticação for introduzida. Eles podem continuar como formato de importação/exportação pessoal, mas o servidor precisa operar sobre registros associados a um usuário e protegidos por transações.

## Prioridade imediata

Os próximos três commits mais valiosos seriam: primeiro, extrair as regras de domínio para funções que não dependam do terminal; segundo, criar uma API local com `GET /health`, leitura de capítulo, vocabulário e progresso usando SQLite; terceiro, implementar uma sessão de revisão completa com `POST /reviews/answer` atômico e idempotente.

Depois desses três passos, o frontend poderá ser desenvolvido contra contratos reais, e não contra mocks que escondem problemas de autenticação, persistência e consistência de XP.

## Referências

[1]: <https://fastapi.tiangolo.com/> "FastAPI official documentation"
[2]: <https://fastapi.tiangolo.com/tutorial/body/> "FastAPI request body and validation"
[3]: <https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/> "FastAPI OAuth2 with Password and JWT tokens"
[4]: <https://docs.pydantic.dev/latest/> "Pydantic documentation"
[5]: <https://alembic.sqlalchemy.org/en/latest/> "Alembic documentation"
