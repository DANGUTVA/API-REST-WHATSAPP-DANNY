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

                #Guardar Log en la BD
                agregar_mensajes_log(json.dumps(messages))

                if tipo == "interactive":
                    tipo_interactivo = messages["interactive"]["type"]

                    if tipo_interactivo == "button_reply":
                        text = messages["interactive"]["button_reply"]["id"]
                        numero = messages["from"]

                        enviar_mensajes_whatsapp(text,numero)
                    
                    elif tipo_interactivo == "list_reply":
                        text = messages["interactive"]["list_reply"]["id"]
                        numero = messages["from"]

                        enviar_mensajes_whatsapp(text,numero)

                if "text" in messages:
                    text = messages["text"]["body"]
                    numero = messages["from"]

                    enviar_mensajes_whatsapp(text,numero)

                    #Guardar Log en la BD
                    agregar_mensajes_log(json.dumps(messages))

        return jsonify({'message':'EVENT_RECEIVED'})
    except Exception as e:
        return jsonify({'message':'EVENT_RECEIVED'})
    
def enviar_mensajes_whatsapp(texto, number):
    texto = texto.lower()

    # Menú con mensaje inicial de bienvenida y con las demás opciones
    if "hola" or "Buenas" or "buenas" or "1" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": (
                    "🚀 Hola, ¿Cómo estás? Bienvenido.\n\n"
                    "Por favor, ingresa un número #️⃣ para recibir información:\n\n"
                    "1️⃣. Ver Menú de Opciones\n"
                    "2️⃣. Ubicación del local. 📍\n"
                    "3️⃣. Enviar temario en PDF. 📄\n"
                    "4️⃣. Audio explicando curso. 🎧\n"
                    "5️⃣. Video de Introducción. ⏯️\n"
                    "6️⃣. Hablar con Mil Razones. 🙋‍♂️\n"
                    "7️⃣. Horario de Atención. 🕜\n"
                    "0️⃣. Regresar al Menú. 🕜"
                )
            }
        }
    # Ubicación del local
    elif "2" in texto:
        data = {
            "messaging_product": "whatsapp",
            "to": number,
            "type": "location",
            "location": {
                "latitude": "-12.067158831865067",
                "longitude": "-77.03377940839486",
                "name": "Estadio Nacional del Perú",
                "address": "Cercado de Lima"
            }
        }
    # Enviar temario en PDF
    elif "3" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "document",
            "document": {
                "link": "https://www.turnerlibros.com/wp-content/uploads/2021/02/ejemplo.pdf",
                "caption": "Temario del Curso #001"
            }
        }
    # Audio explicando curso
    elif "4" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "audio",
            "audio": {
                "link": "https://filesamples.com/samples/audio/mp3/sample1.mp3"
            }
        }
    # Video de Introducción
    elif "5" in texto:
        data = {
            "messaging_product": "whatsapp",
            "to": number,
            "text": {
                "preview_url": True,
                "body": "Introduccion al curso! https://youtu.be/6ULOE2tGlBM"
            }
        }
    # Hablar con AnderCode
    elif "6" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "🤝 En breve me pondre en contacto contigo. 🤓"
            }
        }
    # Horario de Atención
    elif "7" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "📅 Horario de Atención : Lunes a Viernes. \n🕜 Horario : 9:00 am a 5:00 pm 🤓"
            }
        }
    # Regresar al Menú
    elif "0" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": (
                    "🚀 Hola, visita mi web milrazonescr.com para más información.\n\n"
                    "📌Por favor, ingresa un número #️⃣ para recibir información:\n\n"
                    "1️⃣. Ver Menú de Opciones\n"
                    "2️⃣. Ubicación del local. 📍\n"
                    "3️⃣. Enviar temario en PDF. 📄\n"
                    "4️⃣. Audio explicando curso. 🎧\n"
                    "5️⃣. Video de Introducción. ⏯️\n"
                    "6️⃣. Hablar con Mil Razones. 🙋‍♂️\n"
                    "7️⃣. Horario de Atención. 🕜\n"
                    "0️⃣. Regresar al Menú. 🕜"
                )
            }
        }
    # Confirmación con Botones
    elif "boton" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": "¿Confirmas tu registro?"
                },
                "footer": {
                    "text": "Selecciona una de las opciones"
                },
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {
                                "id": "btnsi",
                                "title": "Si"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "btnno",
                                "title": "No"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "btntalvez",
                                "title": "Tal Vez"
                            }
                        }
                    ]
                }
            }
        }
    # Respuestas a los botones
    elif "btnsi" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Muchas Gracias por Aceptar."
            }
        }
    elif "btnno" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Es una Lastima."
            }
        }
    elif "btntalvez" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Estare a la espera."
            }
        }
    # Lista de opciones
    elif "lista" in texto:
        data = {
            "messaging_product": "whatsapp",
            "to": number,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {
                    "text": "Selecciona Alguna Opción"
                },
                "footer": {
                    "text": "Selecciona una de las opciones para poder ayudarte"
                },
                "action": {
                    "button": "Ver Opciones",
                    "sections": [
                        {
                            "title": "Compra y Venta",
                            "rows": [
                                {
                                    "id": "btncompra",
                                    "title": "Comprar",
                                    "description": "Compra los mejores articulos de tecnologia"
                                },
                                {
                                    "id": "btnvender",
                                    "title": "Vender",
                                    "description": "Vende lo que ya no estes usando"
                                }
                            ]
                        },
                        {
                            "title": "Distribución y Entrega",
                            "rows": [
                                {
                                    "id": "btndireccion",
                                    "title": "Local",
                                    "description": "Puedes visitar nuestro local."
                                },
                                {
                                    "id": "btnentrega",
                                    "title": "Entrega",
                                    "description": "La entrega se realiza todos los dias."
                                }
                            ]
                        }
                    ]
                }
            }
        }
    # Respuestas a la lista
    elif "btncompra" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Los mejores artículos top en ofertas."
            }
        }
    elif "btnvender" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Excelente elección."
            }
        }
    # Respuesta por defecto
    else:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": (
                    "🚀 Hola, visita mi web milrazonescr.com para más información.\n\n"
                    "📌Por favor, ingresa un número #️⃣ para recibir información:\n\n"
                    "1️⃣. Ver Menú de Opciones\n"
                    "2️⃣. Ubicación del local. 📍\n"
                    "3️⃣. Enviar temario en PDF. 📄\n"
                    "4️⃣. Audio explicando curso. 🎧\n"
                    "5️⃣. Video de Introducción. ⏯️\n"
                    "6️⃣. Hablar con Mil Razones. 🙋‍♂️\n"
                    "7️⃣. Horario de Atención. 🕜\n"
                    "0️⃣. Regresar al Menú. 🕜"
                )
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