# BibleLingo

App estilo Duolingo para aprender inglês lendo e praticando com a Bíblia (World English Bible).

Gamificação + leitura interativa + vocabulário + quiz + áudio.

## Objetivo

Aprender inglês de forma natural através da leitura da Escritura. Texto da **World English Bible (WEB)** (domínio público).

## O que já funciona

- XP e níveis
- Streak (dias consecutivos)
- Carregamento de Gênesis
- Extração de palavras
- Vocabulário do usuário
- Quiz interativo (múltipla escolha)
- Áudio com **edge-tts** + **cache automático**
- Controle de velocidade da fala
- Persistência em JSON

## Como rodar

```bash
git clone https://github.com/assumcaonerd/biblelingo.git
cd biblelingo
pip install -r requirements.txt
python main.py
```

Fluxo atual:
1. Mostra Gênesis 1
2. Oferece ouvir o texto em inglês
3. Extrai e salva palavras novas
4. Roda quiz (com opção de ouvir a pronúncia)
5. Dá XP e atualiza o streak

## Áudio

Usamos **edge-tts** (Microsoft Edge TTS):
- Gratuito e sem API key
- Cache automático em `data/audio_cache/`
- Velocidade mais lenta por padrão (melhor para aprender)

```bash
pip install edge-tts
```

## Estrutura

```
biblelingo/
├── app/
│   ├── progress.py
│   ├── bible_loader.py
│   ├── parser.py
│   ├── vocabulary.py
│   ├── quiz.py
│   └── audio.py
├── data/
│   ├── genesis_sample.json
│   ├── dictionary.json
│   └── audio_cache/      (gerado automaticamente)
├── main.py
└── requirements.txt
```
