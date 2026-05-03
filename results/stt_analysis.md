# Análise de Erros do STT

## Amostras testadas

| Arquivo | Comando falado | Transcrição gerada | Correto? |
|---|---|---|---|
| 5hz.m4a | "Ajusta a frequência para 5 Hz" | "A justa frequência para 5 Hz" | ❌ |
| confuso.m4a | "Não sei, aumenta a pressão, não, muda frequência, não. Vou querer volume 50 ml" | "Não sei, aumenta a pressão, não, muda frequência, não. Vou querer volume 50 ml." | ✅ |

## Erros mais frequentes observados

### 1. Segmentação incorreta de palavras
**Exemplo:** `"Ajusta"` → `"A justa"`

O Whisper separou uma palavra em duas partes válidas do português.
Esse tipo de erro é silencioso — não aparece como erro ortográfico,
então o normalizer não consegue corrigir.

**Impacto na extração:** Baixo — o LLM foi robusto e extraiu
corretamente mesmo com a transcrição errada.

### 2. Hesitações e mudanças de ideia
**Exemplo:** `"Não sei, aumenta a pressão, não, muda frequência, não. Vou querer volume 50 ml"`

O Whisper transcreveu fielmente todas as hesitações.
O normalizer não removeu os ruídos.

**Impacto na extração:** Nulo — o LLM ignorou as hesitações
e extraiu o comando definitivo corretamente.

## Erros que mais impactam a extração

| Tipo de erro | Impacto | Exemplo |
|---|---|---|
| Segmentação de palavras-chave | Alto | `"ajusta"` → `"a justa"` |
| Número transcrito errado | Alto | `"cinco"` → `"sinto"` |
| Unidade transcrita errada | Médio | `"Hz"` → `"hertz"` (normalizer resolve) |
| Hesitações e ruídos | Baixo | `"ééé"` (LLM ignora) |

## Mitigações recomendadas

### 1. Normalização lexical
Adicionar ao normalizer correções para segmentações comuns:
```python
"a justa": "ajusta",
"fre quência": "frequência",
```

### 2. Reforço de vocabulário técnico
Passar ao Whisper uma lista de palavras do domínio médico
para melhorar a transcrição de termos específicos:
```python
modelo.transcribe(audio, language="pt", initial_prompt="frequência, pressão, volume, Hz, mmHg, ml")
```

### 3. Prompt reforçado no LLM
Instruir o LLM a ignorar hesitações e extrair apenas
o comando definitivo — já implementado no sistema atual.

### 4. Pós-processamento semântico
Validar o valor extraído contra os ranges definidos
no catálogo de comandos antes de retornar status OK.

## Conclusão

O pipeline demonstrou robustez mesmo com transcrições imperfeitas.
O principal risco é a segmentação incorreta de verbos de comando,
que pode ser mitigada com normalização lexical direcionada
ou com o uso do `initial_prompt` do Whisper.