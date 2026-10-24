from flask import Blueprint, jsonify, request
from database import mysql

maestros_bd = Blueprint(
    "maestros",
    __name__,
    url_prefix="/api/maestros"
)


def fila_a_diccionario(cursor, fila):
    columnas = [columna[0] for columna in cursor.description]
    return dict(zip(columnas, fila))


def obtener_columnas_bd(cursor):
    cursor.execute("SELECT * FROM maestros LIMIT 0")
    return [f"`{columna[0]}`" for columna in cursor.description]


@maestros_bd.route("", methods=["GET"])
@maestros_bd.route("/", methods=["GET"])
def lista_maestros():
    cursor = None
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM maestros")
        datos = cursor.fetchall()
        maestros = [fila_a_diccionario(cursor, fila) for fila in datos]
        return jsonify({
            "maestros": maestros,
            "mensaje": "Lista de maestros",
            "exito": True
        }), 200
    except Exception as ex:
        return jsonify({"mensaje": str(ex), "exito": False}), 500
    finally:
        if cursor is not None:
            cursor.close()


@maestros_bd.route("/<string:id_maestro>", methods=["GET"])
def leer_maestro(id_maestro):
    cursor = None
    try:
        cursor = mysql.connection.cursor()
        columnas = obtener_columnas_bd(cursor)
        cursor.execute(
            f"SELECT * FROM maestros WHERE {columnas[0]} = %s",
            (id_maestro,)
        )
        fila = cursor.fetchone()
        if fila is None:
            return jsonify({
                "mensaje": "Maestro no encontrado",
                "exito": False
            }), 404

        maestro = fila_a_diccionario(cursor, fila)
        return jsonify({"maestro": maestro, "exito": True}), 200
    except Exception as ex:
        return jsonify({
            "mensaje": f"Error al consultar el maestro: {ex}",
            "exito": False
        }), 500
    finally:
        if cursor is not None:
            cursor.close()