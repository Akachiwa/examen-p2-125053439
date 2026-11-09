#!/usr/bin/env python3
# =====================================================================
#  MAPPER - Pregunta 8/9: Ingreso total por HORA DEL DIA y CATEGORIA
#  Matricula 125053439 (ultimo digito 9)
#
#  Entrada (una linea del CSV):
#    1,2025-03-14 17:22:05,T004,Ropa,ROP-0012,3,150.25,Tarjeta
#  Salida (clave <TAB> valor):
#    17|Ropa<TAB>45075        <- ingreso en CENTAVOS (3 x 15025)
# =====================================================================
import sys


def main():
    for linea in sys.stdin:
        # strip() quita espacios y el salto de linea (\r\n o \n)
        campos = linea.strip().split(",")

        # 1) Linea mal formada: debe tener exactamente 8 columnas
        if len(campos) != 8:
            sys.stderr.write("reporter:counter:DataMart,LineasMalFormadas,1\n")
            continue

        # 2) Ignorar el encabezado
        if campos[0] == "id":
            continue

        try:
            fecha_hora = campos[1]            # "2025-03-14 17:22:05"
            hora = int(fecha_hora[11:13])     # caracteres 11 y 12 -> 17
            categoria = campos[3]
            cantidad = int(campos[5])
            # En centavos (enteros) para que la suma sea exacta
            precio_centavos = round(float(campos[6]) * 100)

            if not (0 <= hora <= 23) or categoria == "":
                raise ValueError("hora o categoria invalida")
        except (ValueError, IndexError):
            # Dato raro: se cuenta y se brinca, el job NO se cae
            sys.stderr.write("reporter:counter:DataMart,LineasMalFormadas,1\n")
            continue

        ingreso_centavos = cantidad * precio_centavos

        # Clave "HH|Categoria". Hora con 2 digitos para que ordene bien
        print(f"{hora:02d}|{categoria}\t{ingreso_centavos}")


if __name__ == "__main__":
    main()