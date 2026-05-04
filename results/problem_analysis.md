# Análise Inicial do Problema

## 1. Artefatos mínimos definidos

| Artefato | Arquivo | Descrição |
|---|---|---|
| Catálogo de comandos | `data/commands_catalog.json` | Intenções, parâmetros, ranges e unidades suportadas |
| Schema de saída | `src/extractor.py` (Pydantic) | Estrutura validável do JSON de saída |
| Amostras de áudio | `audio_samples/` | 8 gravações reais cobrindo casos normais e de borda |
| Transcrições de referência | `results/wer_evaluation.py` | Transcrições manuais para cálculo de WER |
| Casos de teste | `data/test_cases.json` | 8 casos documentados com entrada e saída esperada |
| Casos de borda | `audio_samples/` + `data/test_cases.json` | Áudio vazio, valor fora do range, dois comandos, idioma errado |
| Métricas de avaliação | `results/evaluation.py` | Script automático de precisão e status |
| Análise STT | `results/stt_analysis.md` | Erros, impacto e mitigações |
| Comparação experimental | `results/experimental_comparison.md` | Variante A vs Variante B |

## 2. Como os artefatos foram construídos

**Áudios:** gravados pelo próprio candidato simulando comandos reais
de um profissional de saúde operando equipamento médico. Incluem
casos limpos, confusos, com hesitação, em idioma errado, com
valores fora do range e com múltiplos comandos.

**Catálogo de comandos:** definido com base no cenário do desafio,
incluindo os parâmetros mais comuns em equipamentos médicos
(frequência, pressão, volume, temperatura) com ranges fisiológicos
realistas.

**Casos de teste:** construídos para cobrir todos os status
possíveis do sistema — OK, INCOMPLETO, AMBIGUO e INVALIDO —
além de casos de borda específicos do domínio.

## 3. Dificuldades identificadas no domínio

### Ambiguidades
- Comando sem parâmetro explícito: `"ajusta para 5"` — qual parâmetro?
- Múltiplos comandos no mesmo áudio: qual executar?
- Valor ambíguo: `"aumenta a pressão"` — quanto aumenta?

### Números e unidades
- STT transcreve números grandes com separador de milhar europeu: `9999` → `9.999`
- Unidades técnicas transcritas de formas variadas: `"Hz"`, `"hertz"`, `"h z"`
- Números por extenso: `"cinco"`, `"cinquenta"`, `"cento e vinte"`
- Valores decimais por extenso: `"dois ponto cinco"`

### Variações de escrita e transcrição
- Segmentação incorreta: `"ajusta"` → `"a justa"`
- Erros ortográficos: `"frekencia"`, `"presao"`, `"volumme"`
- Capitalização de unidades: `"mmHG"` vs `"mmHg"`
- Hesitações e ruídos: `"ééé"`, `"hmm"`, pausas

### Casos incompletos
- Parâmetro sem valor: `"muda o volume"`
- Valor sem parâmetro: `"ajusta para 5"`
- Comando vago: `"aumenta a pressão"`

### Inconsistências de transcrição
- Alucinação em silêncio com `initial_prompt` ativo
- Forçar vocabulário médico em áudio fora do domínio

## 4. Estratégia escolhida para o protótipo

### Abordagem híbrida — LLM + regras determinísticas

O protótipo adota uma abordagem híbrida com três camadas:

**Camada 1 — STT com reforço de domínio**
Whisper com `initial_prompt` contendo vocabulário técnico médico,
reduzindo erros de segmentação e transcrição de termos específicos.

**Camada 2 — Normalização determinística**
Regras explícitas para corrigir o que o STT estraga de forma
previsível: erros ortográficos, unidades, números por extenso
e separador de milhar.

**Camada 3 — Extração semântica com LLM**
LLM com prompt estruturado para extrair intenção, parâmetro,
valor e unidade, tratando hesitações, múltiplos comandos e
casos ambíguos. Pydantic garante schema enforcement mesmo
quando o modelo retorna JSON malformado.

**Camada 4 — Validação por regras**
Validação do valor extraído contra ranges definidos no catálogo,
com rejeição automática de valores fora dos limites permitidos.

### Justificativa da escolha

Regras puras não escalam para variações linguísticas do português
brasileiro. LLM puro sem validação pode aceitar valores perigosos
fora do range. A abordagem híbrida combina a robustez semântica
do LLM com a precisão determinística das regras — essencial
em domínio médico onde erros têm consequências reais.