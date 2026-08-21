# Auditoria e estabilização — BibleLingo

## Estado verificado

A branch `main` contém a implementação auditada no [repositório BibleLingo][1]. O código inclui autenticação JWT, `GET /v1/reviews/due`, seed contextual de Gênesis 1, integração React/Vite na tela **Praticar** e `POST /v1/reviews/answer` idempotente.

## Validações executadas

| Verificação | Resultado |
| --- | --- |
| Suíte Python original | Falhou inicialmente em 6 testes de autenticação por incompatibilidade de `bcrypt` 5.x com `passlib` 1.7.4. |
| Suíte Python após correções locais | **20 testes passaram**. |
| Compilação Python | **Passou** em `app`, `api` e `tests`. |
| Build frontend | **Passou** com TypeScript e Vite. |
| JWT sem token | Retornou `401` em `/v1/reviews/due`. |
| Seed inicial | Retornou perguntas válidas, opções contendo a resposta correta, contexto bíblico e origem `Genesis 1:n`. |
| Resposta e retry | A primeira resposta concedeu 10 XP; a repetição com a mesma chave retornou `already_processed=true` sem duplicar XP. |
| API direta | `GET /health` respondeu `200`. |
| Proxy Vite | `GET /api/health` respondeu `200` através do frontend. |

## Correções publicadas

A instalação limpa revelou que `bcrypt>=4.0.1` permitia instalar bcrypt 5.x, combinação que fazia o registro de usuários falhar com a mensagem de limite de senha mesmo para `secret123`. A dependência foi fixada em `bcrypt==4.0.1`, versão que passou os testes sem esse erro funcional.

O seed foi enriquecido com origem e contexto real de Gênesis 1. O endpoint também passou a rejeitar explicitamente `native_lang` fora de `pt`, `es`, `en`, `ar` e `he`, em vez de produzir uma sessão vazia. O cadastro foi alinhado aos mesmos códigos suportados.

No frontend, a chave de idempotência agora é estável por pergunta durante a sessão, de modo que uma nova tentativa após falha de rede reutilize a mesma chave e não possa conceder XP duplicado. O texto do botão na leitura foi ajustado de “palavras deste capítulo” para “palavras pendentes”, pois a fila atual é baseada na revisão do usuário, não em um capítulo específico.

Os testes foram fortalecidos para verificar contexto/origem no seed, idioma inválido e inicialização explícita do schema SQLite nos testes com `TestClient`.

## Serviços

Não havia API ou frontend ativos no início da auditoria. Após a validação, ambos foram iniciados e posteriormente reiniciados com sucesso:

- API: `http://127.0.0.1:8000`, com banco temporário `/tmp/biblelingo-e2e.db`.
- Frontend: `http://127.0.0.1:5173`.
- Proxy verificado: `http://127.0.0.1:5173/api/health`.

Os serviços permanecem ativos nesta sessão. O segredo usado foi temporário e exclusivo do teste ponta a ponta; nenhum segredo de produção foi criado ou publicado.

## Publicação e pendências

As correções foram publicadas diretamente na branch `main` em sete commits sucessivos: `ec6784c`, `3714287`, `ea9e03e`, `abe388e`, `412eb62`, `f507009` e `7dfaec0`. O relatório foi inicialmente incluído no primeiro desses commits e finalizado no commit adicional `81e5e70`. A comparação byte a byte confirmou que os nove arquivos críticos publicados correspondem às versões testadas localmente. Um clone limpo do HEAD remoto também passou pelos 20 testes, pela compilação Python e pelo build Vite com `npm ci`.

O único aviso não bloqueante restante é a depreciação do uso de `httpx` com `starlette.testclient`, emitida pela versão atual do Starlette. Ela não causou falha nos 20 testes; pode ser tratada posteriormente ao atualizar o contrato de testes para a recomendação da stack.

## Próximas prioridades

A prioridade imediata é configurar CI sobre uma instalação limpa e, em seguida, adicionar refresh/revalidação do JWT no frontend, carregar o perfil via `/v1/me` após reload, registrar métricas de retenção e acerto por palavra e evoluir a prática por capítulo sem perder a fila de revisões vencidas.

[1]: https://github.com/assumcaonerd/biblelingo "Repositório BibleLingo no GitHub"
