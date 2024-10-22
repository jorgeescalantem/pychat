from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import http.client
import json
from pydantic import BaseModel, PositiveInt
import requests
import os
import datetime
import pytz

app = Flask(__name__)


#CONFIGURACION de la base de datos SQL lite
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///metapython.db"
app.config['SQLLCHEMY_TRACK_MODIFICATIONS'] = False
db=SQLAlchemy(app)

# Modelo de la tabla LOG 
class log(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    fecha_y_hora=db.Column(db.DateTime,default=datetime.datetime.now(tz=pytz.utc))
    texto=db.Column(db.TEXT)

# crear tabla si no exixte
with app.app_context():
    db.create_all()

#funcion para ordenar los registros por fecha y hora
def order_por_fecha_y_hora(registros):
    return sorted(registros,key=lambda x: x.fecha_y_hora,reverse=True)    

@app.route('/')
def index():
    #obtener todos los registros de la DB
    registros= log.query.all()
    registros_ordenados=order_por_fecha_y_hora(registros)
    return render_template('index.html',registros=registros_ordenados)

mensajes_log=[]
# funcion para agregar mensajes a la base de datos
def agregra_mensajes_log(texto):
    mensajes_log.append(texto)
    #guardar mensajes en la base de datos
    nuevo_registro = log(texto=texto)
    db.session.add(nuevo_registro)
    db.session.commit()

# conectar comn meta
TOKEN_TEMP= 'TOKENTEMPO'
@app.route('/webhook',methods=['GET','POST'])
def webhook():
    if request.method=='GET':
        challenge=verificar_token(request)
        return challenge
    elif request.method=='POST':
        response = recibir_mensajes(request)
        return response
def verificar_token(req):
    token = req.args.get('hub.verify_token')
    challenge= req.args.get('hub.challenge')

    if challenge and token == TOKEN_TEMP:
        return challenge
    else:
        return jsonify({"error":"token invalido"}),401       
            
def recibir_mensajes(req):  
    try:
        req = request.get_json()
        entry = req['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        objeto_mensaje=value['messages']
        #objeto_para=value['metadata']

        if objeto_mensaje:
           # para=objeto_para[0]
            messages=objeto_mensaje[0]
            if "type" in messages:
                tipo= messages["type"]
                #Guardar Log en la BD
                agregra_mensajes_log(json.dumps(req))
                #agregra_mensajes_log(jsonify(messages))

                if tipo == "interactive":
                    tipo_interactivo = messages["interactive"]["type"]
                    if tipo_interactivo == "button_reply":
                        text = messages["interactive"]["button_reply"]["id"]
                        numero = messages["from"]
                    #return 1
                    
                if "text" in messages:
                    text = messages["text"]["body"]
                    numero= messages["from"]                    #chat= para["phone_number_id"]

                    #agregra_mensajes_log(jsonify(text))
                    #agregra_mensajes_log(jsonify(numero))
                    #agregra_mensajes_log(jsonify(req))
                    agregra_mensajes_log(json.dumps(text))
                    agregra_mensajes_log(json.dumps(numero))
                    agregra_mensajes_log(json.dumps(req))
                    #agregra_mensajes_log(json.dumps(objeto_para))

        return jsonify({'message':'EVENT_RECEIVED'})

    except Exception as e:    
        return jsonify({'message':'EVENT_RECEIVED'})
# enviar mensaje de plantilla para envio con boton number,code,reason

@app.route("/send/<number>",methods=["POST", "GET"] )
def enviar_mensajes_whatsapp(number):
    try:

        #textp = request.json.get('text')
        textp = request.json['text']
        if not textp:
            return jsonify({'message': "Text is required"}), 400

        data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": number,
                "type": "interactive",
                "interactive":{
                    "type":"button",
                    "body": {
                        "text": textp
                    },
                    "footer": {
                        "text": "Desea confirmar el servicio"
                    },
                    "action": {
                        "buttons":[
                            {
                                "type": "reply",
                                "reply":{
                                    "id":"btnconfirmar",
                                    "title":"Confirmar"
                                }
                            },{
                                "type": "reply",
                                "reply":{
                                    "id":"btncancelar",
                                    "title":"Cancelar"
                                }
                            }
                        ]
                    }
                }
            }

        TOKEN_P=os.getenv('TOKEN_API')
        if not TOKEN_P:
                return jsonify({'message': "Token is missing"}), 500
   
        data=json.dumps(data)
        headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {TOKEN_P}"
            }
        url = "https://graph.facebook.com/v20.0/117168924654185/messages"

    
        response = requests.request("POST", url, headers=headers, data=data)
        st=response.status_code        
        if st == 200:
            data= response.json()
            # respuesta datos de contacto
            contacts = data.get("contacts", [{}])[0]
            wa_id = contacts.get("wa_id", "")
            imputs = contacts.get("input", "")
            # respuesta id de whatsapp
            messages = data.get("messages", [{}])[0]
            id = messages.get("id", "")

            send=[
                {'message':"enviado","estado":st,"idWA":id,"imput":imputs,"contacto":wa_id}
            ]
            mensaje_enviado(json.dumps(send))
            return jsonify(send)
            #mensaje_enviado(data)       
            #return jsonify({'message':"enviado","estado":st,"idWA":id,"imput":imputs,"contacto":wa_id})
        elif st == 401:
            return jsonify({'message': "Unauthorized, invalid token"}), 401
        else:
            return jsonify({'message': "Failed to send message", "estado": st}), st
        #agregar_mensajes_log(json.dumps(text))
    except Exception as e:
        #agregar_mensajes_log(json.dumps(e))
        return jsonify({'message': f"Error: {str(e)}"}), 500
    finally:
        if 'response' in locals():
            response.close()
##

def mensaje_enviado(send):
    import mysql.connector
    from mysql.connector import Error

    try:
        # Conectar a la base de datos MySQL
        mydb = mysql.connector.connect(
            host="pychat.informaticaf5.com",
            user="tecJa7_TecJa7",
            password="Dlvb47&45",
            database='tecJa7_pychat'
        )

        if mydb.is_connected():
            cursor = mydb.cursor()

            # Parsear el JSON de send
            send_data = json.loads(send)[0]
            message = send_data['message']
            estado = send_data['estado']
            idWA = send_data['idWA']
            imput = send_data['imput']
            contacto = send_data['contacto']

            utc_now = datetime.datetime.utcnow()
            bogota_timezone = pytz.timezone('America/Bogota')
            fecha_hora = utc_now.replace(tzinfo=pytz.utc).astimezone(bogota_timezone)
            # Insertar los datos en la tabla mensajes_enviados
            sql_insert_query = """INSERT INTO mensajes_enviados (message, estado, idWA, imput, contacto, fecha_hora)
                                  VALUES (%s, %s, %s, %s, %s, %s)"""
            insert_tuple = (message, estado, idWA, imput, contacto, fecha_hora)
            cursor.execute(sql_insert_query, insert_tuple)
            mydb.commit()

            print("Registro insertado exitosamente en la tabla mensajes_enviados")

    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
    finally:
        if mydb.is_connected():
            cursor.close()
            mydb.close()
            print("Conexión a MySQL cerrada")

    agregar_mensajes_log(json.dumps(send))
    msg = send_data['message']
    print(msg)

    return "guardado"



if __name__=='__main__':
    app.run(host='0.0.0.0',port=80,debug=True)
