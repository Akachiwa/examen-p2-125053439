# =====================================================================
#  API REST (CRUD) con Flask sobre la tabla de resultados del job
#  Tabla: ingreso_hora_categoria (hora, categoria, ingreso_total)
# =====================================================================
import os
import time

import psycopg2
import psycopg2.extras
from flask import Flask, jsonify, request

app = Flask(__name__)


# Conexion a PostgreSQL. Los datos salen del archivo .env.
# DB_HOST=db -> "db" es el NOMBRE DEL SERVICIO en docker-compose.
def conectar():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )


SQL_CREAR_TABLA = """
CREATE TABLE IF NOT EXISTS ingreso_hora_categoria (
    id            SERIAL PRIMARY KEY,
    hora          SMALLINT      NOT NULL CHECK (hora BETWEEN 0 AND 23),
    categoria     VARCHAR(50)   NOT NULL,
    ingreso_total NUMERIC(16,2) NOT NULL,
    UNIQUE (hora, categoria)
);
"""


def crear_tabla():
    # Reintentos por si la base todavia esta arrancando
    for intento in range(1, 11):
        try:
            with conectar() as conn, conn.cursor() as cur:
                cur.execute(SQL_CREAR_TABLA)
            print("[api] Tabla lista", flush=True)
            return
        except psycopg2.OperationalError as e:
            print(f"[api] BD no disponible (intento {intento}): {e}", flush=True)
            time.sleep(3)
    raise RuntimeError("No se pudo conectar a la base de datos")


def fila_a_dict(fila):
    return {
        "id": fila["id"],
        "hora": fila["hora"],
        "categoria": fila["categoria"],
        "ingreso_total": float(fila["ingreso_total"]),
    }


def consultar(sql, params=()):
    with conectar() as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql, params)
        return [fila_a_dict(f) for f in cur.fetchall()]


@app.get("/")
def inicio():
    return jsonify({
        "api": "DataMart - Ingreso total por hora del dia y categoria",
        "matricula": os.getenv("MATRICULA", ""),
        "endpoints": [
            "GET    /resultados",
            "GET    /resultados/<clave>   (clave = hora 0-23 o categoria)",
            "POST   /resultados",
            "PUT    /resultados/<id>",
            "DELETE /resultados/<id>",
        ],
    })


# GET /resultados -> todos
@app.get("/resultados")
def listar():
    filas = consultar("SELECT * FROM ingreso_hora_categoria ORDER BY hora, categoria")
    return jsonify({"total_registros": len(filas), "resultados": filas})


# GET /resultados/<clave> -> numero = hora, texto = categoria
@app.get("/resultados/<clave>")
def filtrar(clave):
    if clave.isdigit():
        filas = consultar(
            "SELECT * FROM ingreso_hora_categoria WHERE hora = %s ORDER BY categoria",
            (int(clave),))
    else:
        filas = consultar(
            "SELECT * FROM ingreso_hora_categoria WHERE LOWER(categoria) = LOWER(%s) ORDER BY hora",
            (clave,))
    if not filas:
        return jsonify({"error": f"No hay resultados para '{clave}'"}), 404
    return jsonify({"clave": clave, "total_registros": len(filas), "resultados": filas})


# POST /resultados -> crear
@app.post("/resultados")
def crear():
    d = request.get_json(silent=True) or {}
    if not all(k in d for k in ("hora", "categoria", "ingreso_total")):
        return jsonify({"error": "Faltan campos: hora, categoria, ingreso_total"}), 400
    try:
        with conectar() as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """INSERT INTO ingreso_hora_categoria (hora, categoria, ingreso_total)
                   VALUES (%s, %s, %s) RETURNING *""",
                (d["hora"], d["categoria"], d["ingreso_total"]))
            return jsonify(fila_a_dict(cur.fetchone())), 201
    except psycopg2.errors.UniqueViolation:
        return jsonify({"error": "Ya existe esa combinacion hora/categoria"}), 409
    except psycopg2.Error as e:
        return jsonify({"error": str(e).strip()}), 400


# PUT /resultados/<id> -> actualizar
@app.put("/resultados/<int:id_>")
def actualizar(id_):
    d = request.get_json(silent=True) or {}
    campos = [c for c in ("hora", "categoria", "ingreso_total") if c in d]
    if not campos:
        return jsonify({"error": "Envia al menos un campo para actualizar"}), 400
    set_sql = ", ".join(f"{c} = %s" for c in campos)
    valores = [d[c] for c in campos] + [id_]
    try:
        with conectar() as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                f"UPDATE ingreso_hora_categoria SET {set_sql} WHERE id = %s RETURNING *",
                valores)
            fila = cur.fetchone()
    except psycopg2.Error as e:
        return jsonify({"error": str(e).strip()}), 400
    if fila is None:
        return jsonify({"error": "No existe ese id"}), 404
    return jsonify(fila_a_dict(fila))


# DELETE /resultados/<id> -> borrar
@app.delete("/resultados/<int:id_>")
def borrar(id_):
    with conectar() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM ingreso_hora_categoria WHERE id = %s", (id_,))
        borrados = cur.rowcount
    if borrados == 0:
        return jsonify({"error": "No existe ese id"}), 404
    return jsonify({"mensaje": f"Registro {id_} eliminado"})


if __name__ == "__main__":
    crear_tabla()
    # 0.0.0.0 = escuchar en todas las interfaces (necesario en Docker)
    app.run(host="0.0.0.0", port=5000)