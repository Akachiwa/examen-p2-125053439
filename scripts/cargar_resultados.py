# =====================================================================
#  Lee la salida del job (part-00000) y la inserta en PostgreSQL.
#  Uso (dentro del contenedor api):
#    python scripts/cargar_resultados.py
#  Si se corre dos veces NO duplica (ON CONFLICT ... DO UPDATE).
# =====================================================================
import os
import sys

import psycopg2

ARCHIVO = sys.argv[1] if len(sys.argv) > 1 else "/data/output/resultado/part-00000"

SQL_CREAR_TABLA = """
CREATE TABLE IF NOT EXISTS ingreso_hora_categoria (
    id            SERIAL PRIMARY KEY,
    hora          SMALLINT      NOT NULL CHECK (hora BETWEEN 0 AND 23),
    categoria     VARCHAR(50)   NOT NULL,
    ingreso_total NUMERIC(16,2) NOT NULL,
    UNIQUE (hora, categoria)
);
"""

SQL_INSERTAR = """
INSERT INTO ingreso_hora_categoria (hora, categoria, ingreso_total)
VALUES (%s, %s, %s)
ON CONFLICT (hora, categoria) DO UPDATE SET ingreso_total = EXCLUDED.ingreso_total;
"""


def leer_resultados(ruta):
    registros = []
    with open(ruta, encoding="utf-8") as f:
        for linea in f:
            partes = linea.strip().split("\t")   # hora<TAB>categoria<TAB>total
            if len(partes) != 3:
                continue
            hora, categoria, total = partes
            registros.append((int(hora), categoria, total))
    return registros


def main():
    if not os.path.exists(ARCHIVO):
        sys.exit(f"No existe {ARCHIVO}. ¿Ya corriste el job de Hadoop?")

    registros = leer_resultados(ARCHIVO)
    print(f"Leidos {len(registros)} registros de {ARCHIVO}")

    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )
    with conn, conn.cursor() as cur:        # "with conn" = COMMIT al final
        cur.execute(SQL_CREAR_TABLA)
        cur.executemany(SQL_INSERTAR, registros)
        cur.execute("SELECT COUNT(*) FROM ingreso_hora_categoria")
        print(f"Registros en la tabla: {cur.fetchone()[0]}")
    conn.close()


if __name__ == "__main__":
    main()