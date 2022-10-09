from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from unidecode import unidecode
import actions.asignaturas as asignaturas
import actions.utilidades as utilidades
from swiplserver import PrologMQI, PrologThread
import json

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
                    msg = f"no he cursado {asignaturas.nombre_asignatura(codigo_asignatura)} todavía"
                else:
                    msg = f"no estoy cursando {asignaturas.nombre_asignatura(codigo_asignatura)}, ya la cursé"

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
            
            dispatcher.utter_message(response="utter_como_voy_con_no_entendi")
            return []

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
            dispatcher.utter_message(text=f"todavía ni cursé {nombre_alternativo}")
        elif info_asignatura["estado"] == "cursada":
            dispatcher.utter_message(text=f"cursé {nombre_alternativo} pero todavía no di el final")
        elif info_asignatura["estado"] == "promocion":
            dispatcher.utter_message(text=f"a {nombre_alternativo} la promocioné con un {info_asignatura['nota_promocion']}")
        elif info_asignatura["estado"] == "examen":
            dispatcher.utter_message(text=f"lo aprobé con un {info_asignatura['nota_final']}")
        else:
            dispatcher.utter_message(text=f"la estoy cursando este cuatrimestre")

        return []