import json
import os.path

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
                # archivo.close()
        else:
            print("Archivo no encontrado")
            r = {}
        return r