import cv2
import numpy as np
import logging
import re
import easyocr

logger = logging.getLogger(__name__)
# lista de expreciones regulares para detectar placas
exprecionesRegulares = [
    re.compile(r'\b([A-Z]{3})[- ]?(\d{2})[- ]?(\d{2})\b'),  
    re.compile(r'\b[A-Z]{3}\d{3,5}\b'),                    
    re.compile(r'\b[A-Z]{2}\d{4,5}\b'),                     
    re.compile(r'\b\d{3,4}[A-Z]{3}\b'),                     
    re.compile(r'\b(\d{3})[- ]?([A-Z]{3})\b'),              
    re.compile(r'\b([A-Z]{3})[- ]?(\d{3})[- ]?([A-Z])\b'),  
    re.compile(r'\b([A-Z])[- ]?(\d{2})[- ]?([A-Z]{3})\b'),  
]

# caracteres permitidos en el OCR
permitidos = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789- '


def alfanumericos(texto: str) -> str:
    """
    funcion: metodo que elimina todos los caracteres que no sean letras o numeros
    argumento: 
        texto: recibe cadena de texto a procesar

    retorno: texto limpio de caracteres no alfanumericos
    """
    return re.sub(r'[^A-Z0-9- ]', '', texto.upper())


def normalizarCoincidencia(texto: str) -> str:
    """
    Funcion: normaliza una cadena de texto que representa una placa.
    argumento: 
        texto: recibe una cadena de texto a normalizar.
    Retorno: devuelve la placa en formato limpio.
    """
    texto_limpio = texto.upper().replace(' ', '')
    coincidencia = re.match(r'^([A-Z]{3})(\d{2})(\d{2})$', re.sub(r'[^A-Z0-9]', '', texto_limpio))
    # si coincide con el formato, formatea con guiones
    if coincidencia:
        return f'{coincidencia.group(1)}-{coincidencia.group(2)}-{coincidencia.group(3)}'
    return re.sub(r'[^A-Z0-9]', '', texto_limpio)


def puntuar(placa: str) -> int:
    """
    Funcion: asigna una puntuacion a una placa segun su forma y longitud

    Argumento: 
        placa str: recibe una cadena de texto que representa la placa
    retorno:
        devuelve un num entero que representa la puntuacion
    """
    placaSinGuion = placa.replace('-', '')
    # patrones mas comunes 
    if re.fullmatch(r'[A-Z]{3}\d{4}', placaSinGuion):
        return 100
    if re.fullmatch(r'[A-Z]{3}\d{2}\d{2}', placaSinGuion):
        return 95
    if re.fullmatch(r'[A-Z]{3}\d{3,5}', placaSinGuion):
        return 90
    if re.fullmatch(r'[A-Z]{2}\d{4,5}', placaSinGuion) or re.fullmatch(r'\d{3,4}[A-Z]{3}', placaSinGuion):
        return 80
    # si el patron no es comun entonces puntua segun su longitud
    if not (6 <= len(placaSinGuion) <= 9):
        return 10
    return 50 + min(len(placaSinGuion), 9)


