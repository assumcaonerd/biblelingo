# BibleLingo

App estilo Duolingo para aprender inglês lendo e praticando com a Bíblia (World English Bible).

Gamificação + leitura + vocabulário + quiz + áudio + múltiplos idiomas + **RTL**.

## Objetivo

Aprender inglês através da leitura da Escritura. Texto da **World English Bible (WEB)** (domínio público).

## Idiomas nativos suportados

| Código | Idioma       | Direção |
|--------|--------------|---------|
| `pt`   | Português 🇧🇷  | LTR     |
| `es`   | Español 🇪🇸    | LTR     |
| `en`   | English 🇺🇸    | LTR     |
| `ar`   | العربية 🇸🇦     | **RTL** |
| `he`   | עברית 🇮🇱      | **RTL** |

## Suporte RTL

Para árabe e hebraico o app usa:
- **arabic-reshaper** → conecta as letras árabes corretamente
- **python-bidi** → aplica o algoritmo bidirecional do Unicode

Assim o texto aparece legível no terminal.

```bash
pip install arabic-reshaper python-bidi
```

## Como rodar

```bash
git clone https://github.com/assumcaonerd/biblelingo.git
cd biblelingo
pip install -r requirements.txt
python main.py
```

## O que já funciona

- XP e níveis
- Streak
- Gênesis 1
- Vocabulário
- Quiz interativo
- Áudio (edge-tts + cache)
- Português, espanhol, inglês, **árabe** e **hebraico**
- Exibição correta de textos RTL

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
│   ├── languages.py
│   └── rtl.py              ← suporte RTL
├── data/
│   ├── genesis_sample.json
│   ├── dictionary.json
│   └── audio_cache/
├── main.py
└── requirements.txt
```
