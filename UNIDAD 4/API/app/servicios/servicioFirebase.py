import firebase_admin
from firebase_admin import credentials, firestore
import logging
from pathlib import Path
from typing import Dict, Any, List
import difflib

logger = logging.getLogger(__name__)
# variables de las coleeciones de Firestore
coleccionVehiculos = "Vehiculos"
coleccionPropietarios = "Propietarios"
# diccionario de confuciones del OCR
diccionarioOcr = {
    '0': ['O', 'D', 'Q'],
    'O': ['0', 'Q', 'D'],
    'I': ['1', 'L', 'T'],
    '1': ['I', 'L'],
    'L': ['I', '1'],
    'Z': ['2', '7'],
    '2': ['Z'],
    'S': ['5', '8'],
    '5': ['S'],
    'B': ['8', '3'],
    '8': ['B', '3'],
    '3': ['8', 'B'],
    '6': ['G'],
    'G': ['6', 'C'],
    'C': ['G', 'O'],
    'M': ['N', 'H'],
    'N': ['M', 'H'],
    'H': ['M', 'N'],
    'V': ['Y'],
    'Y': ['V'],
}

def similitud(a: str, b: str) -> float:
    """
    Funcion: metodo que calcula la similitud entre dos cadenas toamdo
            en cuenta confusiones del OCR.
    Argumento: 
        a: cadena 1
        b: cadena 2  
    Retorno: 
        numero float: retorna un numero decimal entre 0 y 1 indicando similitud.         
    """
    # normaliza entradas a mayusculas
    a = (a or "").upper().strip()
    b = (b or "").upper().strip()
    # tabla de traduccion para las confusiones
    trans = str.maketrans({
        "O": "0",
        "I": "1",
        "L": "1",
        "Z": "2",
        "S": "5",
        "B": "8",
    })
    a2 = a.translate(trans)
    b2 = b.translate(trans)
    # calcula similitud base
    base = difflib.SequenceMatcher(None, a, b).ratio()
    alt = difflib.SequenceMatcher(None, a2, b2).ratio()
    return max(base, alt)


def generarVariantes(prefijo: str, maxVariantes: int = 5) -> List[str]:
    """
    Funcion: se encarga de generar variantes de un prefijo de placa
            utilizando un diccionarioOcr, esto para ayudar a mejorar la consulta.
    Argumento: 
        prefijo: recibe una cadena con el prefijo de la placa.
        maxVariantes: se establece el num maximo de variantes.
    Retorno: 
        Lista de cadenas: la funcion retorna una lista de cadenas con las variantes.
    """
    # si el prefijo es menor que 3, no genera nada
    if len(prefijo) < 3:
        return [prefijo]
    
    variantes = {prefijo}  
    # itera sobre los primeros 3 caracteres del prefijo
    for pos in range(min(3, len(prefijo))):
        char = prefijo[pos]
        # si el caracter esta en el dicc, genera variante
        if char in diccionarioOcr:
            for reemplazo in diccionarioOcr[char]:
                nueva = prefijo[:pos] + reemplazo + prefijo[pos+1:]
                variantes.add(nueva)
                
                if len(variantes) >= maxVariantes:
                    break
        
        if len(variantes) >= maxVariantes:
            break
    # limita el num de varienates al max establecido
    resultado = list(variantes)[:maxVariantes]
    logger.debug(f"Variantes generadas para '{prefijo}': {resultado}")
    return resultado



