import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.extractor import extract
from src.extractor import remover_acentos

# Carrega os casos de teste
with open("data/test_cases.json", "r", encoding="utf-8") as f:
    data = json.load(f)

casos = data["test_cases"]

# Contadores
total = len(casos)
status_correto = 0
parameter_correto = 0
value_correto = 0
unit_correto = 0
erros = []

print(f"{'ID':<8} {'Categoria':<20} {'Status':<10} {'Parâmetro':<12} {'Valor':<8} {'Resultado'}")
print("-" * 80)

for caso in casos:
    entrada = caso["input"]
    esperado = caso["expected"]

    resultado = extract(entrada)

    # Verifica status
    s_ok = resultado.status == esperado.get("status", resultado.status)

    # Verifica parâmetro (se esperado tiver)
    p_ok = True
    if "parameter" in esperado:
        p_ok = remover_acentos(resultado.parameter or "") == remover_acentos(esperado["parameter"])

    # Verifica valor (se esperado tiver)
    v_ok = True
    if "value" in esperado:
        v_ok = resultado.value == esperado["value"]

    # Verifica unidade (se esperado tiver)
    u_ok = True
    if "unit" in esperado:
        u_ok = resultado.unit == esperado["unit"]

    # Contabiliza
    if s_ok: status_correto += 1
    if p_ok: parameter_correto += 1
    if v_ok: value_correto += 1
    if u_ok: unit_correto += 1

    geral = "OK" if all([s_ok, p_ok, v_ok, u_ok]) else "ERRO"

    print(f"{caso['id']:<8} {caso['category']:<20} {'OK' if s_ok else 'ERRO':<10} {'OK' if p_ok else 'ERRO':<12} {'OK' if v_ok else 'ERRO':<8} {geral}")

    if not all([s_ok, p_ok, v_ok, u_ok]):
        erros.append({
            "id": caso["id"],
            "input": entrada,
            "esperado": esperado,
            "obtido": resultado.model_dump()
        })

# Métricas finais
print("\n" + "=" * 80)
print(f"TOTAL DE CASOS:        {total}")
print(f"STATUS correto:        {status_correto}/{total} ({status_correto/total*100:.1f}%)")
print(f"PARÂMETRO correto:     {parameter_correto}/{total} ({parameter_correto/total*100:.1f}%)")
print(f"VALOR correto:         {value_correto}/{total} ({value_correto/total*100:.1f}%)")
print(f"UNIDADE correta:       {unit_correto}/{total} ({unit_correto/total*100:.1f}%)")

precisao = sum([s_ok and p_ok and v_ok and u_ok for caso in casos
                for s_ok, p_ok, v_ok, u_ok in [(
                    extract(caso["input"]).status == caso["expected"].get("status", ""),
                    True, True, True
                )]]) / total

print(f"\nACURÁCIA GERAL:        {status_correto/total*100:.1f}%")

# Salva erros
if erros:
    print(f"\nERROS ENCONTRADOS ({len(erros)}):")
    for e in erros:
        print(f"\n  [{e['id']}] {e['input']}")
        print(f"  Esperado: {e['esperado']}")
        print(f"  Obtido:   status={e['obtido']['status']}, parameter={e['obtido']['parameter']}, value={e['obtido']['value']}")
