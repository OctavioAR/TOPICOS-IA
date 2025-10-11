import random
import numpy as np
from typing import List, Tuple
from funcionDeCosto import Solucion
from distancia import cdCercano 

# definimos numero de nodos, CD y tiendas
num_nodos = 100
num_CDS = 10
num_tiendas = 90

# funcion para crear una solucion inicial
def solucionInicial(matriz_distancia: np.ndarray) -> Solucion:

    # crea una solucion inicial asignando cada tienda a su CD mas cercano
    # separar indices de CDs y tiendas
    indices_cds = list(range(num_CDS))
    indices_tiendas = list(range(num_CDS, num_nodos))
    
    # crea una lista de listas para las rutas una para cada CD
    solucion = [[] for _ in indices_cds]
    
    # asignar cada tienda a su CD mas cercano
    for tienda_idx in indices_tiendas:
        #funcion que encuentra el CD mas cercano a la tienda
        cd_cercano = cdCercano(tienda_idx, matriz_distancia, indices_cds)
        solucion[cd_cercano].append(tienda_idx)
        
    # formatear la solucion final: [CD, tienda1, tienda2, ..., CD]
    rutas_finales = []
    for i, tiendas_asignadas in enumerate(solucion):
        # cada ruta inicia y termina en el CD
        ruta = [i] + tiendas_asignadas + [i]
        rutas_finales.append(ruta)
        
    return rutas_finales

def generarVecinos(solucionActual: Solucion, matrizDistancia: np.ndarray) -> Solucion:
    # generar una solucion vecina haciendo un swap de dos tiendas en una ruta aleatoria

    nuevaSolucion = [list(ruta) for ruta in solucionActual] # copia de la solucion actual
    
    # seleccionar una ruta aleatoria
    indiceRuta = random.randint(0, num_CDS - 1) 
    ruta = nuevaSolucion[indiceRuta]
    
    # Una ruta debe tener al menos 2 tiendas para poder intercambiar y minimo 4 nodos: CD, T1, T2, CD
    if len(ruta) < 4:
        return nuevaSolucion # devuelve la misma solucion si no hay tiendas para mover
        
    # seleccionar dos indices de tienda para intercambiar
    # excluimos el CD inicial y el final 
    swap = random.sample(range(1, len(ruta) - 1), 2)
    idx1, idx2 = swap[0], swap[1]
    
    # realizar el intercambio 
    ruta[idx1], ruta[idx2] = ruta[idx2], ruta[idx1]
    # retornar la nueva solucion vecina
    return nuevaSolucion