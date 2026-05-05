# Voice Param Extractor

Pipeline experimental de voz para extração estruturada de parâmetros em português brasileiro — STT + LLM + schema validation.

## Sobre o projeto

Componente de IA que recebe comandos de voz curtos em português brasileiro, transcreve via STT e extrai parâmetros estruturados no formato JSON, com validação de schema e tratamento de casos ambíguos, incompletos e críticos.

O pipeline processa automaticamente todos os arquivos de áudio da pasta `audio_samples/` — sem necessidade de digitar nomes de arquivos ou comandos de texto.

## Pipeline

```
audio_samples/ → STT (Whisper) → Normalização → LLM (Groq) → Validação (Pydantic) → JSON
```

## Estrutura

```
voice-param-extractor/
├── audio_samples/              # áudios de teste (.wav, .mp3, .m4a, .ogg, .flac)
├── data/
│   ├── commands_catalog.json   # catálogo de parâmetros, ranges e unidades
│   └── test_cases.json         # casos de teste documentados
├── src/
│   ├── stt.py                  # transcrição com Whisper
│   ├── normalizer.py           # limpeza e normalização do texto
│   ├── extractor.py            # extração estruturada com LLM + validação de range
│   └── pipeline.py             # pipeline completo — lê audios da pasta automaticamente
├── tests/
│   └── test_pipeline.py        # testes automatizados
├── results/
│   ├── evaluation.py               # script de métricas automáticas
│   ├── wer_evaluation.py           # cálculo de WER por variante
│   ├── stt_analysis.md             # análise de erros do STT
│   ├── experimental_comparison.md  # comparação entre variantes
│   └── problem_analysis.md         # análise inicial do problema
├── Dockerfile                  # imagem Docker do projeto
├── docker-compose.yml          # orquestração do container
├── requirements.docker.txt     # dependências para Docker/Linux
├── requirements.txt            # dependências para Windows
├── .env.example                # exemplo de configuração
└── LINKS.md                    # documento central de avaliação
```

## Instalação e execução

### Opção 1 — Docker (recomendado para qualquer sistema operacional)

O Docker garante ambiente idêntico em qualquer máquina, independente do sistema operacional.

```bash
git clone https://github.com/luizmiguelgr/voice-param-extractor
cd voice-param-extractor
cp .env.example .env
# Edite o .env e adicione sua GROQ_API_KEY
docker compose run pipeline python -m src.pipeline
```

Para rodar os testes:
```bash
docker compose run pipeline python -m pytest tests/ -v
```

### Opção 2 — Ambiente local (Windows)

```bash
git clone https://github.com/luizmiguelgr/voice-param-extractor
cd voice-param-extractor
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
winget install ffmpeg
```

## Configuração

Crie um arquivo `.env` na raiz baseado no `.env.example`:

```
LLM_PROVIDER=groq
GROQ_API_KEY=sua_chave_aqui
OPENAI_API_KEY=
```

Obtenha sua chave gratuita em: https://console.groq.com

## Uso

```bash
# Pipeline completo — processa todos os áudios da pasta audio_samples/
python -m src.pipeline

# Testes automatizados
python -m pytest tests/ -v

# Métricas de avaliação
python results/evaluation.py

# WER por variante
python results/wer_evaluation.py
```

## Exemplo de saída

Entrada: arquivo `audio_samples/5hz.m4a` — *"Ajusta a frequência para 5 hertz"*

```json
{
  "intent": "ajustar_parametro",
  "parameter": "frequencia",
  "value": 5.0,
  "unit": "Hz",
  "status": "OK",
  "requires_confirmation": true,
  "validation_errors": [],
  "notes": ""
}
```

## Resultados experimentais

Comparamos duas variantes do pipeline — baseline vs reforçada:

| Métrica | Variante A — Baseline | Variante B — Reforçada |
|---|---|---|
| Status correto | 6/8 (75%) | 8/8 (100%) |
| Transcrição correta | 4/8 (50%) | 7/8 (87.5%) |
| Falsos negativos críticos | 2 | 0 |
| WER médio | 20.6% | 6.7% |

A adição do `initial_prompt` no Whisper e regras semânticas no LLM eliminou todos os falsos negativos críticos.

Análise completa: [results/experimental_comparison.md](results/experimental_comparison.md)

## Decisões técnicas

- **Groq + LLaMA 3.3 70b** — gratuito, rápido e com boa capacidade de extração estruturada
- **Whisper base** — modelo leve que roda localmente sem custo
- **initial_prompt** — vocabulário técnico médico melhora transcrições do domínio
- **Normalizer minimalista** — corrige apenas o que o STT estraga e o LLM não deduz
- **Pydantic** — schema enforcement mesmo quando o LLM devolve JSON malformado
- **Validação de range** — valores fora dos limites do catálogo são rejeitados automaticamente
- **Pipeline modular** — cada etapa é testável e substituível independentemente
- **Leitura automática da pasta** — o pipeline detecta e processa todos os áudios sem intervenção manual
- **Docker** — ambiente reprodutível em qualquer sistema operacional

## Limitações conhecidas

- Whisper base é não-determinístico em áudios ambíguos — a mesma gravação pode gerar transcrições diferentes a cada execução
- Whisper pode alucinar em silêncio ou ruído de fundo com `initial_prompt` ativo
- Pipeline não suporta múltiplos comandos no mesmo áudio — retorna AMBIGUO e solicita repetição
- Números acima de 999 podem ser transcritos com separador de milhar europeu

## Tecnologias

- Python 3.11+
- [Whisper](https://github.com/openai/whisper) — STT local gratuito
- [Groq](https://console.groq.com) — LLM via API gratuita
- [Pydantic](https://docs.pydantic.dev) — validação de schema
- [pytest](https://pytest.org) — testes automatizados
- [Docker](https://www.docker.com) — ambiente reprodutível
