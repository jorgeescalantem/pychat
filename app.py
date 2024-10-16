from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import http.client
import json
from pydantic import BaseModel, PositiveInt



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
def mensaje_enviado():
    import mysql.connector
    mydb = mysql.connector.connect(
        host = "pychat.informaticaf5.com",
        user = "tecJa7_TecJa7",
        password = "Dlvb47&45",
        database='tecJa7_pychat'
      )
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
    #dateac=dt_string
    bearer="beareadadadadad"
    numero="3561338854"
    mycursor = mydb.cursor()
    text="texto por capturar de prueba"
    sql = "INSERT INTO registro (fecha_hora,mensaje_enviado,mensaje_recibido,id_wa,timestamp_wa,telefono_wa,telefono_from,profile_name,key,mensaje,status,estado,bearer) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)"
    data=(1,dt_string,
          text,
          "null"
          ,"null"
          ,"null"
          ,"null"
          ,"null"
          ,numero
          ,"profile"
          ,"key200"
          ,"200"
          ,"send"
          ,bearer)
    mycursor.execute(sql, data)
    #mycursor.execute(sql)
    mydb.commit()
    mycursor.close()
    mydb.close()



    return("guardado")

@app.route("/send/<number>",methods=["POST", "GET"] )
def enviar_mensajes_whatsapp(number):
    empresa="SCA SOLUCIONES EXPRESS"
    #texto = texto.lower()
    data = request.get_json()

    #data=json.dumps(data)
    #data=jsonify(data)

    headers = {
        "Content-Type" : "application/json",
        "Authorization" : "Bearer EAARsJaQdFWwBOxGhnIYpPoTk9VKcHcI2ThcHr7B23uSADlGCtOQtRvlHOM9MqU4R2cft0qWcn6PV4wgAOZA0ZCXPHDQhYLTD0p5Omhhbg04A0DcXjbULP0uVGfIXu3y0dwx0PsKqcZC0ITQ6Ffnjg7ZAvEhZCIHp4DHOZCQj5sZA2Yz2XHOw4nkFIUILaLLCyh2R5pSfQqJOKu5SaUBF4BY77xGMNZBxnLHkZApj0ghZBkmAZDZD"
    }

    connection = http.client.HTTPSConnection("graph.facebook.com")
    try:
        connection.request("POST","/v20.0/117168924654185/messages", data, headers)
        response = connection.getresponse()
        #print(response.status, response.reason)
        recibir_mensajes(response.text)
        docs_dict = [response.to_json() for doc in response]

        if response.status == 200:
            if len (docs_dict) != 0:
                rp="respuesta ID"
                agregra_mensajes_log(json.dumps(docs_dict))
            else:
                rp="respuesta sin ID"
        elif response.status == 500:
            rp="respuesta status 500"
        else:
            rp="respuesta status 500"
        return jsonify({"status": response.status,"telefono":number,"reason":response.reason,"rp ciclo":rp,"id_wa":product1})        

    except Exception as e:
        return jsonify({'message':'EXCEP'})
    finally:
        connection.close()

if __name__=='__main__':
    app.run(host='0.0.0.0',port=80,debug=True)
