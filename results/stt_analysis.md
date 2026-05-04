# Análise de Erros do STT

## Amostras testadas

| Arquivo | Comando falado | Transcrição gerada | Correto? |
|---|---|---|---|
| 5hz.m4a | "Ajusta a frequência para 5 Hz" | "A justa frequência para 5 Hz" | ❌ |
| confuso.m4a | "Não sei, aumenta a pressão... Vou querer volume 50 ml" | Transcrição fiel | ✅ |
| audiovazio.m4a | silêncio | "" | ✅ |
| freq9999hz.m4a | "Ajusta a frequência para 9999 Hz" | "Ajustar a frequência para 9.999 Hz" | ❌ |
| doiscomandos.m4a | "Ajusta frequência para 5 e pressão para 120" | "A justa frequência para 5 e para 120" | ❌ |
| inglesportugues.m4a | mistura inglês/português | "Setra-guencha 4, 5 heredas" | ❌ |
| negativo.m4a | "Ajusta temperatura para menos 5 graus" | Transcrição fiel | ✅ |
| unidadeerrada.m4a | "Ajusta frequência para 120 mmHg" | "A justa frequência para 120 mmHG" | ⚠️ |

## Erros encontrados

### 1. Segmentação incorreta de palavras
**Exemplo:** `"Ajusta"` → `"A justa"`

O Whisper separou o verbo em duas palavras válidas do português.
É um erro silencioso — não aparece como erro ortográfico.

**Impacto:** Baixo — o LLM foi robusto e extraiu corretamente mesmo assim.

**Mitigação:** `initial_prompt` com vocabulário do domínio.

---

### 2. Separador de milhar europeu em números grandes
**Exemplo:** `"9999"` → `"9.999"`

O Whisper usou ponto como separador de milhar, fazendo o LLM
interpretar `9999` como `9.999` decimal.

**Impacto:** Alto — o valor extraído está errado e passa como `OK`.

**Mitigação:** Normalizar padrão `\d+\.\d{3}` como separador de milhar.

---

### 3. Dois comandos no mesmo áudio
**Exemplo:** `"frequência para 5 e pressão para 120"` → LLM extrai só o primeiro

O pipeline atual não suporta múltiplos comandos por áudio.

**Impacto:** Médio — o segundo comando é silenciosamente ignorado.

**Mitigação:** Detectar `"e"` entre dois comandos e retornar `AMBIGUO`.

---

### 4. Áudio em idioma misto ou incompreensível
**Exemplo:** transcrição virou `"Setra-guencha 4, 5 heredas"`

O Whisper tentou transcrever mesmo sem entender — alucinação total.

**Impacto:** Baixo — o LLM corretamente retornou `INVALIDO`.

**Mitigação:** Validar score de confiança do Whisper antes de processar.

---

### 5. Capitalização inconsistente de unidades
**Exemplo:** `"mmHG"` → normalizer corrigiu para `"mmHg"` ✅

O normalizer resolveu esse caso com sucesso.

## Erros por impacto

| Tipo de erro | Impacto | Resolvido? |
|---|---|---|
| Separador de milhar `9.999` vs `9999` | Alto | ❌ |
| Dois comandos no mesmo áudio | Médio | ❌ |
| Segmentação `"A justa"` | Baixo | ✅ LLM compensa |
| Idioma incompreensível | Baixo | ✅ LLM retorna INVALIDO |
| Capitalização de unidades | Baixo | ✅ normalizer resolve |

## Mitigações implementadas

- Parser robusto que remove markdown do JSON quando o LLM formata errado
- Normalizer corrige unidades com capitalização inconsistente
- LLM com `temperature=0` para respostas determinísticas

## Limitações conhecidas

- Pipeline não suporta múltiplos comandos por áudio
- Números grandes podem ser interpretados com separador de milhar errado
- Whisper base pode alucinar em áudio incompreensível

## Trabalhos futuros

- Adicionar `initial_prompt` com vocabulário técnico no Whisper
- Validar `value` contra `range_min`/`range_max` do catálogo
- Detectar múltiplos comandos e retornar `AMBIGUO`
- Testar modelos maiores do Whisper (`small`, `medium`)
- Adicionar VAD para filtrar silêncio antes do STT