import firebase_admin
from firebase_admin import credentials, firestore
import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)
# variables de las coleeciones de Firestore
coleccionVehiculos = "Vehiculos"
coleccionPropietarios = "Propietarios"

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
    a = (a or "").upper().strip()
    b = (b or "").upper().strip()
    
    # si las longitudes son muy diferentes entonces baja similitud
    if len(a) == 0 or len(b) == 0:
        return 0.0
    coincidencias = 0
    longitud_max = max(len(a), len(b))

    for i in range(min(len(a), len(b))):
        if a[i] == b[i]:
            coincidencias += 1
        elif (a[i] == 'O' and b[i] == '0') or (a[i] == '0' and b[i] == 'O'):
            coincidencias += 0.8 
        elif (a[i] == 'I' and b[i] == '1') or (a[i] == '1' and b[i] == 'I'):
            coincidencias += 0.8
        elif (a[i] == 'S' and b[i] == '5') or (a[i] == '5' and b[i] == 'S'):
            coincidencias += 0.8
        elif (a[i] == 'B' and b[i] == '8') or (a[i] == '8' and b[i] == 'B'):
            coincidencias += 0.8
    
    # porcentaje de similitud
    similitud = coincidencias / longitud_max
    return similitud


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
    return resultado



class FirebaseService:
    """
    La clase realiza las consultas y operacioens con Firebase/firestore
    """
    def __init__(self):
        """
        Funcion: constructor de la clase para inicializar la conexion con firebase

        """
        cred_path = Path(__file__).resolve().parent.parent.parent / "firebase-credentials.json"
        
        if not firebase_admin._apps:
            cred = credentials.Certificate(str(cred_path))
            firebase_admin.initialize_app(cred)
        
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
        
        vehiculoD = vehiculoDatos.to_dict() or {}

        resultado = {
            "documento_id": vehiculoDatos.id,
            "matricula": vehiculoDatos.id,
            "marca": vehiculoD.get("marca"),
            "modelo": vehiculoD.get("modelo"),
            "color": vehiculoD.get("color"),
            "año": vehiculoD.get("año"),
            "propietario_id": vehiculoD.get("propietario_id"),
            "propietario": None 
        }
        # si existen los datos del propietario se añaden al diccionario resultado
        if propietarioDatos and propietarioDatos.exists:
            propietarioD = propietarioDatos.to_dict() or {}
            resultado["propietario"] = {
                "id": propietarioDatos.id,
                "nombre": propietarioD.get("nombre"),
                "contacto": propietarioD.get("contacto"),
                "telefono": propietarioD.get("telefono"),
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
        if not self.db:
            logger.error("Firestore no esta disponible.")
            return None
        placaDetectada = (placaDetectada or "").upper().strip()
        if not placaDetectada:
            return None

        # primero hacemos busqueda por ID exacto
        try:
            vehiculo_doc_ref = self.db.collection(coleccionVehiculos).document(placaDetectada)
            vehiculoDoc = vehiculo_doc_ref.get()
            if vehiculoDoc.exists:
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
                variantesPrefijo = generarVariantes(prefijoOriginal, maxVariantes=8)
                
                candidatosPrefijo = []
                # itera sobre las variantes de prefijo generadas
                for prefijo in variantesPrefijo:
                    try:
                        query = (
                            self.db.collection(coleccionVehiculos)
                            .where(firestore.FieldPath.document_id(), ">=", prefijo)
                            .where(firestore.FieldPath.document_id(), "<", prefijo + "\uf8ff")
                            .limit(10) 
                        )

                        for vehiculoDoc in query.stream():
                            matriculaReal = vehiculoDoc.id.upper().strip()
                            #similitud entre la placa detectada y la real
                            sim = similitud(placaDetectada, matriculaReal)
                            
                            if sim >= 0.75:  
                                candidatosPrefijo.append((sim, vehiculoDoc, matriculaReal, prefijo))
                    
                    except Exception as e:
                        logger.warning(f"Error buscando prefijo '{prefijo}': {e}")
                        continue
                # si hay candidatos por prefijo seleccionamos el mejor
                if candidatosPrefijo:
                    # ordenamos por similitud descendente
                    for i in range(len(candidatosPrefijo)):
                        for j in range(i + 1, len(candidatosPrefijo)):
                            if candidatosPrefijo[j][0] > candidatosPrefijo[i][0]:
                                candidatosPrefijo[i], candidatosPrefijo[j] = candidatosPrefijo[j], candidatosPrefijo[i]
                
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
                logger.error(f"Error en busqueda por prefijo: {e}", exc_info=True)
        
        # logica de busqueda por similitud global en caso de no encontrar por prefijo
        try:
            candidatos = []
            for vehiculoDoc in self.db.collection(coleccionVehiculos).stream():
                matriculaReal = vehiculoDoc.id.upper().strip()

                sim = similitud(placaDetectada, matriculaReal)
                if sim >= 0.85:  
                    candidatos.append((sim, vehiculoDoc, matriculaReal))
            if candidatos:
                for i in range(len(candidatos)):
                    for j in range(i + 1, len(candidatos)):
                        if candidatos[j][0] > candidatos[i][0]:
                            candidatos[i], candidatos[j] = candidatos[j], candidatos[i]
                
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

        return None