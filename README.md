# BibleLingo

O BibleLingo é um aplicativo de terminal em Python para estudar inglês por meio da leitura da **World English Bible (WEB)**. A pessoa lê um capítulo, ouve o inglês, salva palavras úteis no vocabulário e pratica com um quiz curto de múltipla escolha.

A proposta combina **conteúdo contextual**, feedback imediato e um hábito diário leve. O projeto continua deliberadamente modular e sem framework web, para que a evolução para Flask, FastAPI ou um frontend possa acontecer sem reescrever o núcleo.

## O que já funciona

| Área | Comportamento atual |
| --- | --- |
| Leitura | Carrega Gênesis 1 a partir do JSON de amostra e formata os versículos para o terminal. |
| Vocabulário | Registra origem, data, revisões, acertos, erros e próxima data de revisão. |
| Revisão | Prioriza palavras vencidas e aplica intervalos locais de 1, 3, 7, 14 e 30 dias. Erros retornam para revisão no mesmo dia. |
| Quiz | Gera opções únicas no idioma escolhido, sem preencher alternativas falsas com `???`. |
| Feedback | Mostra a resposta correta após o erro e registra cada tentativa para o agendamento da palavra. |
| Áudio | Usa `edge-tts` com cache; se a dependência ou um reprodutor do sistema não estiverem disponíveis, o restante do app continua funcionando. |
| Gamificação | Mantém XP, níveis, bônus por streak, recorde de streak e progresso percentual até o próximo nível. |
| Idiomas | Português, espanhol, inglês, árabe e hebraico como idiomas da interface e das traduções. |
| RTL | Usa `arabic-reshaper` e `python-bidi` para exibir árabe e hebraico de forma mais legível no terminal. |

## Instalação e execução

```bash
git clone https://github.com/assumcaonerd/biblelingo.git
cd biblelingo
python -m venv .venv
source .venv/bin/activate       # Linux/macOS
# No Windows: .venv\\Scripts\\activate
python -m pip install -r requirements.txt
python main.py
```

O áudio depende de acesso à rede para gerar a primeira pronúncia e de um reprodutor de áudio instalado no sistema. No Linux, o aplicativo procura `mpg123`, `ffplay` ou `aplay`. O áudio é uma melhoria opcional: sem ele, a leitura, o vocabulário, o quiz e a gamificação continuam disponíveis.

## Testes

A suíte padrão usa apenas a biblioteca do Python e pode ser executada com:

```bash
python -m unittest discover -s tests -v
```

Os testes cobrem a curva de níveis, carga de progresso inválida, compatibilidade com vocabulário antigo, agendamento de revisão, traduções ausentes, unicidade das opções do quiz e os contratos da camada de domínio sem saída no terminal.

## Estrutura

```text
biblelingo/
├── app/
│   ├── domain/           # regras puras, sem terminal, arquivos ou framework
│   │   ├── __init__.py   # contratos públicos compartilhados
│   │   ├── progress.py   # XP, níveis, streak e eventos de progresso
│   │   ├── vocabulary.py # vocabulário e revisão espaçada local
│   │   └── quiz.py       # perguntas tipadas e correção de respostas
│   ├── progress.py       # adaptador CLI e persistência JSON
│   ├── bible_loader.py   # leitura e formatação do JSON WEB
│   ├── parser.py         # tokenização e remoção de stop words
│   ├── vocabulary.py     # adaptador CLI e persistência JSON
│   ├── quiz.py           # adaptador CLI, feedback e áudio
│   ├── audio.py          # edge-tts, cache e reprodução opcional
│   ├── languages.py      # interface multi-idioma
│   └── rtl.py            # preparação de árabe e hebraico
├── data/
│   ├── genesis_sample.json
│   └── dictionary.json
├── tests/
│   └── test_core.py
├── main.py
├── requirements.txt
└── README.md
```

Os arquivos `progress.json`, `vocabulary.json` e `data/audio_cache/` são criados localmente e permanecem fora do controle de versão conforme o `.gitignore`.

## Decisões de produto

O BibleLingo não tenta copiar todo o catálogo dos aplicativos comerciais. Ele incorpora as mecânicas que melhor combinam com a proposta de leitura bíblica: XP e streak para criar constância, exposição auditiva e prática contextual para dar significado às palavras, feedback específico depois do erro e revisão espaçada para evitar que o vocabulário seja apenas uma lista acumulada.

| Referência | Ideia aproveitada no BibleLingo | Adaptação para o terminal |
| --- | --- | --- |
| [Duolingo](https://blog.duolingo.com/duolingo-101-how-to-learn-a-language-on-duolingo/) | XP, streak, prática curta e feedback de progresso. | Sessões breves, streak diário, bônus de XP e percentual até o próximo nível. |
| [Memrise](https://www.memrise.com/) | Palavras relevantes, áudio, exposição a falantes e práticas multimodais. | Palavra extraída de um versículo, pronúncia sob demanda e tradução em contexto. |
| [Busuu](https://www.busuu.com/en/how-to/corrections) | Correções curtas, claras, encorajadoras e focadas nos erros importantes. | O quiz revela a resposta certa e registra a tentativa sem punir o usuário com alternativas inventadas. |
| [Anki](https://docs.ankiweb.net/) | Agendamento de cartões conforme a lembrança do usuário. | Intervalos locais progressivos de 1, 3, 7, 14 e 30 dias, sem servidor ou conta. |

## Limitações atuais

O conteúdo de amostra cobre apenas Gênesis 1. O dicionário é curado manualmente e ainda não é um sistema completo de definições, frases, pronúncia fonética ou níveis de dificuldade. O app também não possui conta, sincronização entre dispositivos, leaderboard, comunidade ou correção de fala; essas funcionalidades exigiriam uma camada de produto além do MVP terminal.

O texto-base da WEB deve continuar sendo obtido de uma fonte autorizada e mantido com sua atribuição apropriada. O projeto usa o sample atualmente versionado para tornar o primeiro uso previsível e não depender de um download silencioso durante a execução.

## Próximos passos recomendados

A próxima evolução de maior impacto é expandir o conteúdo por capítulo com metadados de dificuldade e frases de exemplo, separar claramente “palavra nova” de “palavra para revisão” e adicionar exercícios de reconhecimento auditivo. A Phase 0 da migração web começou com a extração do domínio: `app/domain` agora pode ser importado por uma futura API FastAPI sem depender de `input()`, `print()` ou persistência JSON. Depois disso, vale criar repositórios de armazenamento, schemas Pydantic e uma API de sessão sem alterar as regras de vocabulário, quiz e progresso.

## Licença e conteúdo

Consulte as licenças e atribuições dos dados antes de distribuir novos capítulos ou traduções. O código do app e os arquivos de conteúdo devem ter suas licenças explicitadas em uma próxima versão pública do repositório.