class ProcesarOCR:
    def __init__(self):
        self.lector = None
        self.lector = easyocr.Reader(['en', 'es'], gpu=False)

    def escalaGris(self, imagen: np.ndarray) -> np.ndarray:
        """
        Funcion: se encarga de convertir una img a escala de grises
        argumento: 
            imagen: recibe una imagen en formato numpy ndarray 
                    para convertirla a escala de grises
        Retorno: devuelve un array en escala de grises
        """
        return cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY) if imagen.ndim == 3 else imagen.copy()

    def mejorar(self, imagen: np.ndarray) -> np.ndarray:
        """
        Funcion: metodo encargado de mejora el contraste de una 
                imagen en escala de grises
        Argumento:
            imagen: recibe una imagen en formato numpy ndarray en escala de grises
        Retorno: devuelve una imagen mejorada en escala de grises
        """
        gris = self.escalaGris(imagen)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gris = clahe.apply(gris)
        return gris

    def variantes(self, imagen: np.ndarray) -> list[np.ndarray]:
        """
        funcion: genera variantes de una img para mejorar el OCR
        argumento: 
            imagen: recibe una imagen en formato numpy ndarray 
                    para generar variantes que mejoren la deteccion.
        
        retorno: devuelve una lista de imagenes en diferentes variantes
        """
        grisMejorada = self.mejorar(imagen)
        variantes = [grisMejorada]
        _, otsu = cv2.threshold(grisMejorada, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        variantes.append(otsu)

        adaptativa = cv2.adaptiveThreshold(grisMejorada, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY, 15, 5)
        variantes.append(adaptativa)

        if np.mean(otsu) > 180:
            variantes.append(255 - otsu)
        return variantes


    def leerLineas(self, imgGris: np.ndarray) -> list[str]:
        """
        funcion: utiliza ocr y se encarga de leer lineas de texto en una imagen
                en escala de grises.
        argumento: 
              imgGris: imagen en escala de grises.
        retorno: devuelve la lista de lineas de texto detectadas
        """
        # si el lector no esta inicializado entonces devuleve lista vacia
        if not self.lector:
            return []
        rgb = cv2.cvtColor(imgGris, cv2.COLOR_GRAY2RGB)
        try:
            lineas = self.lector.readtext(rgb, detail=0, allowlist=permitidos)
            lineas_limpias = []
            for l in lineas:
                if l and isinstance(l, str):
                    lineas_limpias.append(alfanumericos(l))
            return lineas_limpias
        except Exception as e:
            logger.debug(f"OCR fallo en variante: {e}")
            return []

    def extraerCandidatos(self, lineas: list[str]) -> list[str]:
        """
        Funcion: metodo que extrae posibles placas de 
                 una lista de lineas de texto.
        argumento: 
            lineas: recibe una lista de cadenas de texto de las cuales se obtienen posibles placas
        
        retorno: devuelve una lista de placas encontradas.             
        """
        texto_completo = ' '.join(lineas)
        texto_completo = alfanumericos(texto_completo)
        if not texto_completo:
            return []

        candidatos: set[str] = set()

        # iterar sobre las expresiones regulares para encontrar coincidencias
        for patron in exprecionesRegulares:
            for coincidencia in patron.finditer(texto_completo):
                candidatos.add(normalizarCoincidencia(coincidencia.group(0)))

        # buscamos tokens individuales que puedan ser placas
        tokens = [t for t in re.split(r'[\s-]+', texto_completo) if t]
        for token in tokens:
            token_limpio = re.sub(r'[^A-Z0-9]', '', token)
            if 5 <= len(token_limpio) <= 10 and re.search('[A-Z]', token_limpio) and re.search(r'\d', token_limpio):
                candidatos.add(normalizarCoincidencia(token_limpio))

        return list(candidatos)

    def elegirMejor(self, candidatos: list[str]) -> str | None:
        """
        Funcion: este metodo selecciona el mejor candidato de placa, tomando en cuenta
                 la puntuacion y longitud
        Argumento: 
             candidatos: recibe una lista de cadenas de texto que con posibles placas

        retorno: retorna la mejor placa o none si no hay candidatos      
        """
        if not candidatos:
            return None
        
        # ordenamos los candidatos en orden descendente por puntuacion y longitud
        for i in range(len(candidatos)):
            for j in range(i + 1, len(candidatos)):
                puntosI = puntuar(candidatos[i])
                longitudI = len(candidatos[i])
                puntosJ = puntuar(candidatos[j])
                longitudJ = len(candidatos[j])

                if (puntosJ > puntosI) or (puntosJ == puntosI and longitudJ > longitudI):
                    candidatos[i], candidatos[j] = candidatos[j], candidatos[i]

        return candidatos[0] 

    def procesarPlaca(self, imagenPlaca: np.ndarray) -> str:
        """
        funcion: metodo principal que se encarga de procesar una img de placa
                 y devuelve el texto de la misma.
        Argumento: 
            imagenPlaca: recibe la img de la placa en formato array.
        Retorna: devolvemos una cadena de texto con la placa 
        """
        if not self.lector:
            return "OCR NO INICIALIZADO"
        try:
            variantesImg = self.variantes(imagenPlaca)
            candidatos: set[str] = set()
            # recorremos las variantes de la img para extraer lineas y los candidatos
            for i, variante in enumerate(variantesImg):
                lineas = self.leerLineas(variante)
                if not lineas:
                    continue
                candidatosVariante = self.extraerCandidatos(lineas)
                candidatos.update(candidatosVariante)

            # intento con la imagen completa en color si no encontro candidatos
            try:
                rgbCompleta = cv2.cvtColor(imagenPlaca, cv2.COLOR_BGR2RGB) if imagenPlaca.ndim == 3 \
                           else cv2.cvtColor(imagenPlaca, cv2.COLOR_GRAY2RGB)
                lineasCompletas = self.lector.readtext(rgbCompleta, detail=0, allowlist=permitidos)
                lineas_limpias = []
                for l in lineasCompletas:
                    if l:
                        lineas_limpias.append(alfanumericos(l))
                lineasCompletas = lineas_limpias
                candidatos.update(self.extraerCandidatos(lineasCompletas))
            except Exception:
                pass

            if not candidatos:
                return "NO TEXTO"

            mejor_candidato = self.elegirMejor(list(candidatos))
            logger.info(f"Placa final: {mejor_candidato}")
            return mejor_candidato or "NO TEXTO"
        except Exception as e:
            logger.error(f"Error OCR: {e}", exc_info=True)
            return "ERROR OCR"

instanciaOcr = None

def obtenerProcesadorOcr():
    """
    Funcion: metodo para obtener una unica instancia del procesador ocr, 
            esto para evitar cargar modelos en memoria varias veces ya que es pesado
    argumento: ninguno
    retorno: devuelve la instancia unica del procesador ocr        
    """
    global instanciaOcr
    if instanciaOcr is None:
        instanciaOcr = ProcesarOCR()
    return instanciaOcr