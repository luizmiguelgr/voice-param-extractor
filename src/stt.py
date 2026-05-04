import whisper

modelo = whisper.load_model("base")

def transcrever(caminho_audio: str) -> str:
    resultado = modelo.transcribe(
        caminho_audio,
        language="pt",
        initial_prompt="frequência, pressão, volume, temperatura, Hz, mmHg, ml, ajustar, aumentar, diminuir"
    )
    return resultado["text"].strip()