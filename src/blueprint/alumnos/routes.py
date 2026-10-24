from flask import Blueprint, jsonify, request
from database import mysql 


alumnos_bd=Blueprint(
    'alumnos', __name__,
    url_prefix='/api/alumnos'
)

def fila_a_diccionario(cursor, fila):
    columnas = [columna[0] for columna in cursor.description]
    return dict(zip(columnas, fila))


def obtener_columnas_bd(cursor):
    cursor.execute("SELECT * FROM alumnos LIMIT 0")
    # Envolvemos cada nombre de columna en backticks (`) por si contienen espacios
    return [f"`{columna[0]}`" for columna in cursor.description]


@alumnos_bd .route("/alumnos", methods=["GET"])
def lista_alumnos():
    cursor = None
    try:
        cursor = mysql.connection.cursor()
        sql = "SELECT * FROM alumnos"
        cursor.execute(sql)
        datos = cursor.fetchall()
        alumnos = []
        for fila in datos:
            alumno = {
                "matricula": fila[0],
                "nombre": fila[1],
                "apaterno": fila[2],
                "amaterno": fila[3],
                "correo": fila[4],
            }
            alumnos.append(alumno)
        return (
            jsonify(
                {
                    "alumnos": alumnos,
                    "mensaje": "Lista de alumnos",
                    "exito": True,
                }
            ),
            200,
        )

    except Exception as ex:
        print("ERROR DE MYSQL:", ex)
        return jsonify({"mensaje": str(ex), "exito": False}), 500

    finally:
        if cursor is not None:
            cursor.close()


@alumnos_bd .route("/<string:matricula>", methods=["GET"])
def leer_alumno(matricula):
    cursor = None
    try:
        cursor = mysql.connection.cursor()
        columnas = obtener_columnas_bd(cursor)
        cursor.execute(
            f"SELECT * FROM alumnos WHERE {columnas[0]} = %s", (matricula,)
        )
        fila = cursor.fetchone()
        if fila is None:
            return (
                jsonify({"mensaje": "Alumno no encontrado", "exito": False}),
                404,
            )

        alumno = fila_a_diccionario(cursor, fila)
        return jsonify({"alumno": alumno, "exito": True}), 200

    except Exception as ex:
        return (
            jsonify(
                {
                    "mensaje": f"Error al consultar el alumno: {ex}",
                    "exito": False,
                }
            ),
            500,
        )

    finally:
        if cursor is not None:
            cursor.close()


@alumnos_bd.route("/alumnos", methods=["POST"])
def registrar_alumno():
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        return (
            jsonify(
                {"mensaje": "Se requiere un objeto JSON", "exito": False}
            ),
            400,
        )

    campos = ["matricula", "nombre", "apaterno", "amaterno", "correo"]

    if any(
        campo not in datos
        or not isinstance(datos[campo], str)
        or not datos[campo].strip()
        for campo in campos
    ):
        return (
            jsonify(
                {"mensaje": "Faltan campos obligatorios", "exito": False}
            ),
            400,
        )

    cursor = None
    try:
        cursor = mysql.connection.cursor()
        columnas = obtener_columnas_bd(cursor)

        cursor.execute(
            f"SELECT {columnas[0]} FROM alumnos WHERE {columnas[0]} = %s",
            (datos["matricula"].strip(),),
        )
        if cursor.fetchone() is not None:
            return (
                jsonify({"mensaje": "La matrícula ya existe", "exito": False}),
                409,
            )

        sql = f"""
            INSERT INTO alumnos ({columnas[0]}, {columnas[1]}, {columnas[2]}, {columnas[3]}, {columnas[4]})
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(
            sql,
            tuple(datos[campo].strip() for campo in campos),
        )

        mysql.connection.commit()
        return (
            jsonify(
                {
                    "mensaje": "Alumno registrado correctamente",
                    "exito": True,
                }
            ),
            201,
        )

    except Exception as ex:
        mysql.connection.rollback()
        return (
            jsonify(
                {
                    "mensaje": f"Error al registrar el alumno: {ex}",
                    "exito": False,
                }
            ),
            500,
        )

    finally:
        if cursor is not None:
            cursor.close()


@alumnos_bd.route("/alumnos/<string:matricula>", methods=["PUT"])
def modificar_alumno(matricula):
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        return (
            jsonify(
                {"mensaje": "Se requiere un objeto JSON", "exito": False}
            ),
            400,
        )

    campos_actualizables = ["nombre", "apaterno", "amaterno", "correo"]

    if any(
        campo not in datos
        or not isinstance(datos[campo], str)
        or not datos[campo].strip()
        for campo in campos_actualizables
    ):
        return (
            jsonify(
                {
                    "mensaje": "Faltan datos obligatorios para la actualización",
                    "exito": False,
                }
            ),
            400,
        )

    cursor = None
    try:
        cursor = mysql.connection.cursor()
        columnas = obtener_columnas_bd(cursor)

        cursor.execute(
            f"SELECT {columnas[0]} FROM alumnos WHERE {columnas[0]} = %s",
            (matricula,),
        )
        if cursor.fetchone() is None:
            return (
                jsonify(
                    {
                        "mensaje": "No existe un alumno con esa matrícula",
                        "exito": False,
                    }
                ),
                404,
            )

        sql = f"""
            UPDATE alumnos
            SET {columnas[1]} = %s,
                {columnas[2]} = %s,
                {columnas[3]} = %s,
                {columnas[4]} = %s
            WHERE {columnas[0]} = %s
        """
        cursor.execute(
            sql,
            (
                datos["nombre"].strip(),
                datos["apaterno"].strip(),
                datos["amaterno"].strip(),
                datos["correo"].strip(),
                matricula,
            ),
        )
        mysql.connection.commit()

        return (
            jsonify(
                {
                    "mensaje": "Alumno modificado correctamente",
                    "matricula": matricula,
                    "exito": True,
                }
            ),
            200,
        )

    except Exception as ex:
        mysql.connection.rollback()
        return (
            jsonify(
                {
                    "mensaje": f"Error al modificar el alumno: {ex}",
                    "exito": False,
                }
            ),
            500,
        )

    finally:
        if cursor is not None:
            cursor.close()


@alumnos_bd.route("/alumnos/<string:matricula>", methods=["DELETE"])
def eliminar_alumno(matricula):
    cursor = None
    try:
        cursor = mysql.connection.cursor()
        columnas = obtener_columnas_bd(cursor)

        cursor.execute(
            f"SELECT {columnas[0]} FROM alumnos WHERE {columnas[0]} = %s",
            (matricula,),
        )
        if cursor.fetchone() is None:
            return (
                jsonify(
                    {
                        "mensaje": "No existe un alumno con esa matrícula",
                        "exito": False,
                    }
                ),
                404,
            )

        cursor.execute(
            f"DELETE FROM alumnos WHERE {columnas[0]} = %s",
            (matricula,),
        )
        mysql.connection.commit()

        return (
            jsonify(
                {
                    "mensaje": "Alumno eliminado correctamente",
                    "matricula": matricula,
                    "exito": True,
                }
            ),
            200,
        )

    except Exception as ex:
        mysql.connection.rollback()
        return (
            jsonify(
                {
                    "mensaje": f"Error al eliminar el alumno: {ex}",
                    "exito": False,
                }
            ),
            500,
        )

    finally:
        if cursor is not None:
            cursor.close()
