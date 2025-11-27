import os
import logging
from pathlib import Path
from typing import List, Dict, Any

import numpy as np
from ultralytics import YOLO

logger = logging.getLogger(__name__)

class DetectorPlacas:
    """
    Clase que permite cargar el modelo YOLO y poder realizar las detecciones
    de las placas en imagenes.
    """
    def __init__(self, model_path: str | None = None):
        """
        Funcion: metodo constructor de la clase el cual recibe la 
                 ruta del modelo de yolo .
        Argumento: 
            model_path (str | None): Ruta al modelo YOLO. Si es None, 
            se busca en variables de entorno o rutas predeterminadas.
        Retorna: no reotorna nada,
        """
        root = Path(__file__).resolve().parents[2]
        default_model = root / "models" / "best.pt"

        self.model_path = model_path or os.getenv("YOLO_MODEL_PATH") or str(default_model)
        self.model: YOLO | None = None
        self.modelo_cargado = False

    def cargarModelo(self) -> None:
        """
        Funcion: se encarga de cargar el modelo de yolo desde la ruta que se 
                 especifico en el constructor.
        Argumentos: no recibe argumentos.
        Retorno: no retorna nada.
        """
        # manejo de errores
        try: 
            ruta = Path(self.model_path)
            if not ruta.exists():
                raise FileNotFoundError(f"Modelo no encontrado en: {ruta}")
            logger.info(f"Cargando modelo YOLO desde: {ruta}")
            # cargamos el modelo YOLO
            self.model = YOLO(str(ruta))
            self.modelo_cargado = True
            logger.info("Modelo YOLO cargado correctamente")
        except Exception as e:
            logger.error(f"Error cargando modelo: {e}")
            raise

    def detectar(self, imagen: np.ndarray, nivelConfianza: float = 0.5) -> List[Dict[str, Any]]:
        """
        Funcion: el metodo realiza la deteccion de las placas en la imagen 
                recibida como arguemto.
        Argumentos: 
            imagen np.ndarray: imagen en formato de array para realizar la detccion.
            nivelConfianza float: variable que tiene el porcentaje de confianza de la deteccion.
        Retorno: retorna una lista de direcciones con las detecciones realizadas.
        """
        # validar que el modelo fue cargado correctamente
        if not self.modelo_cargado or self.model is None:
            raise RuntimeError("Modelo no cargado. Llama a cargarModelo")
        
        try:
            resultados = self.model(imagen, conf=nivelConfianza)
            detecciones: List[Dict[str, Any]] = []
            # iteramos sobre los resultados para extraer las cajas detectada
            for i in resultados:
                boxes = getattr(i, "boxes", None)
                if boxes is None:
                    continue
                # iteramos sobre las cajas detectadas y extraemos la informacion
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    confianza = float(box.conf[0].item())
                    clase = int(box.cls[0].item())
                    detecciones.append({
                        "bbox": [x1, y1, x2, y2],
                        "confidence": confianza,
                        "class": clase
                    })

            logger.info(f"{len(detecciones)} detecciones")
            return detecciones
        except Exception as e:
            logger.error(f"Error en detección YOLO: {e}")
            return []
        
    # funcion para verificar si el modelo fue cargado
    def esta_cargado(self) -> bool:
        return self.modelo_cargado
    
detector = DetectorPlacas()