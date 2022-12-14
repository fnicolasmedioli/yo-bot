from typing import Any, Text, Dict, List, Optional
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.types import DomainDict
from unidecode import unidecode
import actions.asignaturas as asignaturas
import actions.utilidades as utilidades
from swiplserver import PrologMQI, PrologThread
import json
import datetime
import actions.telegram_api as telegram_api
import requests
import os
import random

# from rasa_sdk import Tracker, FormValidationAction

xRapidApiKey = os.environ.get("xRapidApiKey")

# dispatcher.utter_message(text="Hello World!")
# tracker.latest_message["intent"].get("name")
# tracker.latest_message["entities"]
# tracker.latest_message["entities"][0]["value"]
# return [SlotSet("tipo_tarjeta", tipo_tarjeta)]
# dispatcher.utter_message(template="utter_bring_umbrella")
# tracker.get_slot("id_asignatura")
# latest_message["entities"] = [
#     {
#         "entity": "nombre_entidad",
#         "value": "..."
#         "extractor": "...",
#     }
# ]

class ActionMateriaMasMeGusta(Action):

    def name(self) -> Text:
        return "action_materia_mas_me_gusta"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(response="utter_materia_mas_me_gusta")
        return [SlotSet("asignatura", "programacion exploratoria")]


class ActionSetAsignatura(Action):

    def name(self) -> Text:
        return "action_set_asignatura"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        entidades = utilidades.mapear_entidades(tracker.latest_message["entities"])

        if "asignatura" in entidades and entidades["asignatura"]["extractor"] == "RegexEntityExtractor":

            cod = asignaturas.nombre_a_codigo(entidades["asignatura"]["value"])

            if cod:
                return [SlotSet("asignatura", str(cod))]
        
        return []


class ActionComoVoy(Action):

    def name(self) -> Text:
        return "action_como_voy"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        entidades = utilidades.mapear_entidades(tracker.latest_message["entities"])

        if ("asignatura" in entidades and (not "como_vas_con" in entidades or entidades["como_vas_con"]["value"] == "cursada")
            or (tracker.get_slot("asignatura") and tracker.get_slot("como_vas_con") == None)):

            # Caso especifico pregunta de una materia

            if not "asignatura" in entidades:
                entidades = utilidades.slots_a_entidades(["asignatura"], tracker)

            codigo_asignatura = asignaturas.nombre_a_codigo(entidades["asignatura"]["value"])

            if not codigo_asignatura:
                dispatcher.utter_message(text="y esa asignatura????")
                return []

            info_asignatura = asignaturas.recuperar_info_asignatura(codigo_asignatura)

            if info_asignatura["estado"] != "en curso":
                msg = None
                if info_asignatura["estado"] == "no cursada":
                    msg = f"no he cursado {asignaturas.nombre_asignatura(codigo_asignatura)} todav??a"
                else:
                    msg = f"no estoy cursando {asignaturas.nombre_asignatura(codigo_asignatura)}, ya la curs??"

                dispatcher.utter_message(text=msg)
                return []                        
            
            msg = f"en {asignaturas.nombre_asignatura(codigo_asignatura)} {info_asignatura['como_voy']}"
            dispatcher.utter_message(text=msg)
            
            return []

        elif "como_vas_con" in entidades or tracker.get_slot("como_vas_con"):
            if not "como_vas_con" in entidades:
                entidades = utilidades.slots_a_entidades(["como_vas_con"], tracker)
            if "como_vas_con" in entidades:
                if entidades["como_vas_con"]["value"] == "cursada":
                    dispatcher.utter_message(response="utter_como_voy_con_cursada")
                    return [SlotSet("como_vas_con", "cursada")]
                elif entidades["como_vas_con"]["value"] == "proyecto":
                    dispatcher.utter_message(response="utter_como_voy_con_proyecto")
                    return [SlotSet("como_vas_con", "proyecto")]
                elif entidades["como_vas_con"]["value"] == "finales":
                    dispatcher.utter_message(response="utter_como_estoy_finales")
                    return [SlotSet("como_vas_con", "finales")]
                elif entidades["como_vas_con"]["value"] == "carrera":
                    dispatcher.utter_message(response="utter_como_llevo_carrera")
                    return [SlotSet("como_vas_con", "carrera")]

        dispatcher.utter_message(text="voy bien :)")

        return []


class ActionRespuestaAsignatura(Action):

    def name(self) -> Text:
        return "action_respuesta_asignatura"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        cod_asignatura = tracker.get_slot("asignatura")

        if not cod_asignatura:
            # Pregunta general
            dispatcher.utter_message(response="utter_como_estoy_finales")
            return []

        # Recuperar datos de la asignatura

        info_asignatura = asignaturas.recuperar_info_asignatura(cod_asignatura)
        nombre_alternativo = info_asignatura["nombres"][len(info_asignatura["nombres"])-1]

        if info_asignatura["estado"] == "no cursada":
            dispatcher.utter_message(text=f"todav??a ni curs?? {nombre_alternativo}")
        elif info_asignatura["estado"] == "cursada":
            dispatcher.utter_message(text=f"curs?? {nombre_alternativo} pero todav??a no di el final")
        elif info_asignatura["estado"] == "promocion":
            dispatcher.utter_message(text=f"a {nombre_alternativo} la promocion?? con un {info_asignatura['nota_promocion']}")
        elif info_asignatura["estado"] == "examen":
            dispatcher.utter_message(text=f"lo aprob?? con un {info_asignatura['nota_final']}")
        else:
            dispatcher.utter_message(text=f"la estoy cursando este cuatrimestre")

        return []


