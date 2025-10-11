import pandas as pd
import numpy as np
from distancia import generarMatrizDistancias 
from typing import List, Tuple

# funcion para cargar datos desde archivos CSV
def cargarDatos(
    coordArchivo: str, 
    matrizDistancia: str, 
    matrizGasolina: str
    ) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]: # (coordenadas, distancia, costo)
    # proceso de carga dentro de un bloque try-except para manejo de errores
    try:
        # cargar coordenadas
        coordenadas = pd.read_csv(coordArchivo, encoding='latin1')       
        print(f"{len(coordenadas)} nodos cargados")
        
        # generar la matriz de distancia usando la formula HAVERSINE
        distancia = generarMatrizDistancias(coordenadas)
        
        # cargar la matriz de costos de combustible
        costo = pd.read_csv(matrizGasolina, encoding='latin1').values
        costo = costo.astype(float)
        print(f"Matriz de Costo {costo.shape} cargada")
        
        print("Datos cargados correctamente.")
        # devolver los datos cargados
        return coordenadas, distancia, costo
        
    except FileNotFoundError as fnfe:
        print(f"error verificar que los archivos esten en la carpeta datos {fnfe}")
        raise
    except Exception as e:
        print(f"Error al cargar o recalcular datos: {e}")
        raise