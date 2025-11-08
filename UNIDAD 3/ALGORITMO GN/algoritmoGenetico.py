from operadorGenetico import (
    poblacionInicial, 
    clasificacionRutas, 
    seleccionRutas, 
    grupoApareamiento, 
    crucePoblacion, 
    mutacionPoblacion)

def siguienteGeneracion(generacionActual, indivSeleccionados, razonMutacion):
    """
        Funcion: Realiza el proceso para las siguientes generaciones.
 
        Argumentos:
            generacionActual (list): La poblacion actual de rutas.
            indivSeleccionados (int): El numero de individuos de elite a preservar.
            razonMutacion (float): La probabilidad de mutacion para cada individuo.
        Retorna:
            Una nueva poblacion (generacion) de rutas.
    """
    # clasificar rutas
    poblacionClasificada = clasificacionRutas(generacionActual)
    # seleccion de los candidatos
    resultadosSeleccion = seleccionRutas(poblacionClasificada, indivSeleccionados)
    # generar grupo de apareamiento
    grupoApareamientoRutas = grupoApareamiento(generacionActual, resultadosSeleccion)
    # generar nueva poblacion
    hijos = crucePoblacion(grupoApareamientoRutas, indivSeleccionados)
    # aplicar mutacion
    nuevaGeneracion = mutacionPoblacion(hijos, razonMutacion)
    
    return nuevaGeneracion

def algoritmoGenetico(municipios, tampoblacion, indivSeleccionados, razonMutacion, generaciones, verbose):
    """
        Funcion: Ejecuta el algoritmo genetico para resolver el problema del agente viajero.

        Argumentos:
            municipios (list): Lista de objetos 'municipio' a visitar.
            tampoblacion (int): El tamaño de la poblacion.
            indivSeleccionados (int): El numero de individuos de elite que pasan a la siguiente generacion.
            razonMutacion (float): La tasa de mutacion.
            generaciones (int): El numero de generaciones a ejecutar.
            verbose (bool): Si es True, imprime el progreso durante la ejecucion.

        Retorna:
            Una tupla con la mejor ruta encontrada y su distancia total.
    """
    # se crea la poblacion inicial de manera aleatoria
    poblacion = poblacionInicial(tampoblacion, municipios)

    # se calcula la distancia de la mejor ruta en la poblacion inicial
    mejorAptitudInicial = clasificacionRutas(poblacion)[0][1]
    distanciaInicial = 1 / mejorAptitudInicial

    # si verbose es True, se imprime la distancia inicial
    if verbose:
        print(f"Distancia Inicial:  {distanciaInicial:.2f}")

    # bucle principal que itera a traves de las generaciones
    for i in range(generaciones):
        poblacion = siguienteGeneracion(poblacion, indivSeleccionados, razonMutacion)

        # imprime el progreso cada 10 generaciones
        if verbose and (i + 1) % 10 == 0: 
            mejorAptitud = clasificacionRutas(poblacion)[0][1]
            distancia = 1 / mejorAptitud
            print(f"Generacion {i + 1:4}  Distancia: {distancia:.2f}")
    
    # al final se obtiene la mejor ruta y su distancia de la poblacion final
    mejorIndice = clasificacionRutas(poblacion)[0][0]
    mejorRuta = poblacion[mejorIndice]
    mejorAptitud = clasificacionRutas(poblacion)[0][1]
    distanciaFinal = 1 / mejorAptitud

    # se imprime la distancia final y la mejor ruta encontrada
    if verbose:
        print(f"\n--- Resultados Finales ---")
        print(f"Distancia Final: {distanciaFinal:.2f}")
        print("Mejor Ruta (Ciclo Cerrado):")
        # Se enumera la ruta para mostrar el orden de visita
        for i, ciudad in enumerate(mejorRuta):
            print(f"  {i + 1:2}: {ciudad}") 
        print(f"  {len(mejorRuta) + 1:2}: Regresa a {mejorRuta[0]}") 
    # retorna la mejor ruta y su distancia
    return mejorRuta, distanciaFinal