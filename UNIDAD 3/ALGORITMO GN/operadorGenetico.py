import random
import pandas as pd
import numpy as np
import operator
from aptitud import Aptitud

def crearRuta(listaMunicipios):
    """
        Funcion: Crea una ruta aleatoria a partir de una lista de municipios.

        Argumento:
            listaMunicipios: Lista de objetos 'municipio'.
        
        Retorna:
            Una lista que representa una ruta aleatoria.
    """
    # con random.sample creamos municipios aleatorios de la lista de municipios
    return random.sample(listaMunicipios, len(listaMunicipios))

def poblacionInicial(tamanoPob, listaMunicipios):
    """
        Funcion: Crea una poblacion inicial de rutas.

        Argumento:
            tamanoPob: El tamano de la poblacion.
            listaMunicipios: Lista de objetos 'municipio'.
        
        Retorna:
            Una lista de rutas que representa la poblacion inicial.
    """
    poblacion = []
    # crea rutas aleatorias y las añade a la poblacion
    for i in range(0, tamanoPob):
        poblacion.append(crearRuta(listaMunicipios))
    return poblacion

def clasificacionRutas(poblacion):
    """
        Funcion: Clasifica las rutas en la poblacion segun su aptitud.

        Argumento:
            poblacion: Una lista de rutas.

        Retorna:
            Una lista ordenada de tuplas (indice, aptitud).
    """
    aptitudRutas = {}
    # calcula la aptitud para cada ruta y la almacena con su indice
    for i in range(0, len(poblacion)):
        aptitudRutas[i] = Aptitud(poblacion[i]).rutaApta()
        # ordena el diccionario por el valor de aptitud de forma decendente
    return sorted(aptitudRutas.items(), key=operator.itemgetter(1), reverse=True)

def seleccionRutas(poblacionRanked, numSeleccionados):
    """
        Funcion: Selecciona los individuos para la proxima generacion.

        Argumento:
            poblacionRanked: Una lista ordenada de tuplas (indice, aptitud).
            numSeleccionados: El numero de individuos de elite a seleccionar.
        
        Retorna:
            Una lista de indices de los individuos seleccionados.
    """
    seleccionados = []
    # convierte la lista clasificada en un DF para facilitar los calculos de ruleta
    df = pd.DataFrame(np.array(poblacionRanked), columns=["Indice", "Aptitud"])
    # calcula la suma acumulada de las aptitudes
    df['sumaAcumulada'] = df.Aptitud.cumsum()
    # calcula el porcentaje acumulado para simular la ruleta
    df['porcentajeAcumulado'] = 100 * df.sumaAcumulada / df.Aptitud.sum()

    # Primero se agregan los individuos de elite (los mejores)
    for i in range(0, numSeleccionados):
        seleccionados.append(poblacionRanked[i][0])

    # Segundo se seleccionan los demas por el metodo de la ruleta
    # se selecciona un numero de individuos igual al tamaño de la poblacion menos la elite
    for _ in range(0, len(poblacionRanked) - numSeleccionados):
        umbral = random.random() * 100
        for j in range(len(poblacionRanked)):
            # si el umbral cae dentro del rango de porcentaje del individuo se selcciona
            if umbral <= df.iat[j, 3]:
                seleccionados.append(poblacionRanked[j][0])
                break # sale del bucle para seleccionar al siguiente individuo
    return seleccionados

def grupoApareamiento(poblacion, seleccionados):
    """
        Funcion: Crea un grupo de apareamiento a partir de la poblacion y los resultados de la seleccion.

        Argumento:
            poblacion: La poblacion actual de rutas.
            resultadosSeleccion: Los indices de las rutas seleccionadas.
        
        Retorna:
            Una lista de rutas para el apareamiento.
    """
    padres = []
    # utiliza los indices seleccionados para obtener las rutas de la poblacion
    for indice in seleccionados:
        padres.append(poblacion[indice]) 
    return padres

def cruce(progenitor1, progenitor2):

    """
        Funcion: Realiza el cruce de un punto ordenado entre dos progenitores.

        Argumento:
            progenitor1: La primera ruta progenitora.
            progenitor2: La segunda ruta progenitora.
        
        Retorna:
            Una nueva ruta hija.
    """
    hijo = []
    hijoP1 = []
    hijoP2 = []
    # elige dos puntos de corte aleatorios
    genA = int(random.random() * len(progenitor1))
    genB = int(random.random() * len(progenitor1))

    genInicial = min(genA, genB)
    genFinal = max(genA, genB)
    # el segmento central se toma del progenitor 1
    for i in range(genInicial, genFinal):
        hijoP1.append(progenitor1[i])
    # se toman los genes restantes del progenitor 2
    hijoP2 = [item for item in progenitor2 if item not in hijoP1]
    # combina el segmento del progenitor 1 y los genes del progenitor 2
    hijo = hijoP1 + hijoP2
    return hijo

def crucePoblacion(grupoApareamiento, indivSelecionados):
    """
        Funcion: Crea una nueva poblacion a traves de la reproduccion.

        Argumento:
            grupoApareamiento: El grupo de rutas para apareamiento.
            indivSelecionados: El numero de individuos de elite.
        
        Retorna:
            Una nueva poblacion de rutas hijas.
    """
    hijos = []
    # La cantidad de hijos a crear por cruce es el tamaño del grupo menos la elite
    tamano_no_elite = len(grupoApareamiento) - indivSelecionados
    espacio = random.sample(grupoApareamiento, len(grupoApareamiento))

    # Se preservan los individuos de elite para la siguiente generacion
    for i in range(0,indivSelecionados):
        hijos.append(grupoApareamiento[i])
    
    # Se cruzan los demas para completar la poblacion
    for i in range(0, tamano_no_elite):
        hijo = cruce(espacio[i], espacio[len(grupoApareamiento)-i-1])
        hijos.append(hijo)
    return hijos

def mutacion(individuo, tasaMutacion):
    """
        Funcion: Realiza una mutacion de intercambio en un individuo.

        Argumento:
            individuo: La ruta a mutar.
            tasaMutacion: La probabilidad de mutacion.
        
        Retorna:
            La ruta mutada.
    """
    # Itera sobre cada gen (ciudad) de la ruta
    for indiceCiudad in range(len(individuo)):
        # si el numero aleatorio es menor que la tasa de mutacion, se aplica la mutacion
        if random.random() < tasaMutacion:
            # elige un segundo punto aleatorio para el intercambio
            indiceCiudad2 = int(random.random() * len(individuo))
            # almacena los valores de las ciudades en las dos posiciones
            ciudad1 = individuo[indiceCiudad]
            ciudad2 = individuo[indiceCiudad2]
            # realiza el intercambio de las ciudades mutacion por intercambio
            individuo[indiceCiudad] = ciudad2
            individuo[indiceCiudad2] = ciudad1
    return individuo

def mutacionPoblacion(poblacion, tasaMutacion):
    """
        Funcion: Aplica la mutacion a toda una poblacion.

        Argumento:
            poblacion: La poblacion de rutas.
            tasaMutacion: La probabilidad de mutacion.
        
        Retorna:
            La poblacion mutada.
    """
    poblacionMutada = []
    # aplica la funcion de mutacion a cada individuo de la poblacion
    for i in range(0, len(poblacion)):
        individuoMutado = mutacion(poblacion[i], tasaMutacion)
        poblacionMutada.append(individuoMutado)
    return poblacionMutada