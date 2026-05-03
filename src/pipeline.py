from src.normalizer import normalizar
from src.extractor import extract

def processar(texto: str):
    print(f"Entrada:    {texto}")

    normalizado = normalizar(texto)
    print(f"Normalizando: {normalizado}")

    resultado = extract(normalizado)
    print(f"Saída:\n{resultado.model_dump_json(indent=2)}\n")

    return resultado

if __name__ == "__main__":
    testes = [
        "ajusta a frekencia pra cinco Hz",
        "aumenta presao pra 120",
        "muda o volume",
        "dois ponto cinco Hz",
        "ééé ajusta a frequência pra 5",
    ]

    for texto in testes:
        processar(texto)
        print("-" * 50)