class ActionDiasParaElMundial(Action):

    def name(self) -> Text:
        return "action_dias_para_el_mundial"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        fecha_mundial = datetime.date(2022, 11, 20)
        hoy = datetime.date.today()
        delta = fecha_mundial - hoy

        dias = delta.days

        dispatcher.utter_message(text=f"faltan {dias} d??as, empieza el 20 de noviembre")

        return []


class ActionTeGustaAlgo(Action):

    def name(self) -> Text:
        return "action_te_gusta_algo"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        slot_algo = tracker.get_slot("te_gusta")

        if not slot_algo:
            return []
        
        cosas_que_no_me_gustan = ["pepino", "ara??a", "fumar", "politicos", "mosca"]

        algo_singular = utilidades.plural_a_singular(slot_algo)

        if algo_singular in cosas_que_no_me_gustan:
            if utilidades.es_plural(slot_algo):
                dispatcher.utter_message(text="no me gustan para nada!")
            else:
                dispatcher.utter_message(text="no me gusta para nada!")
        else:
            if utilidades.es_plural(slot_algo):
                dispatcher.utter_message(text="me encantan!")
            else:
                dispatcher.utter_message(text="me encanta!")
        

class ActionTeGustaAsignatura(Action):

    def name(self) -> Text:
        return "action_te_gusta_asignatura"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        if len(tracker.latest_message["entities"]) == 0:
            return []

        entidad_asignatura = tracker.latest_message["entities"][0]["value"]

        asignatura_json = asignaturas.buscar_asignatura_por_nombre(entidad_asignatura)

        if not asignatura_json:
            return []

        cod_asignatura = asignatura_json["codigo"]

        info = asignaturas.recuperar_info_asignatura(cod_asignatura)

        if info["me_gusta"]:
            dispatcher.utter_message(text=f"siii! {asignaturas.nombre_asignatura(cod_asignatura)} es de las materias que m??s me gustan")
        else:
            dispatcher.utter_message(text=f"no, {asignaturas.nombre_asignatura(cod_asignatura)} es de las materias que menos me gustan")
        

        return []
    

class ActionTelegramManagement(Action):

    def name(self) -> Text:
        return "action_telegram_management"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        if not "metadata" in tracker.latest_message or not tracker.latest_message["metadata"]:
            return []
        
        metadata = tracker.latest_message["metadata"]

        message = metadata["message"]
        user_id = str(message["from"]["id"])
        user_is_bot = message["from"]["is_bot"]
        user_name = message["from"]["first_name"]
        message_timestamp = message["date"]
        chat_id = str(message["chat"]["id"])
        chat_type = message["chat"]["type"]

        if user_is_bot or chat_type == "private":
            return []

        data_obj = utilidades.OperarArchivo.leer_json("latest_messages.json")

        if not chat_id in data_obj:
            data_obj[chat_id] = {}

        write = ""

        if not user_id in data_obj[chat_id]:
            data_obj[chat_id][user_id] = {
                "nombre": user_name,
                "ultimo_msg": message_timestamp,
                "ultima_solicitud": message_timestamp
            }
            write += f"Hola {user_name}! Te registr?? en mi base de datos, a partir de ahora si no trabajas te voy a mandar al frente 3:)\n"
        
        # Actualizar timestamps del usuario que habl??

        data_obj[chat_id][user_id]["ultimo_msg"] = message_timestamp
        data_obj[chat_id][user_id]["ultima_solicitud"] = message_timestamp

        # Para cada integrante chequear
        # ultimo mensaje y ultimo llamado de atencion

        now = datetime.datetime.timestamp(datetime.datetime.now())

        MAX_IDLE = 3600 * 24 * 2 # 2 dias
        TIEMPO_SOLICITUD = 3600 * 5 # 6 horas

        for k in list(data_obj[chat_id].keys()):
            usuario = data_obj[chat_id][k]

            if (now - usuario["ultimo_msg"] > MAX_IDLE) and (now - usuario["ultima_solicitud"] > TIEMPO_SOLICITUD):
                # Entonces solicitar al usuario que participe en el grupo
                write += f"Por favor {usuario['nombre']}, participa en el grupo.\n"
                usuario["ultima_solicitud"] = int(now)
        
        utilidades.OperarArchivo.escribir_json(data_obj, "latest_messages.json")

        if write != "":
            telegram_api.send_message(write, chat_id)


        if not tracker.get_slot("nombre"):
            return [SlotSet("nombre", user_name)]
        else:
            return []

def find_last(s, q):
    desde = -1
    while True:
        t = s.find(q, desde + 1)
        if t == -1:
            break
        desde = t
    return desde


