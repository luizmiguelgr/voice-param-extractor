import whisper
import os

modelo = whisper.load_model("base")

def transcrever(caminho_audio: str) -> str:
    if not os.path.exists(caminho_audio):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_audio}")
    
    resultado = modelo.transcribe(
        caminho_audio,
        language="pt",
        initial_prompt="frequência, pressão, volume, temperatura, Hz, mmHg, ml, ajustar, aumentar, diminuir"
    )
    return resultado["text"].strip()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python -m src.stt caminho/para/audio.wav")
    else:
        texto = transcrever(sys.argv[1])
        print(f"Transcrição: {texto}")