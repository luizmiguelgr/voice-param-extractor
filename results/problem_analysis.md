# Análise Inicial do Problema

## 1. Artefatos mínimos definidos

| Artefato | Arquivo | Descrição |
|---|---|---|
| Catálogo de comandos | `data/commands_catalog.json` | Intenções, parâmetros, ranges e unidades suportadas |
| Schema de saída | `src/extractor.py` | Estrutura validável do JSON de saída via Pydantic |
| Amostras de áudio | `audio_samples/` | 8 gravações cobrindo casos normais e de borda |
| Transcrições de referência | `results/wer_evaluation.py` | Transcrições manuais para cálculo de WER |
| Casos de teste | `data/test_cases.json` | 8 casos com entrada e saída esperada |
| Métricas de avaliação | `results/evaluation.py` | Script automático de precisão e status |
| Análise STT | `results/stt_analysis.md` | Erros, impacto e mitigações |
| Comparação experimental | `results/experimental_comparison.md` | Variante A vs Variante B |

## 2. Como os artefatos foram construídos

Os áudios foram gravados localmente simulando comandos reais de um profissional de saúde, cobrindo casos limpos, confusos, com hesitação, em idioma errado, com valores fora do range e com múltiplos comandos. O catálogo de comandos foi definido com parâmetros comuns em equipamentos médicos (frequência, pressão, volume, temperatura) com ranges fisiológicos realistas. Os casos de teste cobrem todos os status possíveis do sistema: OK, INCOMPLETO, AMBIGUO e INVALIDO.

## 3. Dificuldades identificadas no domínio

As principais dificuldades são ambiguidades semânticas (comando sem parâmetro explícito, múltiplos comandos no mesmo áudio, valor sem unidade), casos incompletos (parâmetro sem valor, comando vago) e inconsistências de transcrição do STT. Para detalhes completos sobre erros de transcrição e mitigações, ver [results/stt_analysis.md](results/stt_analysis.md).

## 4. Estratégia escolhida

O protótipo adota uma abordagem híbrida com quatro camadas:

| Camada | Responsabilidade |
|---|---|
| STT com reforço de domínio | Whisper com `initial_prompt` de vocabulário técnico médico |
| Normalização determinística | Correção de erros ortográficos, unidades e separador de milhar |
| Extração semântica com LLM | Extração de intenção, parâmetro, valor e unidade com schema enforcement via Pydantic |
| Validação por regras | Verificação do valor contra ranges do catálogo com rejeição automática de valores fora dos limites |

Regras puras não escalam para variações linguísticas do português brasileiro. LLM puro sem validação pode aceitar valores perigosos fora do range. A abordagem híbrida combina robustez semântica com precisão determinística — essencial em domínio médico. Para análise detalhada dos resultados, ver [results/experimental_comparison.md](results/experimental_comparison.md).