def url_imagen_valida(url):

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"
    }

    try:
        r = requests.get(url, headers=headers, timeout=4)

        if r.status_code == 200 and "image" in r.headers["content-type"]:
            return True
    except:
        pass

    return False


def seleccionar_url_imagen_valida(arr):
    cantidad = len(arr)
    try_n = 0
    url_elegida = None

    while try_n < 5 and not url_elegida:
        n_random = random.randint(0, cantidad-1)
        url_random = arr[n_random]["url"]
        if url_imagen_valida(url_random):
            url_elegida = url_random
        try_n += 1
    
    return url_elegida

class ActionUnaFoto(Action):

    def name(self) -> Text:
        return "action_foto"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        if not xRapidApiKey:
            print("xRapidApiKey no encontrada")
            return []
        
        if len(tracker.latest_message["entities"]) == 0:
            return []

        texto_busqueda = tracker.latest_message["entities"][0]["value"]

        if not texto_busqueda:
            texto_busqueda = tracker.get_slot("pedido_foto")

        if not texto_busqueda:
            return []

        print(f"imagen a buscar: \"{texto_busqueda}\"")
        
        querystring = {"q": texto_busqueda, "pageNumber": "1", "pageSize": "3", "autoCorrect": "true"}

        headers = {
            "X-RapidAPI-Key": xRapidApiKey,
            "X-RapidAPI-Host": "contextualwebsearch-websearch-v1.p.rapidapi.com"
        }

        url_foto = None

        try:
            response = requests.request("GET", "https://contextualwebsearch-websearch-v1.p.rapidapi.com/api/Search/ImageSearchAPI", headers=headers, params=querystring)
        except:
            dispatcher.utter_message(text="no me pude conectar con la API de imagenes :(")
            return []

        if len(response.json()["value"]) == 0:
            dispatcher.utter_message(text="no encontr?? fotos :(")
            return []

        url_foto = seleccionar_url_imagen_valida(response.json()["value"])

        if not url_foto:
            dispatcher.utter_message(text="no pude conseguir fotos :(")
            return []

        dispatcher.utter_message(image=url_foto)

        return []


class ActionEstablecerReunion(Action):

    def name(self) -> Text:
        return "action_establecer_reunion"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Guardar los datos

        datos_disponibilidad = utilidades.OperarArchivo.leer_json("disponibilidad.json")

        dia = tracker.get_slot("dia")

        if not dia in datos_disponibilidad:
            datos_disponibilidad[dia] = []

        # Asumo que la reunion dura una hora

        hora_str = tracker.get_slot("hora")

        lugar = tracker.get_slot("lugar")

        datos_a_guardar = {
            "desde": hora_str,
            "hasta": str((int(hora_str[0:2])+1)%24).zfill(2) + hora_str[2:],
            "motivo": "tengo reunion con alguien",
            "lugar": lugar
        }

        nombre_persona = tracker.get_slot("nombre")
        
        if nombre_persona:
            datos_a_guardar["motivo"] = "tengo reunion con " + nombre_persona

        datos_disponibilidad[dia].append(datos_a_guardar)

        utilidades.OperarArchivo.escribir_json(datos_disponibilidad, "disponibilidad.json")

        dispatcher.utter_message(text=f"bien, entonces el {dia} a las {hora_str} voy a estar esperandote en {lugar}!")

        return [SlotSet("dia", None), SlotSet("hora", None), SlotSet("lugar", None)]


def estoy_ocupado(dia, hora):

    datos = utilidades.OperarArchivo.leer_json("disponibilidad.json")

    if not dia in datos:
        return False

    for rango_horario in datos[dia]:
        if hora >= rango_horario["desde"] and hora <= rango_horario["hasta"]:
            return rango_horario["motivo"]


class ValidateReunionForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_reunion_form"

    def validate_dia(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:

        utter = len(utilidades.mapear_entidades(tracker.latest_message["entities"]))

        hora = tracker.get_slot("hora")

        validos = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo", "hoy", "ma??ana"]

        if slot_value in validos:

            if hora:

                ocupado = estoy_ocupado(slot_value, hora)

                if ocupado:
                    if utter:
                        dispatcher.utter_message(text="no estoy disponible ese dia a esa hora porque " + ocupado + ", coordinemos otro momento")
                    SlotSet("dia", None)
                    SlotSet("hora", None)
                    return { "dia": None, "hora": None }

            return { "dia": slot_value }

        return { "dia": None }

    def validate_hora(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:

        utter = len(utilidades.mapear_entidades(tracker.latest_message["entities"]))

        if not slot_value:
            return { "hora": None }

        hora_transformada = utilidades.parsear_y_transformar_hora(slot_value)

        dia = tracker.get_slot("dia")

        if hora_transformada:
            if dia:
                ocupado = estoy_ocupado(dia, slot_value)
                if ocupado:
                    if utter:
                        dispatcher.utter_message(text="no estoy disponible ese dia a esa hora porque " + ocupado + ", coordinemos otro momento")
                    SlotSet("dia", None)
                    SlotSet("hora", None)
                    return { "dia": None, "hora": None }
            return { "hora": hora_transformada }

        return { "hora": None }