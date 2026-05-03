from groq import Groq
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError
from typing import Optional
import os, json

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

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

Retorne somente o JSON, sem explicações, sem markdown.
"""

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

    try:
        data = json.loads(raw)
        return ExtractionResult(**data)
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