import os
from pathlib import Path
from ultralytics import YOLO 

base_dir = Path(__file__).resolve().parent

rutaDataset = base_dir / "imagenes placas"
nomArchivoYaml = base_dir / "configuracion_datos.yaml"

listaClases = ['placas']

def generarArchivoYaml():
    """
    Funcion: funcion para verificar la estructura del dataset y
            poder generar el archivo de configuracion YAML para YOLOv8.
    Argumentos: no recibe argumentos.
    Retorna: no retorna nada, pero crea el archivo YAML.
    """
    # dividir el dataset en train valid y test
    for dividir in ['train', 'valid', 'test']:
        direcDividido = rutaDataset / dividir
        direcImg = direcDividido / 'images'
        direcEtiquetas = direcDividido / 'labels'
        # verificar si existen las carpetas
        if not direcImg.exists():
            raise FileNotFoundError(f"No existe carpeta de imagenes: {direcImg}")
        if not direcEtiquetas.exists():
            raise FileNotFoundError(f"No existe carpeta de etiquetas: {direcEtiquetas}")
        
        # verificar si las carpetas contienen archivos
        imagenes = list(direcImg.glob("*.jpg")) + list(direcImg.glob("*.png"))
        etiquetas = list(direcEtiquetas.glob("*.txt"))
        print(f"{dividir}: {len(imagenes)} imagenes, {len(etiquetas)} etiquetas")
        
        if len(imagenes) == 0 or len(etiquetas) == 0:
            raise FileNotFoundError(f"Faltan archivos en {direcDividido}")
    # generar el archivo YAML
    contenidoYaml = f"""# Archivo de configuracion de datos para YOLOv8
    path: {rutaDataset.as_posix()}

    # Rutas relativas a 'path'
    train: train/images
    val: valid/images
    test: test/images

    # Definición de clases
    nc: {len(listaClases)}
    names: {listaClases}
    """
    # abir y escribir el archivo Yaml para el entrenamiento
    with open(nomArchivoYaml, 'w') as archivo:
        archivo.write(contenidoYaml)
    print(f"Archivo de configuración generado: {nomArchivoYaml}")

def entrenarModelo():

    """
    Funcion: esta funcion se encarga de entrenar el modelo Yolo utilizando
            el dataset que configuro la funcion generarArchivoYaml. Ademas, exportamos 
            el modelo entrenado best.pt
    Argumento: no recibe ningun argumento.
    Retorno: no retorna nada, pero guarda el modelo entrenado en la carpeta runs.
    """

    nombreModelo = 'yolov8n.pt'
    rutaModelo = base_dir / nombreModelo
    
    print(f"Cargando modelo base: {nombreModelo}...")
    modeloYolo = YOLO(nombreModelo) 
    
    if not rutaModelo.exists():
        modeloDefault = Path.home() / '.cache' / 'ultralytics' / nombreModelo
        if modeloDefault.exists():
            import shutil
            shutil.copy2(modeloDefault, rutaModelo)
            print(f"Modelo copiado a: {rutaModelo}")

    print("Inicio de entrenamiento del modelo")
    
    dirModelo = base_dir / 'runs' / 'detect'

    # parametros de entrenamiento del modelo CNN
    modeloYolo.train(
        data=str(nomArchivoYaml),
        epochs=35,                      # numero de epocas
        imgsz=640,                      # tamaño de imagenes
        project=str(dirModelo),         # carpeta de guardado
        name='entrenamiento_placas',
        exist_ok=True                   # sobrescribir el directorio
    )
    
    rutaModelo = dirModelo / 'entrenamiento_placas' / 'weights' / 'best.pt'

if __name__ == "__main__":
    generarArchivoYaml()
    entrenarModelo()
    print("\nEntrenamiento y exportacion completados.")