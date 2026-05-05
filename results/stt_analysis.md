# Análise de Erros do STT

## Conjunto de amostras testadas

| Arquivo | Comando falado | Transcrição sem initial_prompt | Transcrição com initial_prompt |
|---|---|---|---|
| 5hz.m4a | "Ajusta a frequência para 5 Hz" | "A justa frequência para 5 Hz" | "ajusta a frequência para 5 Hz" |
| confuso.m4a | "Não sei... vou querer volume 50 ml" | Transcrição fiel | Transcrição fiel |
| audiovazio.m4a | silêncio/ruído | string vazia | Variável — ver nota |
| freq9999hz.m4a | "Ajusta frequência para 9999 Hz" | "Ajustar a frequência para 9.999 Hz" | "ajustar frequência para 9.999 Hz" |
| doiscomandos.m4a | "Ajusta frequência para 5 e pressão para 120" | "A justa frequência para 5 e para 120" | "ajusta a frequência para 5 e pressão para 120" |
| inglesportugues.m4a | mistura inglês/português | "Setra-guencha 4, 5 heredas" | "Sete frequência 405 Hz, 5 Hz" |
| negativo.m4a | "Ajusta temperatura para menos 5 graus" | Transcrição fiel | Transcrição fiel |
| unidadeerrada.m4a | "Ajusta frequência para 120 mmHg" | "A justa frequência para 120 mmHG" | "ajusta frequência para 120 mmHg" |

**Nota sobre audiovazio.m4a:** o arquivo contém ruído de fundo sem fala inteligível. Na Variante B, o Whisper gerou transcrições completamente diferentes a cada execução — "telephone, oscillator, Saul e também Charme destreitor HAVE", "ligeira de 180º celsius", "Jie...", caracteres japoneses e coreanos. Este comportamento é chamado de não-determinismo e é uma característica conhecida do Whisper em áudios ambíguos. Em todos os casos o status final foi INVALIDO.

---

## a. Tipos de erro mais frequentes

### 1. Segmentação incorreta de palavras

O Whisper separou o verbo em duas palavras válidas do português. É um erro silencioso — não aparece como erro ortográfico e o normalizer não consegue corrigir porque "a justa" são palavras válidas em outro contexto.

| Ocorrência | Sem prompt | Com prompt |
|---|---|---|
| 5hz.m4a | "A justa" | "ajusta" |
| doiscomandos.m4a | "A justa" | "ajusta" |
| unidadeerrada.m4a | "A justa" | "ajusta" |

Frequência: Alta — apareceu em 4 dos 8 áudios sem initial_prompt. Resolvido completamente com initial_prompt.

---

### 2. Separador de milhar europeu

O Whisper usou ponto como separador de milhar ao transcrever números grandes, fazendo o sistema interpretar 9999 como 9.999.

| Ocorrência | Transcrito | Esperado |
|---|---|---|
| freq9999hz.m4a | "9.999 Hz" | "9999 Hz" |

Frequência: Média — aparece em números acima de 999. Mitigado pelo normalizer com regex.

---

### 3. Não-determinismo em áudio ambíguo

O mesmo arquivo de áudio pode gerar transcrições completamente diferentes a cada execução do Whisper. Observado exclusivamente no audiovazio.m4a, que contém ruído sem fala inteligível.

| Execução | Transcrição gerada |
|---|---|
| 1 | "telephone, oscillator, Saul e também Charme destreitor HAVE" |
| 2 | "ligeira de 180º celsius" |
| 3 | "Jie..." |
| 4 | caracteres japoneses e coreanos |

Frequência: Baixa — ocorre em áudio sem fala clara. O status final permaneceu INVALIDO em todos os casos.

---

### 4. Forçar vocabulário em áudio fora do domínio

Com `initial_prompt`, o Whisper tenta encaixar o áudio no vocabulário médico mesmo quando o áudio não tem relação com o domínio.

| Situação | Sem prompt | Com prompt |
|---|---|---|
| inglesportugues.m4a | "Setra-guencha 4, 5 heredas" | "Sete frequência 405 Hz, 5 Hz" |

Frequência: Baixa. O resultado com prompt parece mais válido mas foi igualmente rejeitado pelo sistema.

---

## b. Erros que mais impactam a extração estruturada

| Tipo de erro | Impacto | Motivo |
|---|---|---|
| Separador de milhar 9.999 vs 9999 | Alto | Valor extraído errado — passou como OK antes da correção |
| Segmentação "A justa" vs "ajusta" | Médio | LLM compensa na maioria dos casos mas não é garantido |
| Não-determinismo em áudio ambíguo | Médio | Comportamento imprevisível — dificulta reprodutibilidade |
| Forçar vocabulário fora do domínio | Médio | Resultado parece válido mas não é |
| Capitalização de unidades mmHG vs mmHg | Baixo | Normalizer resolve |

---

## c. Mitigações implementadas

### 1. initial_prompt com vocabulário técnico

```python
resultado = modelo.transcribe(
    caminho_audio,
    language="pt",
    initial_prompt="frequência, pressão, volume, temperatura, Hz, mmHg, ml, ajustar, aumentar, diminuir"
)
```

Resultado: reduziu segmentação incorreta de 4 para 0 casos. Reduziu WER médio de 20.6% para 6.7%.

---

### 2. Normalização lexical

Correção de erros ortográficos e unidades com grafia errada.

| Entrada | Saída |
|---|---|
| "frekencia" | "frequência" |
| "hertz" | "Hz" |
| "mmhg" | "mmHg" |
| "presao" | "pressão" |

---

### 3. Tratamento de separador de milhar

```python
texto = re.sub(r'(\d+)\.(\d{3})\b', r'\1\2', texto)
```

Resultado: "9.999" convertido para "9999" corretamente.

---

### 4. Validação de range por parâmetro

Valores fora do range definido no catálogo são automaticamente marcados como INVALIDO com mensagem explicativa. Protege contra valores perigosos que passariam despercebidos sem essa camada.

---

### 5. Pós-processamento semântico no LLM

O system prompt instrui o LLM a detectar múltiplos comandos e retornar AMBIGUO em vez de executar silenciosamente apenas o primeiro.

---

## Conclusão

O `initial_prompt` foi a mitigação mais impactante — reduziu erros de segmentação de 50% dos casos para 0% e o WER médio de 20.6% para 6.7%. O principal risco identificado é o não-determinismo do Whisper base em áudios ambíguos, que gera transcrições imprevisíveis mas que o pipeline trata corretamente como INVALIDO.
