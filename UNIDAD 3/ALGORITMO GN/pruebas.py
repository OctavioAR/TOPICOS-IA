import random
from municipio import municipio
from aptitud import Aptitud
from operadorGenetico import clasificacionRutas

# --- Datos de prueba ---
# usamos un conjunto pequeño de municipios para que los resultados
# de las pruebas sean faciles de verificar
listaMunicipiosPrueba = [
    municipio("A", 0, 0),
    municipio("B", 0, 3),
    municipio("C", 4, 3),
    municipio("D", 4, 0)
]

def pruebaDistanciaMun():
    """Prueba que la distancia entre dos municipios se calcule correctamente"""
    
    print("Iniciando Prueba: Distancia entre municipios")
    mun_a = listaMunicipiosPrueba[0] # (0, 0)
    mun_b = listaMunicipiosPrueba[1] # (0, 3)
    mun_c = listaMunicipiosPrueba[2] # (4, 3)
    
    dist_a_b = mun_a.distancia(mun_b)
    if dist_a_b == 3.0:
        print("PASO: La distancia en el eje Y es correcta (3.0)")
    else:
        print(f"FALLO: La distancia en el eje Y debia ser 3.0, pero fue {dist_a_b}")

    dist_b_c = mun_b.distancia(mun_c)
    if dist_b_c == 4.0:
        print("PASO: La distancia en el eje X es correcta (4.0)")
    else:
        print(f"FALLO: La distancia en el eje X debia ser 4.0, pero fue {dist_b_c}")

    # distancia diagonal (triangulo 3-4-5)
    dist_a_c = mun_a.distancia(mun_c)
    if dist_a_c == 5.0:
        print("PASO: La distancia diagonal es correcta (5.0).")
    else:
        print(f"FALLO: La distancia diagonal debia ser 5.0, pero fue {dist_a_c}")
    print("-" * 50)

def pruebaAptitud():
    """Prueba que la clase Aptitud calcule correctamente la distancia y la aptitud de una ruta"""

    print("Iniciando Prueba: Calculo de Aptitud y Distancia")
    # ruta A -> B -> C -> D -> A
    ruta_simple = [
        listaMunicipiosPrueba[0], # A(0,0)
        listaMunicipiosPrueba[1], # B(0,3)
        listaMunicipiosPrueba[2], # C(4,3)
        listaMunicipiosPrueba[3]  # D(4,0)
    ]
    # distancia esperada: A-B(3) + B-C(4) + C-D(3) + D-A(4) = 14
    distancia_esperada = 14.0
    
    calculador_aptitud = Aptitud(ruta_simple)
    distancia_calculada = calculador_aptitud.distanciaRuta()
    
    if distancia_calculada == distancia_esperada:
        print(f"PASO: La distancia total de la ruta es correcta ({distancia_calculada})")
    else:
        print(f"FALLO: La distancia de la ruta debia ser {distancia_esperada}, pero fue {distancia_calculada}")
    
    aptitud_calculada = calculador_aptitud.rutaApta()
    aptitud_esperada = 1 / distancia_esperada
    
    # usamos una pequeña tolerancia para comparar numeros flotantes
    if abs(aptitud_calculada - aptitud_esperada) < 1e-9:
        print(f"PASO: La aptitud de la ruta es correcta ({aptitud_calculada:.6f})")
    else:
        print(f"FALLO: La aptitud debia ser {aptitud_esperada:.6f}, pero fue {aptitud_calculada:.6f}")
    print("-" * 50)

def pruebaClasificacionRutas():
    """Prueba que las rutas se ordenen correctamente de mayor a menor aptitud"""

    print("Iniciando Prueba: Clasificacion de Rutas")
    # Ruta 1 (corta, alta aptitud): A-B-C-D-A, Distancia = 14
    ruta1 = [listaMunicipiosPrueba[i] for i in [0, 1, 2, 3]]
    # Ruta 2 (larga, baja aptitud): A-C-B-D-A, Distancia = 5 + 4 + 3 + 4 = 16
    ruta2 = [listaMunicipiosPrueba[i] for i in [0, 2, 1, 3]]
    
    poblacion = [ruta2, ruta1] 
    
    clasificacion = clasificacionRutas(poblacion)
    
    # El primer elemento de la clasificacion debe ser el indice de la mejor ruta (indice 1)
    if clasificacion[0][0] == 1:
        print("PASO: La ruta con mayor aptitud fue clasificada primero")
    else:
        print(f"FALLO: Se esperaba que la ruta con indice 1 fuera la mejor, pero fue la de indice {clasificacion[0][0]}")
    print("-" * 50)

if __name__ == '__main__':
    print("== PRUEBAS DEL ALGORITMO GENETICO ==")
    
    pruebaDistanciaMun()
    pruebaAptitud()
    pruebaClasificacionRutas()
    
    print("\nPruebas finalizadas.")