from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import http.client



app = Flask(__name__)
#CONFIGURACION de la base de datos SQL lite
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///metapython.db"
app.config['SQLLCHEMY_TRACK_MODIFICATIONS'] = False
db=SQLAlchemy(app)


# Modelo de la tabla LOG 
class log(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    fecha_y_hora=db.Column(db.DateTime,default=datetime.utcnow)
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
                if tipo == "interactive":
                    agregra_mensajes_log(json.dumps(req))
                if "text" in messages:
                    text = messages["text"]["body"]
                    numero= messages["from"]
                    #chat= para["phone_number_id"]


                    agregra_mensajes_log(json.dumps(text))
                    agregra_mensajes_log(json.dumps(numero))
                    agregra_mensajes_log(json.dumps(req))
                    #agregra_mensajes_log(json.dumps(objeto_para))

        return jsonify({'message':'EVENT_RECEIVED'})

    except Exception as e:    
        return jsonify({'message':'EVENT_RECEIVED'})
# enviar mensaje de plantilla para envio con boton
@app.route("/send/<number>",methods=["POST", "GET"] )
def enviar_mensajes_whatsapp(number):
    empresa="SCA SOLUCIONES EXPRESS"
    #texto = texto.lower()
    data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive":{
                "type":"button",
                "body": {
                    "text": "¡Hola! ALEJANDRA ESTRADA nos contactamos de la empresa SCA SOLUCIONES EXPRESS. \n Te escribo para confirmar el servicio de transporte de IDA el dia 2024-04-02 alas 11:00. \n El conductor asignado es ERNESTO PEREZ y estará conduciendo el vehículo con placa GFD679.\n Puedes llamarlo al teléfono 3247895632 . Recuerda que tu servicio tiene un valor de $ $ 5.500 por concepto de COPAGO, ante cualquier inquietud puedes contactarnos al teléfono (601)6089876."
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

    data=json.dumps(data)

    headers = {
        "Content-Type" : "application/json",
        "Authorization" : "Bearer EAARsJaQdFWwBO14dybKf8i26DOHIzIpL9c3MCSI6umxRN1HiYw8a8RE9E7LEOUCw7ZBshoPjsdJpyr92Qz67HetCv9TSdgvDjwTZBdZCVvChNW5eHX6z8d2do9De92QCR3nTugtdfeJBJ4yUGy0lNNnSSewZCtztTwdVMMPNORJNuo3BPiPotmT984cRWrwF7lV1QlkYxUs6aZAZApm2w0W4cyTKjIhAb6wgZDZD"
    }

    connection = http.client.HTTPSConnection("graph.facebook.com")

    try:
        connection.request("POST","/v19.0/117168924654185/messages", data, headers)
        response = connection.getresponse()
        
        d=response
        with open("response.json",'w') as outfile:
            json.dump(d,outfile,indent=4)
        #resp=[]
        #resp.append(response)

        #resp=json.dumps(data)

        
        


        #agregra_mensajes_log(response)
        #return (resp)      
        #recibir_mensajes
        return jsonify({"status": response.status,"telefono":number,"reason":response.reason})
        
    

        #print(response.status, response.reason)
    except Exception as e:
        agregra_mensajes_log(json.dumps(e))
    finally:
        connection.close()
IDWAsh=""
def recibir_respuesta(req):
    req=request.get_json()
    idWA=req['entry'][0]['changes'][0]['value']['messages'][0]['id'] 

    IDWAsh=idWA
              


if __name__=='__main__':
    app.run(host='0.0.0.0',port=80,debug=True)
