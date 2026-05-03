import pytest
from src.normalizer import normalizar
from src.extractor import extract

# ─── Testes do Normalizer ───────────────────────────────────────────────────

def test_corrige_erro_ortografico():
    assert "frequência" in normalizar("frekencia")

def test_converte_numero_por_extenso():
    assert "5" in normalizar("cinco")

def test_converte_unidade():
    assert "Hz" in normalizar("hertz")

def test_remove_espacos_duplos():
    resultado = normalizar("ajusta  a  frequência")
    assert "  " not in resultado

# ─── Testes do Extractor ────────────────────────────────────────────────────

def test_caso_valido_simples():
    resultado = extract("ajuste a frequência para 5 Hz")
    assert resultado.status == "OK"
    assert resultado.value == 5.0
    assert resultado.unit == "Hz"

def test_unidade_omitida():
    resultado = extract("aumenta pressão para 120")
    assert resultado.status == "OK"
    assert resultado.value == 120.0
    assert resultado.parameter == "pressao"

def test_caso_incompleto():
    resultado = extract("muda o volume")
    assert resultado.status == "INCOMPLETO"
    assert resultado.value is None

def test_caso_ambiguo():
    resultado = extract("ajusta para 5")
    assert resultado.status in ["AMBIGUO", "INCOMPLETO"]

def test_valor_fora_do_esperado():
    resultado = extract("ajusta a frequência para 99999 Hz")
    assert resultado.requires_confirmation == True

def test_saida_sempre_tem_status():
    resultado = extract("xpto blargh 123 zzz")
    assert resultado.status is not None
    assert resultado.intent is not None