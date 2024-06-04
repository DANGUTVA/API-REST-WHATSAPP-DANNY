from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import http.client
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
    try:
        req = request.get_json()
        entry =req['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        objeto_mensaje = value['messages']

        if objeto_mensaje:
            messages = objeto_mensaje[0]

            if "type" in messages:
                tipo = messages["type"]

            if tipo =="interactive":
                return 0
            
            if "text" in messages:
                text = messages["text"]["body"]
                numero = messages["from"]

                enviar_mensajes_whatsapp(text, numero)
                #enviar_mensajes_whatsapp(json.dumps(text, numero))

        return jsonify({'message':'EVENT_RECEIVED'})
    except Exception as e:
        return jsonify({'message':'EVENT_RECEIVED'})
    
def enviar_mensajes_whatsapp(texto, number):
    texto = texto.lower()

    if "hola" in texto:
        data = {
             "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "🚀 Hola, ¿Cómo estás? Bienvenido."
            }
        }
    else:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum."
            }
        }

    #CONVERTIR EL DICCIONARIO A FORMATO JSON
    data = json.dumps(data)

    headers = {
        "Content-Type" : "application/json",
        "Authorization" : "Bearer EAAOEH3xitTkBO2Yk62TMtmZBzJpXi6bUZBMOaLzHSg7UvBFccadkQeir0G7MGKhZA2H2HizcaZB1Rk73RjkHXkrkG5XtycSUcNZCyBCloTIZCOynyY03ynzS9jjBAWgdLYovY3YYS5xgaX78zYhNxktkPh7go4ZAyTjS2RQAJ43MyO3CJ9L8YgfZCvZAGFbFtm3w2iZA4kuGqTGqZCMMt0OpwZDZD"
    }

    connection = http.client.HTTPSConnection("graph.facebook.com")

    try:
        connection.request("POST", "/v19.0/331842380014779/messages", data, headers)
        response = connection.getresponse()
        print(response.status, response.reason)
    except Exception as e:
        agregar_mensajes_log(json.dumps(e))
    finally: 
        connection.close()

if __name__=='__main__':
    app.run(host='0.0.0.0',port=80,debug=True)