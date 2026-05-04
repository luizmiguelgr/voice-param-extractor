import re

# Palavras técnicas com grafia errada
CORRECOES = {
    "frekencia": "frequência",
    "frequencia": "frequência",
    "presao": "pressão",
    "pressao": "pressão",
    "volumme": "volume",
    "hertz": "Hz",
    "hz": "Hz",
    "milimetros de mercurio": "mmHg",
    "mmhg": "mmHg",
    "mililitros": "ml",
}

# Números por extenso

NUMEROS = {
    "zero": "0", "um": "1", "dois": "2", "três": "3", "tres": "3",
    "quatro": "4", "cinco": "5", "seis": "6", "sete": "7",
    "oito": "8", "nove": "9", "dez": "10", "vinte": "20",
    "trinta": "30", "quarenta": "40", "cinquenta": "50",
    "sessenta": "60", "setenta": "70", "oitenta": "80",
    "noventa": "90", "cem": "100", "cento": "100",
    "cento e vinte": "120", "cento e cinquenta": "150", 
}

def normalizar(texto: str) -> str:
    texto = texto.lower().strip()

    # Converte números por extenso (frases primeiro, depois palavras)
    for extenso, numero in sorted(NUMEROS.items(), key=lambda x: -len(x[0])):
        texto = re.sub(rf'\b{extenso}\b', numero, texto, flags=re.IGNORECASE)
    
    # Corrige as palavras técnicas
    for palavras_erradas, palavras_certas in CORRECOES.items():
        texto = re.sub(rf'\b{palavras_erradas}\b', palavras_certas, texto, flags=re.IGNORECASE)

    # Remove espaços duplos
    texto = re.sub(r'\s+', ' ', texto).strip()

    # Separador de milhar europeu (de 9.999 para 9999)
    texto = re.sub(r'(\d+)\.(\d{3})\b', r'\1\2', texto)

    return texto