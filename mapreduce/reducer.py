#!/usr/bin/env python3
# =====================================================================
#  REDUCER - Ingreso total por HORA DEL DIA y CATEGORIA
#
#  Hadoop entrega las lineas YA ORDENADAS por clave:
#    00|Abarrotes<TAB>12345
#    00|Abarrotes<TAB>6789
#    00|Bebidas<TAB>4500
#  Sumamos mientras la clave sea igual; cuando cambia, imprimimos.
#
#  Salida:  hora<TAB>categoria<TAB>ingreso_total
# =====================================================================
import sys


def imprimir(clave, total_centavos):
    hora, categoria = clave.split("|", 1)
    # Centavos -> pesos con 2 decimales SIN usar float
    pesos = f"{total_centavos // 100}.{total_centavos % 100:02d}"
    print(f"{hora}\t{categoria}\t{pesos}")


def main():
    clave_actual = None
    total = 0

    for linea in sys.stdin:
        linea = linea.strip()
        if not linea:
            continue
        try:
            clave, valor = linea.split("\t", 1)
            valor = int(valor)
        except ValueError:
            continue

        if clave == clave_actual:
            total += valor                      # misma clave -> sumar
        else:
            if clave_actual is not None:
                imprimir(clave_actual, total)   # cambio de clave -> imprimir
            clave_actual = clave
            total = valor

    # No olvidar la ultima clave
    if clave_actual is not None:
        imprimir(clave_actual, total)


if __name__ == "__main__":
    main()