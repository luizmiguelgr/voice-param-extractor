# Voice Param Extractor

Pipeline experimental de voz para extração estruturada de parâmetros em português brasileiro — STT + LLM + schema validation.

## Sobre o projeto

Componente de IA que recebe comandos de voz curtos em português brasileiro, transcreve via STT e extrai parâmetros estruturados no formato JSON, com validação de schema e tratamento de casos ambíguos.

## Pipeline

áudio → STT (Whisper) → Normalização → LLM (Groq) → JSON validado (Pydantic)

## Estrutura

voice-param-extractor/
├── audio_samples/        # áudios de teste
├── data/                 # catálogo de comandos e casos de teste
├── src/
│   ├── stt.py            # transcrição com Whisper
│   ├── normalizer.py     # limpeza e normalização do texto
│   ├── extractor.py      # extração estruturada com LLM
│   └── pipeline.py       # pipeline completo
├── tests/
│   └── test_pipeline.py  # testes automatizados
├── .env.example          # exemplo de configuração
└── requirements.txt

## Instalação

```bash
git clone https://github.com/luizmiguelgr/voice-param-extractor
cd voice-param-extractor
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Instale também o ffmpeg:
```bash
winget install ffmpeg
```

## Configuração

Crie um arquivo `.env` na raiz:

LLM_PROVIDER=groq
GROQ_API_KEY=sua_chave_aqui
OPENAI_API_KEY=

(groq possui chave gratuita)

## Uso

**Pipeline completo com áudio:**
```bash
python -m src.pipeline
```

**Só transcrição:**
```bash
python -m src.stt audio_samples/seu_audio.m4a
```

**Testes automatizados:**
```bash
python -m pytest tests/ -v
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

## Comparação experimental

Testamos dois tipos de áudio para avaliar a robustez do pipeline:

| | Áudio limpo | Áudio confuso |
|---|---|---|
| Transcrição | "Ajusta frequência para 5 Hz" | "Não sei, aumenta pressão, não, muda frequência, não. Vou querer volume 50 ml" |
| Status | OK | OK |
| Extração correta | ✅ | ✅ |

O LLM demonstrou robustez ao ignorar hesitações e mudanças de ideia, extraindo apenas o comando definitivo.

## Decisões técnicas

- **Groq + LLaMA 3.3 70b**: gratuito, rápido e com boa capacidade de extração estruturada
- **Whisper base**: modelo leve que roda localmente sem custo
- **Normalizer minimalista**: só corrige o que o STT estraga e o LLM não consegue deduzir
- **Pydantic**: garante schema enforcement mesmo quando o LLM devolve JSON malformado
- **Pipeline modular**: cada etapa é testável e substituível independentemente

## Tecnologias

- Python 3.11+
- [Whisper](https://github.com/openai/whisper) — STT local
- [Groq](https://console.groq.com) — LLM via API gratuita
- [Pydantic](https://docs.pydantic.dev) — validação de schema
- [pytest](https://pytest.org) — testes automatizados

