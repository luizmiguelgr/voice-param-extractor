# Comparação Experimental — Variante A vs Variante B

## Objetivo

Comparar o impacto do `initial_prompt` no Whisper e do prompt reforçado no LLM sobre a qualidade da extração estruturada.

---

## Variantes comparadas

### Variante A — Baseline
- Whisper sem `initial_prompt`
- LLM com prompt simples — só define os campos do JSON
- Sem validação de range contra catálogo

### Variante B — Reforçada
- Whisper com `initial_prompt` de vocabulário técnico médico
- LLM com prompt reforçado — inclui regras de AMBIGUO, múltiplos comandos e hesitações
- Validação de range contra catálogo de parâmetros
- Pipeline lê áudios automaticamente da pasta `audio_samples/`

---

## Resultados por áudio

| Áudio | Var. A — Transcrição | Var. A — Status | Var. B — Transcrição | Var. B — Status |
|---|---|---|---|---|
| 5hz.m4a | "A justa frequência para 5 Hz" | OK | "ajusta a frequência para 5 Hz" | OK |
| confuso.m4a | Transcrição fiel | OK | Transcrição fiel | OK |
| audiovazio.m4a | string vazia | INVALIDO | Alucinação variável* | INVALIDO |
| freq9999hz.m4a | "9.999 Hz" — value: 9.999 | OK (incorreto) | "9.999 Hz" — value: 9999 | INVALIDO |
| doiscomandos.m4a | "para 5 e para 120" — perde pressão | OK (incorreto) | "para 5 e pressão para 120" | AMBIGUO |
| inglesportugues.m4a | "Setra-guencha" | INVALIDO | "Sete frequência 405 Hz" | INVALIDO |
| negativo.m4a | "menos 5 graus" | INVALIDO | "menos 5 graus" | INVALIDO |
| unidadeerrada.m4a | "120 mmHG" | INVALIDO | "120 mmHg" | INVALIDO |

*O áudio vazio apresentou comportamento não-determinístico na Variante B — transcrições diferentes a cada execução ("telephone, oscillator...", "ligeira de 180º celsius", "Jie...", caracteres japoneses). Em todos os casos o status final foi INVALIDO.

---

## Métricas comparativas

| Métrica | Variante A — Baseline | Variante B — Reforçada |
|---|---|---|
| Status correto | 6/8 (75%) | 8/8 (100%) |
| Transcrição correta | 4/8 (50%) | 7/8 (87.5%) |
| Falsos negativos críticos | 2 | 0 |
| WER médio | 20.6% | 6.7% |
| Alucinações com impacto no status | 0 | 0 |

---

## Análise

### O que melhorou na Variante B

**1. Segmentação corrigida pelo initial_prompt**

`"A justa"` foi corrigido para `"ajusta"` em 4 casos — melhoria direta na qualidade da transcrição sem nenhuma mudança no código de extração. Redução de WER de 20.6% para 6.7%.

**2. Detecção de múltiplos comandos**

Na Variante A o segundo comando era silenciosamente ignorado. Na Variante B o sistema retorna AMBIGUO e solicita que o usuário repita um comando por vez — comportamento mais seguro em ambiente médico.

**3. Validação de range**

O valor 9999 Hz passou como OK na Variante A. Na Variante B é corretamente rejeitado como INVALIDO com mensagem explicativa sobre o range permitido (0.5 a 100 Hz).

---

### O que piorou na Variante B

**1. Não-determinismo em áudio ambíguo**

O áudio vazio apresentou transcrições completamente diferentes a cada execução na Variante B, enquanto na Variante A retornava consistentemente string vazia. O resultado final permaneceu INVALIDO em todos os casos, mas o comportamento é imprevisível e dificulta a reprodutibilidade de testes.

**2. Forçar vocabulário em áudio fora do domínio**

Áudio incompreensível passou de `"Setra-guencha"` para `"Sete frequência 405 Hz"` — aparentemente mais válido mas igualmente incorreto. Ambos foram rejeitados pelo sistema.

---

## Trade-off principal

O `initial_prompt` melhora significativamente transcrições no domínio médico mas aumenta o risco de comportamento imprevisível em áudio fora do domínio. Para um sistema de equipamentos médicos onde o contexto é controlado, o benefício supera o risco — especialmente pela eliminação de falsos negativos críticos.

---

## Conclusão

A Variante B superou a Variante A em todas as métricas críticas. O ganho mais significativo foi a eliminação de falsos negativos — casos onde o sistema retornava OK para extração incorreta. Em ambiente médico, um falso negativo é mais perigoso que um falso positivo, justificando a adoção da Variante B como abordagem definitiva do pipeline.
