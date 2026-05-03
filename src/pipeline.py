from src.normalizer import normalizar
from src.extractor import extract
from src.stt import transcrever

def processar_audio(caminho_audio: str):
    print(f"Áudio:      {caminho_audio}")
    
    transcricao = transcrever(caminho_audio)
    print(f"Transcrição: {transcricao}")
    
    normalizado = normalizar(transcricao)
    print(f"Normalizado: {normalizado}")
    
    resultado = extract(normalizado)
    print(f"Saída:\n{resultado.model_dump_json(indent=2)}\n")
    
    return resultado

def processar(texto: str):
    print(f"Entrada:     {texto}")
    
    normalizado = normalizar(texto)
    print(f"Normalizado: {normalizado}")
    
    resultado = extract(normalizado)
    print(f"Saída:\n{resultado.model_dump_json(indent=2)}\n")
    
    return resultado

if __name__ == "__main__":
    print("=== ÁUDIO LIMPO ===")
    processar_audio("audio_samples/5hz.m4a")

    print("=== ÁUDIO CONFUSO ===")
    processar_audio("audio_samples/confuso.m4a")

    print("=== CASOS DE BORDA ===")
    casos_borda = [
        "audio_samples/audiovazio.m4a",
        "audio_samples/freq9999hz.m4a",
        "audio_samples/doiscomandos.m4a",
        "audio_samples/inglesportugues.m4a",
        "audio_samples/negativo.m4a",
        "audio_samples/unidadeerrada.m4a",
    ]

    for audio in casos_borda:
        print(f"\n{'='*50}")
        processar_audio(audio)