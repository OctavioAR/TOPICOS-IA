import numpy as np
import pandas as pd
from typing import Tuple

# radio de la tierra en km
radioTierra = 6371.0

# funcion para calcular la distancia entre dos puntos usando la formula de Haversine
def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:

    # calcula la distancia entre dos puntos lat y lon en KM

    # convertir grados a radianes
    lat1_rad = np.radians(lat1)
    lon1_rad = np.radians(lon1)
    lat2_rad = np.radians(lat2)
    lon2_rad = np.radians(lon2)

    # diferencias de coordenadas
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    # formula de Haversine
    a = np.sin(dlat / 2.0)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2.0)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    # distancia en kilometros
    distance_km = radioTierra * c
    
    # retorna la distancia en km
    return distance_km

# funcion para generar la matriz de distancias entre todos los nodos
def generarMatrizDistancias(coordenadas: pd.DataFrame) -> np.ndarray:

    # genera la matriz de distancias usando la formula de haversine
    n = len(coordenadas)
    matriz_haversine = np.zeros((n, n))
    
    # extraer las coordenadas como arrays para un acceso mas rapido
    lats = coordenadas['Latitud_WGS84'].values
    lons = coordenadas['Longitud_WGS84'].values
    
    # llenar la matriz en forma de vector 
    for i in range(n):
        matriz_haversine[i, :] = haversine(lats[i], lons[i], lats, lons)

    # retornar la matriz de distancias    
    return matriz_haversine

# funcion para encontrar CD mas cercano a una tienda
def cdCercano(tienda_idx: int, matriz_distancia: np.ndarray, cds_indices: list) -> int:
    # encuentra el indice del CD mas cercano a la tienda dada

    # extrae las distancias desde la tienda a todos los CDs
    distancias_a_cds = matriz_distancia[tienda_idx, cds_indices]
    
    # encuentra el indice del CD con la distancia minima
    cd_mas_cercano_idx_local = np.argmin(distancias_a_cds)
    
    # devuelve el indice global del CD
    return cds_indices[cd_mas_cercano_idx_local]