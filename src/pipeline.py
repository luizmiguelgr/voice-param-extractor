import os
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

if __name__ == "__main__":
    pasta = "audio_samples"
    extensoes = (".wav", ".mp3", ".m4a", ".ogg", ".flac")

    audios = [
        f for f in sorted(os.listdir(pasta))
        if f.lower().endswith(extensoes)
    ]

    if not audios:
        print("Nenhum áudio encontrado!")
    else:
        for nome in audios:
            caminho = os.path.join(pasta, nome)
            processar_audio(caminho)
            print("=" * 50)