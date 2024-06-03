from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

app = Flask(__name__)

#CONFIGURACION DE LA BASE DE DATOS SQLLITE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///metapython.db'
app.config['SQLALCHEMY_TRACK_NOTIFICATIONS'] = False
db = SQLAlchemy(app)

#MODELO DE LA TABLA LOG
class Log(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    fecha_y_hora = db.Column(db.DateTime, default = datetime.now())
    texto = db.Column(db.TEXT)

#CREAR LA TABLA SI NO EXISTE
with app.app_context():
    db.create_all()

    prueba1 = Log(texto = 'Mensaje de Prueba 1')
    prueba2 = Log(texto = 'Mensaje de Prueba 2')

    db.session.add(prueba1)
    db.session.add(prueba2)
    db.session.commit()


#FUNCION PARA ORDENAR LOS REGISTROS POR FECHA Y HORA
def ordenar_por_fecha_y_hora(registros):
    return sorted(registros, key=lambda x: x.fecha_y_hora, reverse=True)


@app.route('/')
def index():
    #OBTENER TODOS LOS REGISTROS DE LA BASE DE DATOS
    registros = Log.query.all()
    registros_ordenados = ordenar_por_fecha_y_hora(registros)
    return render_template('index.html', registros = registros_ordenados)

mensajes_log = []

#FUNCION PARA AGREGAR MENSAJES Y GUARDAR EN LA BASE DE DATOS
def agregar_mensajes_log(texto):
    mensajes_log.append(texto)

    #GUARDAR EL MENSAJE EN LA BASE DE DATOS
    nuevo_registro = Log(texto = texto)
    db.session.add(nuevo_registro)
    db.session.commit()


if __name__=='__main__':
    app.run(host='0.0.0.0',port=80,debug=True)