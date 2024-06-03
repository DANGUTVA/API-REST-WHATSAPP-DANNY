from flask import Flask, request, jsonify, render_template
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

#TOKEN DE VERIFICACION PARA LA CONFIGURACION
TOKEN_APIMETA = "DANGUTVA"

@app.route('/webhook', methods=['GET','POST'])
def webhook():
    if request.method == 'GET':
        challenge = verificar_token(request)
        return challenge
    elif request.method == 'POST':
        response = recibir_mensajes(request)
        return response

def verificar_token(req):
    token = req.args.get('hub.verify_token')
    challenge = req.args.get('hub.challenge')

    if challenge and token == TOKEN_APIMETA:
        return challenge
    else:
        return jsonify({'error':'Token Invalido'}),401

def recibir_mensajes(req):
    req = request.get_json()
    agregar_mensajes_log(req)

    return jsonify({'message':'EVENT_RECEIVED'})

if __name__=='__main__':
    app.run(host='0.0.0.0',port=800,debug=True)