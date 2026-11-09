#!/usr/bin/env python3
# =====================================================================
#  VERSION SECUENCIAL (sin Hadoop) de la misma pregunta.
#  Mismo formato de salida que el reducer para comparar con "diff".
#  Uso:
#    time python3 secuencial.py /data/input/ventas_125053439.csv > /data/output/secuencial.txt
# =====================================================================
import sys


def main():
    if len(sys.argv) != 2:
        sys.exit("Uso: python3 secuencial.py <archivo.csv>")

    totales = {}   # (hora, categoria) -> centavos
    malas = 0

    with open(sys.argv[1], encoding="utf-8") as f:
        for linea in f:
            campos = linea.strip().split(",")
            if len(campos) != 8:
                malas += 1
                continue
            if campos[0] == "id":
                continue
            try:
                hora = int(campos[1][11:13])
                categoria = campos[3]
                cantidad = int(campos[5])
                precio_centavos = round(float(campos[6]) * 100)
                if not (0 <= hora <= 23) or categoria == "":
                    raise ValueError
            except (ValueError, IndexError):
                malas += 1
                continue

            clave = (f"{hora:02d}", categoria)
            totales[clave] = totales.get(clave, 0) + cantidad * precio_centavos

    # Mismo orden que Hadoop ("HH|Categoria")
    for (hora, categoria) in sorted(totales, key=lambda k: f"{k[0]}|{k[1]}"):
        c = totales[(hora, categoria)]
        print(f"{hora}\t{categoria}\t{c // 100}.{c % 100:02d}")

    sys.stderr.write(f"Lineas mal formadas: {malas}\n")


if __name__ == "__main__":
    main()