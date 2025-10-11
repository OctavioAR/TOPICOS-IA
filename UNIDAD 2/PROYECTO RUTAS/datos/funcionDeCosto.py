import numpy as np
from typing import List

# definimos variable solucion como una lista de rutas
Solucion = List[List[int]]

def calcularCosto(
    solucion: Solucion,
    matrizDistancia: np.ndarray,
    matrizCosto: np.ndarray
) -> float:
    # calcula el costo total (FO) para la solucion dada
    # Costo = suma de (Distancia * CostoCombustible) para cada tramo (i a j)

    # inicializamos costo total
    costoTotal = 0.0
    
    # iterar sobre cada ruta en la solucion
    for ruta in solucion:
        # Una ruta valida debe tener al menos: CD -> Tienda X -> CD
        if len(ruta) < 2:
            continue

        # iterar sobre todos los tramos (i a j) de la ruta
        for i in range(len(ruta) - 1):
            nodo_inicio = ruta[i]
            nodo_fin = ruta[i+1]

            # las matrices estan indexadas por los nodos
            distancia = matrizDistancia[nodo_inicio, nodo_fin]
            costoGasolina = matrizCosto[nodo_inicio, nodo_fin]

            # el costo de este tramo es Distancia * Costo por unidad de distancia
            costoTotal += distancia * costoGasolina
        
    return costoTotal