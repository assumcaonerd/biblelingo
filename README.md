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
- Persistência em JSON

### Em construção
- Carregamento dos livros da WEB
- Parser de palavras
- Vocabulário do usuário
- Quiz engine
- Interface (terminal primeiro, depois web)

## Como rodar

```bash
pip install -r requirements.txt
python main.py
```

## Estrutura

```
biblelingo/
├── app/
│   ├── progress.py      # XP + Streak (pronto)
│   ├── bible_loader.py
│   ├── parser.py
│   ├── vocabulary.py
│   └── quiz.py
├── data/                # JSONs da WEB e dicionário
├── main.py
└── requirements.txt
```

## Filosofia

O código está sendo escrito de forma progressiva e educativa. Cada módulo tem TODOs claros para quem quiser contribuir ou aprender mexendo.
