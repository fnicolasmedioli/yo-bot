from unidecode import unidecode
import actions.utilidades as utilidades
from swiplserver import PrologMQI, PrologThread
import json

ARCHIVO_PROLOG_PATH = "./conocimiento.pl"

def consultar_prolog(consulta_str, find_all):
    with PrologMQI() as mqi:
        with mqi.create_thread() as prolog_thread:
            prolog_thread.query_async("consult('" + ARCHIVO_PROLOG_PATH + "').")
            prolog_thread.query_async(consulta_str, find_all = find_all)

            return prolog_thread.query_async_result()

def simplificar_nombre_asignatura(s):

    def reemplazar_romanos(s):
        if (s[-3:] == " ii"):
            s = s[:-2] + "2"
        elif (s[-2:] == " i"):
            s = s[:-1] + "1"
        return s

    return reemplazar_romanos(unidecode(s).strip().lower())

def comparar_asignaturas(a, b):
    a = simplificar_nombre_asignatura(a)
    b = simplificar_nombre_asignatura(b)

    return a == b

def buscar_asignatura_por_codigo(codigo):

    if type(codigo) != int:
        codigo = int(codigo)

    asignaturas = utilidades.OperarArchivo.leer_json("./asignaturas.json")

    for asignatura in asignaturas:
        if codigo == asignatura["codigo"]:
            return asignatura

def buscar_asignatura_por_nombre(nombre):

    asignaturas = utilidades.OperarArchivo.leer_json("./asignaturas.json")

    for asignatura in asignaturas:
        for nombre_comparado in asignatura["nombres"]:
            if (comparar_asignaturas(nombre, nombre_comparado)):
                return asignatura

def codigo_a_nombres(codigo):

    if type(codigo) == str:
        codigo = int(codigo)

    asignaturas = utilidades.OperarArchivo.leer_json("./asignaturas.json")

    for asignatura in asignaturas:
        if asignatura["codigo"] == codigo:
            return asignatura["nombres"]

def nombre_asignatura(codigo):
    lista_nombres = codigo_a_nombres(codigo)
    if (lista_nombres):
        return lista_nombres[len(lista_nombres)-1]

def nombre_a_codigo(nombre):

    asignatura = buscar_asignatura_por_nombre(nombre)

    if asignatura:
        return asignatura["codigo"]

def recuperar_info_asignatura(codigo):

    info = {}

    # Recuperar nota cursada (si existe)
    r = consultar_prolog(f"nota_cursada({codigo}, NotaCursada).", False)
    if (r):
        info["nota_cursada"] = r[0]["NotaCursada"]

    # Recuperar nota final (si existe)
    r = consultar_prolog(f"nota_final({codigo}, NotaFinal).", False)
    if (r):
        info["nota_final"] = r[0]["NotaFinal"]
    
    # Recuperar año y cuatrimestre
    r = consultar_prolog(f"materia({codigo}, Anio, Cuatrimestre).", False)
    if (r):
        info["año"] = r[0]["Anio"]
        info["cuatrimestre"] = r[0]["Cuatrimestre"]
    
    # Recuperar nota promocion (si existe)
    r = consultar_prolog(f"nota_promocion({codigo}, NotaPromocion).", False)
    if (r):
        info["nota_promocion"] = r[0]["NotaPromocion"]

    # Recuperar estado
    r = consultar_prolog(f"estado_asignatura({codigo}, Estado).", False)
    if (r):
        info["estado"] = r[0]["Estado"]

    # Agregar toda la info de asignaturas.json

    info_json = buscar_asignatura_por_codigo(codigo)
    claves = list(info_json.keys())
    for clave in claves:
        info[clave] = info_json[clave]

    r = consultar_prolog(f"me_gusta({codigo}).", False)
    info["me_gusta"] = r
    
    return info