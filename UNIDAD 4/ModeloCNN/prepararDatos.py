import pandas as pd
import os
from pathlib import Path

base_dir = Path(__file__).resolve().parent

rutaDataset = base_dir / "imagenes placas"
 
rutasCsv = {
    'train': base_dir / 'trainCSV.csv',
    'valid': base_dir / 'validCSV.csv',
    'test': base_dir / 'testCSV.csv',
}

def formatoYolo(fila):

    """
    Funcion: convertir las coordernadas al formato especifico de Yolo tipo
             x_centro, y_centro, etc.
    Parametros:
        fila: recibe una fita de DF con las coordenadas en formato Pascal VOC
    Retorno: 
        una serie con las coordenadas en formato requerido para Yolo.
    """

    # extraer las coorde
    ancho_imagen = fila['ancho_imagen']
    altura_imagen = fila['altura_imagen']
    x_min = fila['x_min']
    y_min = fila['y_min']
    x_max = fila['x_max']
    y_max = fila['y_max']
 
    x_centro_px = (x_min + x_max) / 2
    y_centro_px = (y_min + y_max) / 2
    ancho_caja_px = x_max - x_min
    altura_caja_px = y_max - y_min
    # normalizar las cordes
    x_centro_norm = x_centro_px / ancho_imagen if ancho_imagen > 0 else 0
    y_centro_norm = y_centro_px / altura_imagen if altura_imagen > 0 else 0
    ancho_norm = ancho_caja_px / ancho_imagen if ancho_imagen > 0 else 0
    altura_norm = altura_caja_px / altura_imagen if altura_imagen > 0 else 0

    # 0 para la clase placa
    indiceClase = 0

    return pd.Series([indiceClase, x_centro_norm, y_centro_norm, ancho_norm, altura_norm])

def genaerarArchivos():
    
    """
    Funcion: esta fuincion se encarga de generar los archivos de anotaciones para
            el modelo de Yolo, a partir de los archivo csv.
    Parametros: no recibe ninguno.
    Retorno: no retorna nada, solo genera los archivos en las carpetas donde van.

    """

    print(f"Directorio base: {base_dir}")
    for division, ruta_csv in rutasCsv.items():
        print(f"\nProcesando división: {division} ({ruta_csv})...")
        
        if not ruta_csv.exists():
            print(f"ERROR: El archivo '{ruta_csv}' no se encuentara")
            alternativas = list(base_dir.glob(f"*{division}*.csv"))
            if alternativas:
                print(f"  Archivos CSV encontrados: {[p.name for p in alternativas]}")
            continue
        
        df_actual = pd.read_csv(ruta_csv)
        df_actual.columns = ['nombre_archivo', 'ancho_imagen', 'altura_imagen', 'clase', 'x_min', 'y_min', 'x_max', 'y_max']
        
        columnas_yolo = ['indice_clase', 'x_centro', 'y_centro', 'ancho_norm', 'altura_norm']
        df_yolo = df_actual.apply(formatoYolo, axis=1)
        df_yolo.columns = columnas_yolo
        df_anotaciones = pd.concat([df_actual[['nombre_archivo']], df_yolo], axis=1)
        
        # creamos la carpeta de salida labels
        ruta_carpeta_labels = rutaDataset / division / "labels"
        ruta_carpeta_labels.mkdir(parents=True, exist_ok=True)
        print(f"Ruta de destino: {ruta_carpeta_labels}")
        
        # genera los archivos .txt con las anotaciones
        contadorArchivos = 0
        for i, fila in df_anotaciones.iterrows():
            nombre_base = Path(fila['nombre_archivo']).stem
            
            linea_anotacion = (
                f"{int(fila['indice_clase'])} "
                f"{fila['x_centro']:.6f} "
                f"{fila['y_centro']:.6f} "
                f"{fila['ancho_norm']:.6f} "
                f"{fila['altura_norm']:.6f}"
            )

            # escribir las anotaciones en el archivo txt
            ruta_archivo_txt = ruta_carpeta_labels / f"{nombre_base}.txt"
            with open(ruta_archivo_txt, 'w') as f:
                f.write(linea_anotacion)
            contadorArchivos += 1

        print(f"Generados {contadorArchivos} archivos .txt en {ruta_carpeta_labels}")

if __name__ == "__main__":
    genaerarArchivos()