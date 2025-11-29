from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image
import io
import cv2
import numpy as np
import logging
# importamos los modulos y servicios 
from app.modelos.modeloYolo import DetectorPlacas
from app.servicios.servicioOcr import obtenerProcesadorOcr
from app.servicios.servicioFirebase import FirebaseService
# config del logger para mostrar info en consola
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
# inicializamos la app de fastapi
app = FastAPI(
    title="API placas vehiculares",
    description="proyecto topicos IA",
    version="2.0.0"
)
# configuracion CORS para dar acceso desde cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

detector = DetectorPlacas()
servicioOcr = None
servicioFirebase = FirebaseService()

# endpoints de la API
@app.on_event("startup")
async def startup_event():
    """
    Funcion: se ejecuta al inciar el servidor para mostrar los estados 
            de los servicios y cargar los modelos necesarios        
    """
    try:
        logger.info("Iniciando servidor...")

        detector.cargarModelo()
        logger.info("Modelo YOLO cargado correctamente")

        global servicioOcr
        servicioOcr = obtenerProcesadorOcr()
        logger.info("OCR inicializado correctamente")
        
        if servicioFirebase.db:
            logger.info("Firebase conectado correctamente")
        else:
            logger.warning("Firebase no disponible")
        
        logger.info("Servidor listo para recibir peticiones")
        
    except Exception as e:
        logger.error(f"Error al iniciar el servidor: {e}", exc_info=True)
        raise

