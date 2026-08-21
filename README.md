# BibleLingo

App estilo Duolingo para aprender inglês lendo e praticando com a Bíblia (World English Bible).

Gamificação + leitura interativa + vocabulário + quiz + áudio + **múltiplos idiomas**.

## Objetivo

Aprender inglês de forma natural através da leitura da Escritura. Texto da **World English Bible (WEB)** (domínio público).

## Idiomas suportados

O app ensina **inglês**. O usuário pode escolher seu idioma nativo:

| Código | Idioma     |
|--------|------------|
| `pt`   | Português  |
| `es`   | Español    |
| `en`   | English    |

A interface e as traduções do quiz mudam conforme o idioma escolhido.

## O que já funciona

- XP e níveis
- Streak (dias consecutivos)
- Carregamento de Gênesis
- Extração de palavras
- Vocabulário do usuário
- Quiz interativo (múltipla escolha)
- Áudio com edge-tts + cache
- **Suporte a múltiplos idiomas nativos**
- Persistência em JSON

## Como rodar

```bash
git clone https://github.com/assumcaonerd/biblelingo.git
cd biblelingo
pip install -r requirements.txt
python main.py
```

Na primeira tela você escolhe o idioma nativo. Depois o fluxo segue normalmente.

## Estrutura

```
biblelingo/
├── app/
│   ├── progress.py
│   ├── bible_loader.py
│   ├── parser.py
│   ├── vocabulary.py
│   ├── quiz.py
│   ├── audio.py
│   └── languages.py      ← config de idiomas + textos da UI
├── data/
│   ├── genesis_sample.json
│   ├── dictionary.json   ← traduções pt + es
│   └── audio_cache/
├── main.py
└── requirements.txt
```