class FirebaseService:
    """
    La clase realiza las consultas y operacioens con Firebase/firestore
    """
    def __init__(self):
        """
        Funcion: constructor de la clase para inicializar la conexion con firebase
        Argumento: no recibe nada.
        Retorno: no retorna nada.
        """
        cred_path = Path(__file__).resolve().parent.parent.parent / "firebase-credentials.json"
        
        if not firebase_admin._apps:
            cred = credentials.Certificate(str(cred_path))
            firebase_admin.initialize_app(cred)
            logger.info("Firebase inicializado")
        
        self.db = firestore.client()

    def combinarDatos(self, vehiculoDatos: firestore.DocumentSnapshot, propietarioDatos: firestore.DocumentSnapshot | None) -> Dict[str, Any]:
        
        """
        Funcion: se encarga de combinar los datos obtenidos de la coleccion vehiculos 
                y propietarios, combinandolos en un solo diccionario.
        Argumento:
            vahiculoDatos: documento de fisrestore con los datos del vehiuculo.
            propietarioDatos: documento de firestore con los datos del propietario.

        Retorno: diccionario con los datos combinados del vehiculo y propietario.
        """
        
        # obtenermos los datos del vehiculo
        vehiculo_data = vehiculoDatos.to_dict() or {}
        

        # creamos un diccionario con los datos del vehiculo
        resultado = {
            "documento_id": vehiculoDatos.id,
            "matricula": vehiculoDatos.id,
            "marca": vehiculo_data.get("marca"),
            "modelo": vehiculo_data.get("modelo"),
            "color": vehiculo_data.get("color"),
            "año": vehiculo_data.get("año"),
            "propietario_id": vehiculo_data.get("propietario_id"),
            "propietario": None 
        }
        # si existen los datos del propietario se añaden al diccionario resultado
        if propietarioDatos and propietarioDatos.exists:
            propietario_data = propietarioDatos.to_dict() or {}
            resultado["propietario"] = {
                "id": propietarioDatos.id,
                "nombre": propietario_data.get("nombre"),
                "contacto": propietario_data.get("contacto"),
                "telefono": propietario_data.get("telefono"),
            }
        
        return resultado

    def buscarVehiculo(self, placaDetectada: str) -> Dict[str, Any] | None:
        """
        funcion: busca un vehiculo en firestore por medio de la placa detectada,
                primero busca por el id exacto, si no entonces usa prefijos y similitud.
        Argumento:
            placaDetectada: recibe una cadena con la placa optenida del OCR.
        Retorna: diccionario con los datos del vehiculo y propietario o en su lugar None 
                si no encuentra nada.
        """
        # verificamos si la BD esta disponible
        if not self.db:
            logger.error("Firestore no está disponible.")
            return None
        placaDetectada = (placaDetectada or "").upper().strip()
        if not placaDetectada:
            return None

        logger.info(f"Buscando en Firebase: {placaDetectada}")
        # primero hacemos busqueda por ID exacto
        try:
            vehiculo_doc_ref = self.db.collection(coleccionVehiculos).document(placaDetectada)
            vehiculoDoc = vehiculo_doc_ref.get()
            # si encuentra por ID exacto, obtiene datos del propietario y retorna combinado
            if vehiculoDoc.exists:
                logger.info(f"Vehiculo encontrado por ID exacto: {vehiculoDoc.id}")
                propietarioId = (vehiculoDoc.to_dict() or {}).get("propietario_id")
                propietarioDoc = None
                if propietarioId:
                    propietarioDoc = self.db.collection(coleccionPropietarios).document(propietarioId).get()
                
                return self.combinarDatos(vehiculoDoc, propietarioDoc)
        except Exception as e:
            logger.warning(f"Error buscando por ID: {e}")

        # si no encuentra por ID, entonces busca por prefijos 
        if len(placaDetectada) >= 3:
            try:
                prefijoOriginal = placaDetectada[:3]
                # generar variantes del prefijo usando el diccionario OCR
                variantesPrefijo = generarVariantes(prefijoOriginal, maxVariantes=8)
                logger.info(f"Buscando por prefijos: {variantesPrefijo}")
                
                candidatosPrefijo = []
                # itera sobre las variantes de prefijo generadas
                for prefijo in variantesPrefijo:
                    try:
                        # consulta firestore en los documentos que coincidan
                        query = (
                            self.db.collection(coleccionVehiculos)
                            .where(firestore.FieldPath.document_id(), ">=", prefijo)
                            .where(firestore.FieldPath.document_id(), "<", prefijo + "\uf8ff")
                            .limit(10) 
                        )
                        # iteramos sobre los resultados obtenidos
                        for vehiculoDoc in query.stream():
                            matriculaReal = vehiculoDoc.id.upper().strip()
                            # calculamos la similitud entre la placa detectada y la real
                            sim = similitud(placaDetectada, matriculaReal)
                            
                            if sim >= 0.75:  
                                candidatosPrefijo.append((sim, vehiculoDoc, matriculaReal, prefijo))
                    
                    except Exception as e:
                        logger.warning(f"Error buscando prefijo '{prefijo}': {e}")
                        continue
                # si hay candidatos por prefijo seleccionamos el mejor
                if candidatosPrefijo:
                    # ordenamos con sort por similitud descendente
                    candidatosPrefijo.sort(key=lambda t: t[0], reverse=True)
                    sim, mejorVehiculo, matriculaReal, prefijoUsado = candidatosPrefijo[0]
                    
                    propietarioId = (mejorVehiculo.to_dict() or {}).get("propietario_id")
                    propietarioDoc = None
                    if propietarioId:
                        propietarioDoc = self.db.collection(coleccionPropietarios).document(propietarioId).get()

                    normalizado = self.combinarDatos(mejorVehiculo, propietarioDoc)
                    normalizado["_corregido_desde"] = placaDetectada
                    normalizado["_similitud"] = sim
                    normalizado["_metodo"] = "prefijo_variante"
                    normalizado["_prefijo_usado"] = prefijoUsado
                    
                    return normalizado
                    
            except Exception as e:
                logger.error(f"Error en búsqueda por prefijo: {e}", exc_info=True)
        
        # logica de busqueda por similitud global en caso de no encontrar por prefijo
        try:
            candidatos = []
            # iteramos cobre todos los documentos de vehiculos
            for vehiculoDoc in self.db.collection(coleccionVehiculos).stream():
                matriculaReal = vehiculoDoc.id.upper().strip()

                sim = similitud(placaDetectada, matriculaReal)
                if sim >= 0.85:  
                    candidatos.append((sim, vehiculoDoc, matriculaReal))
            # si hay candidaos por similitud global seleccionamos el mejor
            if candidatos:
                # ordenamos con sort por similitud descendente
                candidatos.sort(key=lambda t: t[0], reverse=True)
                sim, mejorVehiculo, matriculaReal = candidatos[0]

                propietarioId = (mejorVehiculo.to_dict() or {}).get("propietario_id")
                propietarioDoc = None
                if propietarioId:
                    propietarioDoc = self.db.collection(coleccionPropietarios).document(propietarioId).get()

                normalizado = self.combinarDatos(mejorVehiculo, propietarioDoc)
                normalizado["_corregido_desde"] = placaDetectada
                normalizado["_similitud"] = sim
                normalizado["_metodo"] = "similitud_global"
                
                logger.info(
                    f"Encontrado por similitud global ({sim*100:.1f}%): {placaDetectada} - {matriculaReal}"
                )
                return normalizado

        except Exception as e:
            logger.error(f"Error en búsqueda por similitud: {e}", exc_info=True)

        logger.warning(f"Placa '{placaDetectada}' no encontrada en Firebase")
        return None