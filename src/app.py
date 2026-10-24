from flask import Flask, jsonify, request
from flask_mysqldb import MySQL 
from flask_cors import CORS

from config import config
app=Flask (__name__)
CORS(app)
con=MySQL(app)

def fila_a_diccionario(curso, fila):
    columna=[columna[0] for columna in cursor.description]
    return dict(zip(columnas, fila))

@app.route("/alumnos", methods=['GET'])
def lista_alumnos():
    try:
        cursor=con.connection.cursor()
        sql="select * from alumnos"
        cursor.execute(sql)
        datos=cursor.fetchall()
        alumnos=[]
        for fila in datos:
            alumno={"matricula":fila[0], "nombre":fila[1], "apaterno":fila[2], "amaterno":fila[3], "correo":fila[4]}
            
            alumnos.append(alumno)
        return jsonify({'alumnos':alumnos,'mensaje':"lista de alumnos", 'exito':True})
    except Exception as ex:
        return jsonify({'mensaje': "Error", 'exito': False})

def pagina_no_encontrada(error):
    return"<h1>pagina no encontrada</h1>"

if __name__=="__main__":
    app.config.from_object(config['development'])
    app.register_error_handler(404,pagina_no_encontrada)
    app.run(host='0.0.0.0',port=5000)

def lista_alumnos():
        try:

            except Exeception as ex:
                return jsonify({"messaje": "error {}".format(ex),
                'exito': false})   
@app.route("/alumnos/<string:matricula", methods=['GET']):
def leer_alumno_bd(matricula):
    curso=con.connection.curso()
    sql=("""SELECT * FROM alumnos WHERE matricula=%s""",(matricula,))
    fila=cursor.fetchone()
    if fila is None:
        return jsonif({
            'mesaje': 'alumno no encontrado',
            'exito':True
        }),404
        alumno=fila_a_diccionario(cursor, fila)
        return jsonify ({
            'alumno':alumno,
            'exito':True
        }),200
        except Exception as ex:
            return jsonify({
                'alumno':"errer al consulta",
                'exito':False
            })500
            finally
            if cursor is not None:
                cursor.close()

