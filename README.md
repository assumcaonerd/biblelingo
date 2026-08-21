# BibleLingo

App estilo Duolingo para aprender inglês lendo e praticando com a Bíblia (World English Bible).

Gamificação simples + leitura interativa + vocabulário + quizzes.

## Objetivo do projeto

Aprender inglês de forma natural através da leitura da Escritura. O texto usado é a **World English Bible (WEB)**, que está em domínio público.

## Status atual

### Já implementado
- Sistema de **XP** e **níveis**
- Sistema de **Streak** (dias consecutivos)
- Bônus de XP baseado no streak
- Carregador da Bíblia WEB (Gênesis sample)
- Parser de palavras (com stop words)
- Vocabulário do usuário
- **Quiz interativo** (múltipla escolha)
- Dicionário inicial inglês → português
- Persistência em JSON

### Próximos passos
- Mais capítulos e livros
- Interface web
- Mais tipos de pergunta no quiz
- Sistema de vidas / hearts

## Como rodar

```bash
git clone https://github.com/assumcaonerd/biblelingo.git
cd biblelingo
python main.py
```

O fluxo completo agora é:
1. Mostra Gênesis 1
2. Extrai e salva palavras novas
3. Roda um quiz com 5 perguntas
4. Dá XP (leitura + palavras + acertos)
5. Atualiza o streak

## Estrutura

```
biblelingo/
├── app/
│   ├── progress.py
│   ├── bible_loader.py
│   ├── parser.py
│   ├── vocabulary.py
│   └── quiz.py
├── data/
│   ├── genesis_sample.json
│   └── dictionary.json
├── main.py
└── requirements.txt
```