@app.post("/detectar-placa")
async def detectar_placa(imagen: UploadFile = File(...)):
    """
    Funcion: este es el endpoint principal el cual por medio de la peticion
            POST recibe una img y la procesa para detectar placas vehiculares
            extrallendo su texto con el ocr y consultando la BD.
    """
    try:
        # validamos que el archivo recivido sea valido
        if not imagen.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="El archivo debe ser una imagen (JPEG, PNG, etc.)"
            )
        
        logger.info(f"Procesando imagen: {imagen.filename} ({imagen.content_type})")
        # leemos la img y convertimos a formato openCV
        contenido = await imagen.read()
        imagen_pil = Image.open(io.BytesIO(contenido)).convert('RGB')
        imagen_np = np.array(imagen_pil)
        imagen_cv = cv2.cvtColor(imagen_np, cv2.COLOR_RGB2BGR)
        
        logger.info(f"Tamaño imagen: {imagen_cv.shape}")
        # mandamos a llamar a la funcion detectar placa de YOLO 
        detecciones = detector.detectar(imagen_cv)
        # en caso de no detectar placa retornamos mensaje
        if not detecciones or len(detecciones) == 0:
            logger.warning("No se detectaron placas en la imagen")
            return JSONResponse(
                status_code=200,
                content={
                    "estado": "no_detectado",
                    "mensaje": "No se detectaron placas vehiculares en la imagen",
                    "sugerencias": [
                        "Asegurate de que la placa sea visible",
                        "Mejora la iluminacion",
                        "Acerca mas la camara a la placa"
                    ]
                }
            )
        
        logger.info(f"Detectadas {len(detecciones)} placa(s)")
        
        # lista de todas las detecciones procesadas
        todasDetecciones = []
        
        # iteramos sobre cada deteccion encontrada
        for i, deteccion in enumerate(detecciones):
            try:
                # optenemos coordenads y confianza
                x1, y1, x2, y2 = map(int, deteccion['bbox'])
                confianzaDeteccion = float(deteccion.get('confidence', 0.0))
                
                logger.info(f"Procesando deteccion {i+1}: bbox={[x1,y1,x2,y2]}, conf={confianzaDeteccion:.2f}")
                
                placaRegion = imagen_cv[y1:y2, x1:x2]
                
                textoPlacaOcr = "ERROR OCR"
                if servicioOcr:
                    try:
                        # realizamos el ocr en la region de la placa detectada
                        textoPlacaOcr = servicioOcr.procesarPlaca(placaRegion)
                        logger.info(f"OCR extraido: '{textoPlacaOcr}'")
                    except Exception as e:
                        logger.error(f"Error en OCR: {e}", exc_info=True)
                else:
                    logger.warning("OCR no disponible")
                
                placaFinal = textoPlacaOcr
                datosVehiculo = None
                corregidoBD = False
                busqueda = "ocr_directo"
                
                # intentar corregir la placa usando la BD de firebase
                if textoPlacaOcr and textoPlacaOcr not in ["ERROR OCR", "NO TEXTO", "NO FORMATO"]:
                    try:
                        datosVehiculo = servicioFirebase.buscarVehiculo(textoPlacaOcr)
                        
                        if datosVehiculo:
                            placa_real = datosVehiculo.get('matricula') or datosVehiculo.get('documento_id')
                            
                            if placa_real and placa_real != textoPlacaOcr:
                                placaFinal = placa_real
                                corregidoBD = True
                                busqueda = "similitud"
                                
                                similitud = datosVehiculo.get('_similitud', 0)
                                logger.info(
                                    f"Placa corregida: '{textoPlacaOcr}' - '{placaFinal}' "
                                    f"(similitud: {similitud*100:.1f}%)"
                                )
                            else:
                                placaFinal = placa_real or textoPlacaOcr
                                busqueda = "exacta"
                                logger.info(f"Placa exacta encontrada: '{placaFinal}'")
                        else:
                            logger.warning(f"Placa '{textoPlacaOcr}' no encontrada en Firebase")
                            
                    except Exception as e:
                        logger.error(f"Error consultando Firebase: {e}", exc_info=True)
                # resultados de la deteccion actual
                deteccionResultado = {
                    "placa_ocr_original": textoPlacaOcr,
                    "placa_final": placaFinal,
                    "confianza_deteccion": round(confianzaDeteccion, 4),
                    "bbox": [x1, y1, x2, y2],
                    "indice": i,
                    "corregido_por_db": corregidoBD,
                    "metodo_busqueda": busqueda
                }
                
                if datosVehiculo:
                    datos_limpios = {
                        k: v for k, v in datosVehiculo.items()
                        if not k.startswith('_')
                    }
                    deteccionResultado["datos_vehiculo"] = datos_limpios
                
                todasDetecciones.append(deteccionResultado)
                logger.info(f"Deteccion {i+1} procesada exitosamente")
                
            except Exception as e:
                logger.error(f"Error procesando deteccion {i+1}: {e}", exc_info=True)
                continue
        
        if not todasDetecciones:
            return JSONResponse(
                status_code=200,
                content={
                    "estado": "error",
                    "mensaje": "No se pudo procesar ninguna deteccion valida",
                    "detalle": "Todas las detecciones fallaron en el procesamiento"
                }
            )
        
        mejor_deteccion = max(
            todasDetecciones,
            key=lambda x: (
                1 if x.get('datos_vehiculo') else 0,
                x['confianza_deteccion']
            )
        )
        
        logger.info(f"Mejor deteccion: {mejor_deteccion['placa_final']}")
        # retornamos la mejor deteccion encontrada en formato JSON
        return JSONResponse(
            status_code=200,
            content={
                "estado": "exito",
                "placa": mejor_deteccion['placa_final'],
                "confianza": mejor_deteccion['confianza_deteccion'],
                "bbox": mejor_deteccion['bbox'],
                "corregido": mejor_deteccion['corregido_por_db'],
                "metodo": mejor_deteccion['metodo_busqueda'],
                "placa_ocr": mejor_deteccion['placa_ocr_original'],
                "datos_vehiculo": mejor_deteccion.get('datos_vehiculo'),
                "todas_detecciones": todasDetecciones,
                "total_detecciones": len(todasDetecciones)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error critico procesando imagen: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "estado": "error",
                "mensaje": "Error interno del servidor",
                "detalle": str(e),
                "tipo_error": type(e).__name__
            }
        )
# inicio del servidor 
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )