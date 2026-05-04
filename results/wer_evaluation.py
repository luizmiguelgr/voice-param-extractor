def calcular_wer(referencia: str, hipotese: str) -> float:
    ref = referencia.lower().split()
    hip = hipotese.lower().split()

    d = [[0] * (len(hip) + 1) for _ in range(len(ref) + 1)]

    for i in range(len(ref) + 1):
        d[i][0] = i
    for j in range(len(hip) + 1):
        d[0][j] = j

    for i in range(1, len(ref) + 1):
        for j in range(1, len(hip) + 1):
            if ref[i-1] == hip[j-1]:
                d[i][j] = d[i-1][j-1]
            else:
                d[i][j] = 1 + min(d[i-1][j], d[i][j-1], d[i-1][j-1])

    return d[len(ref)][len(hip)] / len(ref) if ref else 0.0


# Referências e transcrições reais coletadas
amostras = [
    {
        "arquivo": "5hz.m4a",
        "referencia": "ajusta a frequência para 5 Hz",
        "sem_prompt": "A justa frequência para 5 Hz",
        "com_prompt": "ajusta a frequência para 5 Hz",
    },
    {
        "arquivo": "confuso.m4a",
        "referencia": "não sei aumenta a pressão não muda frequência não vou querer volume 50 ml",
        "sem_prompt": "Não sei aumenta a pressão não muda frequência não vou querer volume 50 ml",
        "com_prompt": "não sei aumenta pressão não muda frequência não vou querer volume 50 ml",
    },
    {
        "arquivo": "freq9999hz.m4a",
        "referencia": "ajustar a frequência para 9999 Hz",
        "sem_prompt": "Ajustar a frequência para 9.999 Hz",
        "com_prompt": "ajustar frequência para 9.999 Hz",
    },
    {
        "arquivo": "doiscomandos.m4a",
        "referencia": "ajusta a frequência para 5 e pressão para 120",
        "sem_prompt": "A justa frequência para 5 e para 120",
        "com_prompt": "ajusta a frequência para 5 e pressão para 120",
    },
    {
        "arquivo": "negativo.m4a",
        "referencia": "ajustar temperatura para menos 5 graus",
        "sem_prompt": "ajustar temperatura para menos 5 graus",
        "com_prompt": "ajustar temperatura para menos 5 graus",
    },
    {
        "arquivo": "unidadeerrada.m4a",
        "referencia": "ajusta frequência para 120 mmHg",
        "sem_prompt": "A justa frequência para 120 mmHG",
        "com_prompt": "ajusta frequência para 120 mmHg",
    },
]

print(f"{'Arquivo':<20} {'WER sem prompt':>15} {'WER com prompt':>15} {'Melhora':>10}")
print("-" * 65)

total_sem = []
total_com = []

for a in amostras:
    wer_sem = calcular_wer(a["referencia"], a["sem_prompt"])
    wer_com = calcular_wer(a["referencia"], a["com_prompt"])
    melhora = wer_sem - wer_com

    total_sem.append(wer_sem)
    total_com.append(wer_com)

    print(f"{a['arquivo']:<20} {wer_sem*100:>14.1f}% {wer_com*100:>14.1f}% {melhora*100:>+9.1f}%")

media_sem = sum(total_sem) / len(total_sem)
media_com = sum(total_com) / len(total_com)

print("-" * 65)
print(f"{'MÉDIA GERAL':<20} {media_sem*100:>14.1f}% {media_com*100:>14.1f}% {(media_sem-media_com)*100:>+9.1f}%")
print(f"\nWER médio sem initial_prompt: {media_sem*100:.1f}%")
print(f"WER médio com initial_prompt: {media_com*100:.1f}%")
print(f"Redução de WER com initial_prompt: {(media_sem-media_com)*100:.1f} pontos percentuais")