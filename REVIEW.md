# Revisão técnica e pedagógica do BibleLingo

**Data da revisão:** 21 de agosto de 2026  
**Escopo:** núcleo terminal em Python, dados de Gênesis 1, vocabulário, quiz, áudio, gamificação e internacionalização.

## Síntese

O BibleLingo já tinha uma boa separação de responsabilidades para um MVP: leitura, parser, vocabulário, quiz, áudio, progresso e idiomas estavam isolados. A principal fragilidade não era a ideia, mas a distância entre algumas promessas da documentação e o comportamento real. A instalação não incluía o áudio anunciado; o idioma inglês não tinha dados no dicionário e caía silenciosamente para português; e o histórico de revisão só avançava quando o usuário acertava.

A entrega atual corrige esses pontos sem transformar o projeto em um clone de aplicativos comerciais. O núcleo agora combina quatro referências de produto de forma compatível com um aplicativo de terminal: **streak e XP** para consistência, **áudio e contexto** para tornar a palavra significativa, **feedback curto após erros** e **revisão espaçada local** para decidir quando a palavra volta.

## Inconsistências encontradas e correções

| Prioridade | Problema verificado | Impacto | Correção aplicada |
| --- | --- | --- | --- |
| Alta | `edge-tts` era importado por `app/audio.py`, mas não aparecia em `requirements.txt`. | A instalação documentada não cobria uma função anunciada e o primeiro uso podia falhar. | `edge-tts` foi incluído; a importação continua opcional e o restante do app funciona sem áudio. |
| Alta | As 49 entradas do dicionário não tinham campo `en`, embora `en` aparecesse como idioma suportado. | `get_translation()` usava português como fallback silencioso para quem escolhesse inglês. | Foram adicionadas definições em inglês e o fallback silencioso foi removido. Dados ausentes agora tornam a pergunta indisponível, com mensagem explícita. |
| Alta | O gerador podia preencher distratores com `???` e aceitar opções repetidas. | O exercício podia ensinar uma alternativa falsa ou perder valor pedagógico. | As opções agora são únicas; uma pergunta sem distratores reais é descartada. |
| Média | `mark_reviewed()` só era chamado em respostas corretas. | Erros não influenciavam a próxima revisão, apesar de serem o sinal mais importante para reforço. | Cada tentativa agora registra acerto ou erro. Acertos avançam por 1, 3, 7, 14 e 30 dias; erros retornam para hoje. |
| Média | O comentário de `xp_for_level()` citava metas que não correspondiam à fórmula implementada. | A documentação interna induzia a uma leitura errada da curva de níveis. | O comentário foi corrigido e o progresso até o próximo nível passou a ser exibido. |
| Média | A palavra era guardada sem o versículo de origem no momento do quiz. | A Bíblia deixava de funcionar como contexto de recuperação da memória. | Cada entrada guarda o texto do versículo e o quiz o mostra antes da pergunta. |

## O que foi implementado

O vocabulário recebeu uma camada de agendamento compatível com o JSON anterior. Campos antigos continuam sendo carregados, enquanto novas informações — contexto, acertos, erros, sequência de acertos e próxima revisão — são preenchidas com valores seguros. A seleção do quiz prioriza palavras vencidas, depois a data de revisão e, por fim, as menos praticadas.

O áudio foi tratado como uma capacidade opcional, não como uma condição para iniciar o app. O cache continua disponível, mas a ausência de `edge-tts` ou de `mpg123`, `ffplay` e `aplay` não impede leitura, vocabulário, quiz ou XP. A documentação de instalação foi alinhada com o arquivo de dependências.

O fluxo principal também ganhou um indicador de progresso para o próximo nível. O XP continua sendo calculado por leitura, palavras novas e acertos, com bônus de streak, mas o usuário passa a enxergar tanto a quantidade total quanto a distância até a próxima meta.

## Benchmark de aplicativos

A comparação foi usada para selecionar padrões transferíveis, não para copiar recursos que exigiriam conta, servidor ou comunidade. O Duolingo documenta XP por lições e práticas, streak diário, score de progresso, desafios e revisão de erros; por isso, o BibleLingo reteve a distinção entre progresso acumulado e hábito diário.[1]

O Memrise destaca palavras e frases relevantes, vídeos de falantes nativos e práticas de pronúncia, construção de frases e compreensão auditiva. No terminal, a adaptação mais importante é apresentar a palavra junto do versículo, permitir áudio sob demanda e revisá-la em mais de uma sessão.[2]

O Busuu recomenda correções curtas, simples, encorajadoras e focadas nos problemas mais importantes, inclusive priorizando inteligibilidade em vez de punir sotaque. Isso orientou o feedback direto do quiz e a decisão de não transformar cada erro em uma penalidade agressiva.[3]

O Anki oferece a referência conceitual para agendamento de estudo e estatísticas de revisão. O BibleLingo adotou apenas uma versão pequena e explicável do princípio, sem introduzir uma dependência de servidor ou uma configuração complexa no MVP.[4]

| Padrão de referência | Adaptação no BibleLingo | Estado |
| --- | --- | --- |
| Hábito diário | Streak, bônus de XP e resumo de sessão. | Implementado |
| Progresso visível | Nível, XP total e percentual até a próxima meta. | Implementado |
| Aprendizagem contextual | Palavra ligada ao texto do versículo. | Implementado |
| Prática auditiva | `edge-tts`, cache e velocidade mais lenta para palavras. | Implementado como opcional |
| Feedback de erro | Resposta correta exibida e tentativa registrada. | Implementado |
| Revisão espaçada | Próxima revisão calculada localmente. | Implementado |
| Comunidade e leaderboard | Não incluídos no terminal. | Próxima fase, se houver backend |

## Validação

A suíte automatizada contém sete testes e terminou com sucesso. Ela cobre a curva progressiva de níveis, carga de progresso inválida, compatibilidade com vocabulário antigo, agendamento de acertos e erros, ausência de fallback de tradução, cobertura de definições em inglês e unicidade das opções do quiz. A compilação de `app`, `main.py` e `tests` também foi concluída sem erros.

Além dos testes unitários, o fluxo completo foi executado em diretórios temporários para `pt`, `es`, `en`, `ar` e `he`. Todas as cinco sessões chegaram ao resumo de progresso sem erro; os dois idiomas RTL passaram pela preparação de exibição prevista pelo projeto.

## Limitações que permanecem

O conteúdo versionado continua limitado a Gênesis 1 e o dicionário ainda é curado manualmente. As definições em inglês são glosses pedagógicas, não um dicionário lexicográfico completo. Ainda não há frases de exemplo independentes, reconhecimento auditivo, avaliação de fala, sincronização, contas, comunidade ou interface web.

A próxima evolução de maior impacto é expandir o conteúdo por capítulo com metadados de dificuldade e exemplos de uso, acrescentar exercícios de reconhecimento auditivo e separar um adaptador de armazenamento do núcleo. Isso permitirá uma futura interface web sem reescrever as regras de progresso, vocabulário e quiz.

## Referências

[1]: <https://blog.duolingo.com/duolingo-101-how-to-learn-a-language-on-duolingo/> "How to Use Duolingo for Language Learning — Duolingo Blog"
[2]: <https://www.memrise.com/> "Memrise — Learn a language"
[3]: <https://www.busuu.com/en/how-to/corrections> "Giving and receiving language corrections — Busuu"
[4]: <https://docs.ankiweb.net/> "Anki Manual"
[5]: <https://github.com/assumcaonerd/biblelingo> "BibleLingo — repositório revisado"
