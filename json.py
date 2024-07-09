import json 

def cargar_datos(ruta):
    with open(ruta) as contenido:
        datos=json.load(contenido)
        for dato in datos:
            print (dato) 

if __name__=='__main__':
    ruta='C:\Users\JAEM\Documents\python\pychat\docs\ejemplo_response.json'

