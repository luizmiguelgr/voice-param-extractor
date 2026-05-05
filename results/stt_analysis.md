# Análise de Erros do STT

## Conjunto de amostras testadas

| Arquivo | Comando falado | Sem initial_prompt | Com initial_prompt |
|---|---|---|---|
| 5hz.m4a | "Ajusta a frequência para 5 Hz" | "A justa frequência para 5 Hz" | "ajusta a frequência para 5 Hz" |
| confuso.m4a | "Não sei... vou querer volume 50 ml" | Transcrição fiel | Transcrição fiel |
| audiovazio.m4a | silêncio/ruído | string vazia | Não-determinístico — ver stt_analysis.md |
| freq9999hz.m4a | "Ajusta frequência para 9999 Hz" | "9.999 Hz" | "9.999 Hz" |
| doiscomandos.m4a | "Ajusta frequência 5 e pressão 120" | "A justa frequência para 5 e para 120" | "ajusta frequência para 5 e pressão para 120" |
| inglesportugues.m4a | mistura inglês/português | "Setra-guencha 4, 5 heredas" | "Sete frequência 405 Hz, 5 Hz" |
| negativo.m4a | "Ajusta temperatura para menos 5 graus" | Transcrição fiel | Transcrição fiel |
| unidadeerrada.m4a | "Ajusta frequência para 120 mmHg" | "A justa frequência para 120 mmHG" | "ajusta frequência para 120 mmHg" |

---

## a. Tipos de erro mais frequentes

### 1. Segmentação incorreta de palavras

| Ocorrência | Sem prompt | Com prompt |
|---|---|---|
| 5hz.m4a | "A justa" | "ajusta" |
| doiscomandos.m4a | "A justa" | "ajusta" |
| unidadeerrada.m4a | "A justa" | "ajusta" |

Alta frequência — 4 dos 8 áudios sem initial_prompt. Resolvido completamente com initial_prompt.

### 2. Separador de milhar europeu

| Ocorrência | Transcrito | Esperado |
|---|---|---|
| freq9999hz.m4a | "9.999 Hz" | "9999 Hz" |

Média frequência — números acima de 999. Resolvido pelo normalizer com regex.

### 3. Não-determinismo em áudio ambíguo

O audiovazio.m4a gerou transcrições diferentes a cada execução com initial_prompt ativo. O status final permaneceu INVALIDO em todos os casos. Documentado em detalhes no `experimental_comparison.md`.

### 4. Forçar vocabulário em áudio fora do domínio

| Situação | Sem prompt | Com prompt |
|---|---|---|
| inglesportugues.m4a | "Setra-guencha 4, 5 heredas" | "Sete frequência 405 Hz, 5 Hz" |

Baixa frequência. Ambos os casos foram corretamente rejeitados pelo sistema.

---

## b. Erros que mais impactam a extração estruturada

| Tipo de erro | Impacto | Motivo |
|---|---|---|
| Separador de milhar 9.999 vs 9999 | Alto | Valor extraído errado — passou como OK antes da correção |
| Segmentação "A justa" vs "ajusta" | Médio | LLM compensa na maioria dos casos mas não é garantido |
| Não-determinismo em áudio ambíguo | Médio | Comportamento imprevisível — dificulta reprodutibilidade |
| Forçar vocabulário fora do domínio | Médio | Resultado parece válido mas não é |
| Capitalização mmHG vs mmHg | Baixo | Normalizer resolve |

---

## c. Mitigações implementadas

| Mitigação | Implementação | Resultado |
|---|---|---|
| initial_prompt com vocabulário técnico | `language="pt", initial_prompt="frequência, pressão..."` | WER de 20.6% para 6.7% |
| Normalização lexical | dicionário de correções no normalizer.py | erros ortográficos e unidades corrigidos |
| Separador de milhar | `re.sub(r'(\d+)\.(\d{3})\b', r'\1\2', texto)` | "9.999" → "9999" |
| Validação de range | `validar_range()` no extractor.py | valores críticos rejeitados automaticamente |
| Pós-processamento semântico | regras no system prompt do LLM | múltiplos comandos detectados como AMBIGUO |

---

## Conclusão

O `initial_prompt` foi a mitigação mais impactante — reduziu erros de segmentação de 50% dos casos para 0% e o WER médio de 20.6% para 6.7%. O principal risco residual é o não-determinismo do Whisper base em áudios ambíguos, que gera transcrições imprevisíveis mas que o pipeline trata corretamente como INVALIDO.
