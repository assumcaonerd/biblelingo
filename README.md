# BibleLingo

App estilo Duolingo para aprender inglês lendo e praticando com a Bíblia (World English Bible).

Gamificação simples + leitura interativa + vocabulário + quizzes.

## Objetivo do projeto

Aprender inglês de forma natural através da leitura da Escritura. O texto usado é a **World English Bible (WEB)**, que está em domínio público.

## Status atual

Estamos construindo do zero, seguindo a filosofia *build-your-own*.

### Já implementado
- Sistema de **XP** e **níveis**
- Sistema de **Streak** (dias consecutivos)
- Bônus de XP baseado no streak
- Carregador da Bíblia WEB (Gênesis sample)
- Parser de palavras (com stop words)
- **Vocabulário do usuário** (adicionar palavras a partir dos versículos)
- Persistência em JSON (progresso + vocabulário)

### Próximos passos
- Quiz engine
- Interface mais interativa no terminal
- Mais capítulos / livros
- Web interface (Flask ou similar)

## Como rodar

```bash
git clone https://github.com/assumcaonerd/biblelingo.git
cd biblelingo
python main.py
```

Na primeira execução ele:
1. Mostra Gênesis 1
2. Extrai palavras novas
3. Adiciona ao vocabulário
4. Dá XP e atualiza o streak

## Estrutura

```
biblelingo/
├── app/
│   ├── progress.py       # XP + Streak
│   ├── bible_loader.py   # Carrega WEB
│   ├── parser.py         # Extrai palavras
│   ├── vocabulary.py     # Vocabulário do usuário
│   └── quiz.py           # (próximo)
├── data/
│   └── genesis_sample.json
├── main.py
└── requirements.txt
```

## Filosofia

Código escrito de forma progressiva. Cada módulo pode ser estudado e estendido isoladamente.
