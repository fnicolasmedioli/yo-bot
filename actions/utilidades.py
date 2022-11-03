import json
import os.path
import re

def slots_a_entidades(lista_slots, tracker):
    entidades = {}
    for s in lista_slots:
        entidades[s] = { "value": tracker.get_slot(s) }
    return entidades

def mapear_entidades(lista_entidades):
    mapeo = {}

    for item in lista_entidades:
        if not (item["entity"] in mapeo) or mapeo[item["entity"]]["extractor"] == "DIETClassifier" and item["extractor"] == "RegexEntityExtractor":
            mapeo[item["entity"]] = item
    
    if "asignatura" in mapeo and mapeo["asignatura"]["extractor"] == "DIETClassifier":
        del mapeo["asignatura"]
    
    return mapeo

def es_plural(s):
    return s[-2:] == "es" or s[-1] == "s"

def plural_a_singular(s):
    if not es_plural:
        return s
    elif s[-2] == "e":
        return s[0:-2]
    else:
        return s[0:-1]            

class OperarArchivo():

    @staticmethod
    def escribir_json(s,ruta):
        with open(ruta,"w") as archivo:
            json.dump(s, archivo, indent=4)

    @staticmethod
    def leer_json(ruta): 
        r = None
        if os.path.isfile(ruta):
            with open(ruta, "r") as archivo:
                r = json.load(archivo)
        else:
            print("Archivo no encontrado")
            r = {}
        return r
    

# Transforma string del tipo "cinco", en la respectiva hora "5:00", "12:00"
def palabra_a_hora_numerica(s):
    numeros_palabras = [None, "una", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez", "once", "doce", "trece", "catorce", "quince", "dieciseis", "diecisiete", "dieciocho", "diecinueve", "veinte", "veintiuna", "veintidos", "veintitres", "venticuatro"]
    try:
        return numeros_palabras.index(s)
    except:
        return None


def parsear_y_transformar_hora(hora):

    pm = False

    hora = hora.replace(" de la mañana", "")
    hora = hora.replace(" am", "")
    hora = hora.replace(" de la tarde", " pm")
    hora = hora.replace(" de la noche", " pm")
    
    if hora.find(" pm") != -1 or hora.find(" PM") != -1:
        pm = True
        hora = hora[:-3]

    reg1 = r"^\d{1,2}(\:\d\d)?$"

    if re.search(reg1, hora):
        if hora.find(":") == -1:
            hora += ":00"
        hora = hora.zfill(5)
        if pm:
            hora = str(int(hora[:2]) + 12).zfill(2) + hora[2:]
        return hora

    # Buscar horas en formato "cinco", "cuatro y media", "dos menos cuarto"

    separados = hora.split(" ")

    if len(separados) == 1 or len(separados) == 2:

        hora = palabra_a_hora_numerica(separados[0])

        if not hora:
            return None

        if pm:
            hora += 12
    
        return str(hora).zfill(2) + ":00"

    if len(separados) == 3 or len(separados) == 4:

        try:
            hora = int(separados[0])
        except:
            hora = palabra_a_hora_numerica(separados[0])
        
        hora_str = None

        if not hora:
            return None        

        if pm:
            hora += 12

        modificador = {
            "media": 30,
            "veinte": 20,
            "cuarto": 15,
            "diez": 10,
            "cuarenta": 40
        }

        minutos = None

        if not separados[2] in modificador:
            # Probar si tampoco es del tipo "cuatro y 25"
            try:
                minutos = int(separados[2])
            except:
                return None
        else:
            minutos = modificador[separados[2]]

        if separados[1] == "y":
            hora_str = str(hora).zfill(2) + ":" + str(minutos)
            return hora_str
        
        if separados[1] == "menos":
            hora = hora-1
            if hora == -1:
                hora = 23
            hora_str = str(hora).zfill(2) + ":" + str(60-minutos)
            return hora_str