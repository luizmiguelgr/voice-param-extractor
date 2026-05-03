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
    print("=== TESTE COM ÁUDIO ===")
    processar_audio("audio_samples/5hz.m4a")

    print("=== TESTE COM TEXTO ===")
    processar("ajusta a frequência para 5 Hz")