import math
import random
from typing import List, Tuple
import numpy as np

from funcionDeCosto import calcularCosto, Solucion
from solucion import solucionInicial, generarVecinos

def recocidoSimulado(
    matrizDistancia: np.ndarray,
    matrizCosto: np.ndarray,
    T0: float = 100.0,              # Temperatura inicial
    TF: float = 0.1,                # Temperatura final 
    alpha: float = 0.95,            # Factor de enfriamiento
    L: int = 200                    # Iteraciones por temperatura
) -> Tuple[Solucion, float, List[float]]:
    
    # inicializacion de la solucion y calculo de su costo
    solucionActual = solucionInicial(matrizDistancia)
    costoActual = calcularCosto(solucionActual, matrizDistancia, matrizCosto)
    
    # guardar la mejor solucion encontrada y su costo
    mejorSolucion = [list(ruta) for ruta in solucionActual]
    mejorCosto = costoActual 
    
    T = T0  # temperatura actual
    historialCosto = [costoActual]
    ciclo_temp = 0 # contador para los ciclos de enfriamiento
    
    # impresion inicial
    print(f"Temperatura inicial: {T0}, Factor de enfriamiento: {alpha}")
    print(f"Costo de la solución inicial: ${costoActual:,.2f} MXN")
    
    print("\n| Ciclo | Temperatura | Costo Actual | Mejor Costo |")
    print("|-------|-------------|--------------|-------------|")
    print(f"| {ciclo_temp:^5} | {T:11.4f} | ${costoActual:^8.2f} | ${mejorCosto:^7.2f} |")
    
    # bucle principal del recocido como criterio de parada la temperatura final 
    while T > TF:
        ciclo_temp += 1
        
        for _ in range(L):  # realiza L iteraciones a esta temperatura
            
            #generamos vecino y evaluamos su costo
            nuevaSolucion = generarVecinos(solucionActual, matrizDistancia)
            nuevoCosto = calcularCosto(nuevaSolucion, matrizDistancia, matrizCosto)
            
            # diferencia de costo entre la nueva solucion y la actual
            delta = nuevoCosto - costoActual
            
            # criterio de aceptacion
            if delta < 0:
                solucionActual = nuevaSolucion
                costoActual = nuevoCosto
            else:
                # se acepta con probabilidad de aceptacion si es peor
                probabilidad_aceptacion = math.exp(-delta / T)
                if random.random() < probabilidad_aceptacion:
                    solucionActual = nuevaSolucion
                    costoActual = nuevoCosto
            
            # actualiza la mejor solucion global
            if costoActual < mejorCosto:
                mejorSolucion = [list(ruta) for ruta in solucionActual]
                mejorCosto = costoActual
            
            historialCosto.append(costoActual)
        
        # enfriamiento geometrico
        T *= alpha
    
        print(f"| {ciclo_temp:^5} | {T:11.4f} | ${costoActual:^8.2f} | ${mejorCosto:^7.2f} |")
    # retornamos la mejor solucion encontrada y su costo
    return mejorSolucion, mejorCosto, historialCosto