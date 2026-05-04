# Voice Param Extractor

Pipeline experimental de voz para extração estruturada de parâmetros em português brasileiro — STT + LLM + schema validation.

## Sobre o projeto

Componente de IA que recebe comandos de voz curtos em português brasileiro, transcreve via STT e extrai parâmetros estruturados no formato JSON, com validação de schema e tratamento de casos ambíguos, incompletos e críticos.

## Pipeline

```
áudio → STT (Whisper) → Normalização → LLM (Groq) → Validação (Pydantic) → JSON
```

## Estrutura

```
voice-param-extractor/
├── audio_samples/          # áudios de teste
├── data/
│   ├── commands_catalog.json   # catálogo de parâmetros e ranges
│   └── test_cases.json         # casos de teste documentados
├── src/
│   ├── stt.py              # transcrição com Whisper
│   ├── normalizer.py       # limpeza e normalização do texto
│   ├── extractor.py        # extração estruturada com LLM + validação
│   └── pipeline.py         # pipeline completo
├── tests/
│   └── test_pipeline.py    # testes automatizados
├── results/
│   ├── evaluation.py           # script de métricas automáticas
│   ├── stt_analysis.md         # análise de erros do STT
│   └── experimental_comparison.md  # comparação entre variantes
├── .env.example
└── requirements.txt
```

## Instalação

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
# Pipeline completo com áudio
python -m src.pipeline

# Só transcrição
python -m src.stt audio_samples/seu_audio.m4a

# Testes automatizados
python -m pytest tests/ -v

# Métricas de avaliação
python results/evaluation.py
```

## Exemplo de saída

Entrada: *"Ajusta a frequência para 5 hertz"*

```json
{
  "intent": "ajustar_parametro",
  "parameter": "frequencia",
  "value": 5.0,
  "unit": "Hz",
  "status": "OK",
  "requires_confirmation": false,
  "validation_errors": [],
  "notes": ""
}
```

## Resultados experimentais

Comparamos duas variantes do pipeline — baseline vs reforçada. Resumo:

| Métrica | Variante A — Baseline | Variante B — Reforçada |
|---|---|---|
| Status correto | 6/8 (75%) | 8/8 (100%) |
| Transcrição correta | 4/8 (50%) | 7/8 (87.5%) |
| Falsos negativos críticos | 2 | 0 |

A adição do `initial_prompt` no Whisper e regras semânticas no LLM eliminou todos os falsos negativos críticos.

📄 Análise completa: [results/experimental_comparison.md](results/experimental_comparison.md)

## Decisões técnicas

- **Groq + LLaMA 3.3 70b** — gratuito, rápido e com boa capacidade de extração estruturada
- **Whisper base** — modelo leve que roda localmente sem custo
- **initial_prompt** — vocabulário técnico médico melhora transcrições do domínio
- **Normalizer minimalista** — corrige apenas o que o STT estraga e o LLM não deduz
- **Pydantic** — schema enforcement mesmo quando o LLM devolve JSON malformado
- **Validação de range** — valores fora dos limites do catálogo são rejeitados automaticamente
- **Pipeline modular** — cada etapa é testável e substituível independentemente

## Limitações conhecidas

- Whisper base pode alucinar em silêncio com `initial_prompt` ativo
- Pipeline não suporta múltiplos comandos — retorna `AMBIGUO` e pede repetição
- Números acima de 999 podem ser transcritos com separador de milhar errado
- Áudio fora do domínio pode ser forçado no vocabulário médico pelo `initial_prompt`

## Trabalhos futuros

- VAD para filtrar silêncio antes do STT
- Modelos maiores do Whisper (`small`, `medium`)
- Score de confiança para rejeitar transcrições ruins
- Suporte a múltiplos comandos no mesmo áudio

## Tecnologias

- Python 3.11+
- [Whisper](https://github.com/openai/whisper) — STT local gratuito
- [Groq](https://console.groq.com) — LLM via API gratuita
- [Pydantic](https://docs.pydantic.dev) — validação de schema
- [pytest](https://pytest.org) — testes automatizados
