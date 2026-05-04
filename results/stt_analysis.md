# Análise de Erros do STT

## Conjunto de amostras testadas

| Arquivo | Comando falado | Transcrição sem initial_prompt | Transcrição com initial_prompt |
|---|---|---|---|
| 5hz.m4a | "Ajusta a frequência para 5 Hz" | "A justa frequência para 5 Hz" ❌ | "ajusta a frequência para 5 Hz" ✅ |
| confuso.m4a | "Não sei... vou querer volume 50 ml" | Transcrição fiel ✅ | Transcrição fiel ✅ |
| audiovazio.m4a | silêncio | "" ✅ | Alucinação com caracteres japoneses ⚠️ |
| freq9999hz.m4a | "Ajusta frequência para 9999 Hz" | "Ajustar a frequência para 9.999 Hz" ❌ | "ajustar frequência para 9.999 Hz" ❌ |
| doiscomandos.m4a | "Ajusta frequência para 5 e pressão para 120" | "A justa frequência para 5 e para 120" ❌ | "ajusta a frequência para 5 e pressão para 120" ✅ |
| inglesportugues.m4a | mistura inglês/português | "Setra-guencha 4, 5 heredas" ❌ | "Sete frequência 405 Hz, 5 Hz" ⚠️ |
| negativo.m4a | "Ajusta temperatura para menos 5 graus" | Transcrição fiel ✅ | Transcrição fiel ✅ |
| unidadeerrada.m4a | "Ajusta frequência para 120 mmHg" | "A justa frequência para 120 mmHG" ❌ | "ajusta frequência para 120 mmHg" ✅ |

---

## a. Tipos de erro mais frequentes

### 1. Segmentação incorreta de palavras
**Exemplo:** `"Ajusta"` → `"A justa"`

O Whisper separou o verbo em duas palavras válidas do português.
É um erro silencioso — não aparece como erro ortográfico e o
normalizer não consegue corrigir porque "a justa" são palavras válidas.

**Frequência:** Alta — apareceu em 4 dos 8 áudios sem initial_prompt.
**Com initial_prompt:** Resolvido em todos os casos.

---

### 2. Separador de milhar europeu
**Exemplo:** `"9999"` → `"9.999"`

O Whisper usou ponto como separador de milhar ao transcrever
números grandes, fazendo o sistema interpretar 9999 como 9.999.

**Frequência:** Média — aparece em números acima de 999.
**Mitigação aplicada:** regex no normalizer converte `9.999` → `9999`.

---

### 3. Alucinação em áudio vazio ou silêncio
**Exemplo:** silêncio → `"e vai pessim仗ar que joga o immersed..."`

Com `initial_prompt` ativo, o Whisper tentou transcrever silêncio
e gerou texto com caracteres japoneses e coreanos.

**Frequência:** Baixa — só ocorre em áudio sem fala clara.
**Risco:** O LLM corretamente retornou INVALIDO, mas o comportamento é imprevisível.

---

### 4. Forçar vocabulário em áudio incompreensível
**Exemplo:** inglês misturado → `"Setra-guencha"` sem prompt, `"Sete frequência 405 Hz"` com prompt

Com `initial_prompt`, o Whisper tenta encaixar o áudio no vocabulário
médico mesmo quando o áudio não tem nada a ver com o domínio.

**Frequência:** Baixa — só ocorre em áudio fora do domínio.
**Observação:** O resultado pareceu mais válido mas ainda foi corretamente rejeitado pelo range.

---

## b. Erros que mais impactam a extração estruturada

| Tipo de erro | Impacto | Motivo |
|---|---|---|
| Separador de milhar `9.999` vs `9999` | **Alto** | Valor extraído errado, passou como OK antes da correção |
| Segmentação `"A justa"` vs `"Ajusta"` | **Médio** | LLM compensa na maioria dos casos mas não é garantido |
| Alucinação em silêncio | **Médio** | LLM retorna INVALIDO mas comportamento é imprevisível |
| Forçar vocabulário em áudio fora do domínio | **Médio** | Resultado parece válido mas não é |
| Capitalização de unidades `mmHG` vs `mmHg` | **Baixo** | Normalizer resolve |

---

## c. Mitigações implementadas

### 1. initial_prompt com vocabulário técnico ✅
```python
resultado = modelo.transcribe(
    caminho_audio,
    language="pt",
    initial_prompt="frequência, pressão, volume, temperatura, Hz, mmHg, ml, ajustar, aumentar, diminuir"
)
```
**Resultado:** reduziu segmentação incorreta de 4 para 0 casos.

---

### 2. Normalização lexical ✅
Correção de erros ortográficos e unidades com grafia errada.
```
"frekencia" → "frequência"
"hertz"     → "Hz"
"mmhg"      → "mmHg"
```

---

### 3. Tratamento de separador de milhar ✅
```python
texto = re.sub(r'(\d+)\.(\d{3})\b', r'\1\2', texto)
```
**Resultado:** `"9.999"` → `"9999"` corretamente.

---

### 4. Validação de range por parâmetro ✅
Valores fora do range definido no catálogo são automaticamente
marcados como INVALIDO com mensagem explicativa.

---

### 5. Pós-processamento semântico no LLM ✅
O system prompt instrui o LLM a detectar múltiplos comandos
e retornar AMBIGUO em vez de ignorar silenciosamente.

---

## Mitigações recomendadas para produção

### Voice Activity Detection (VAD)
Filtrar silêncio antes de passar pro Whisper eliminaria
alucinações em áudio vazio.
```python
# biblioteca recomendada: silero-vad
```

### Modelo maior do Whisper
O modelo `small` ou `medium` tem WER menor que o `base`
especialmente em português brasileiro com termos técnicos.

### Score de confiança
Rejeitar transcrições com score de confiança abaixo de um threshold
antes de passar pro LLM.

---

## Conclusão

O `initial_prompt` foi a mitigação mais impactante — reduziu
erros de segmentação de 50% dos casos para 0%. O principal
risco residual é a alucinação em áudio silencioso, mitigável
com VAD em ambiente de produção.
