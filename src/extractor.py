from groq import Groq
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError
from typing import Optional
import os
import json
import unicodedata

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Carrega o catálogo de parâmetros
with open("data/commands_catalog.json", "r", encoding="utf-8") as f:
    CATALOGO = json.load(f)

PARAMETROS = {p["id"]: p for p in CATALOGO["parameters"]}

# Schema de saída com Pydantic
class ExtractionResult(BaseModel):
    intent: str  # o que o user quer fazer
    parameter: Optional[str] = None # parâmetro (freq, pressão)
    value: Optional[float] = None   # valor
    unit: Optional[str] = None      #hz, mmHg...
    status: str                     #ok, ambiguo, incpompleto, inválido
    requires_confirmation: bool = False
    validation_errors: list = []    #erros encontrados
    notes: Optional[str] = None     #observações

SYSTEM_PROMPT = """
você é um sistema de extração de parâmetros para <equipamentos médicos>.
recebe comandos em português do brasil e retorna apenas um JSON válido

Campos obrigatórios:
- intent: "ajustar_parâmetro", "consultar_parametro" ou "comando_invalido
- parameter: nome do parâmetro (exemplo: "frequencia", "pressao", "volume")
- value: valor numérico extraído
- unit: unidade (exemplo: "Hz", "mmHg", "ml")
- status: "OK", "AMBIGUO", "INCOMPLETO" ou "INVALIDO"
- requires_confirmation: true se o valor for crítico
- validation_errors: lista de erros encontrados
- notes: observações sobre a extração

Regras importantes:
- Se o comando contiver mais de um parâmetro a ser ajustado, retorne status "AMBIGUO" com validation_errors explicando que múltiplos comandos foram detectados
- Se faltar o valor ou parâmetro, retorne status "INCOMPLETO"
- Se o comando não fizer sentido, retorne status "INVALIDO"
- Ignore hesitações como "ééé", "hmm", "não sei" e extraia apenas o comando definitivo

Retorne somente o JSON, sem explicações, sem markdown.
"""

def remover_acentos(texto: str) -> str:
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )

def validar_range(resultado: ExtractionResult) -> ExtractionResult:
    if resultado.parameter and resultado.value is not None:
        param_normalizado = remover_acentos(resultado.parameter.lower())
        param = PARAMETROS.get(param_normalizado)

        if param:
            if resultado.value < param["range_min"] or resultado.value > param["range_max"]:
                resultado.status = "INVALIDO"
                resultado.requires_confirmation = True
                resultado.validation_errors.append(
                    f"Valor {resultado.value} fora do range permitido "
                    f"({param['range_min']} a {param['range_max']} {param['unit']})"
                )
    return resultado

def extract(text: str) -> ExtractionResult:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text}
        ],
        temperature=0
    )

    raw = response.choices[0].message.content.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        data = json.loads(raw)
        return validar_range(ExtractionResult(**data))
    except (json.JSONDecodeError, ValidationError) as e:
        return ExtractionResult(
            intent="comando_inválido",
            status="INVALIDO",
            validation_erros=[str(e)],
            notes=f"Falha no parsing resposta do modelo: {raw}"
            #parsing = análise sintática
        )
    
if __name__ == "__main__":
    testes = [
        "Ajusta a frequência para 5 hertz",
        "aumenta pressão pra 120",
        "muda o volume"
    ]

    for texto in testes:
        print(f"\nEntrada: {texto}")
        resultado = extract(texto)
        print(resultado.model_dump_json(indent=2))