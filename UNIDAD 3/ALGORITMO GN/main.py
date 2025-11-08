from algoritmoGenetico import algoritmoGenetico
from municipio import municipio

def datasetMunicipios():
    """
    Funcion: Crea el conjunto de municipios con coordenadas simuladas.

    Retorna:
        list: Lista de objetos 'municipio'.
    """
    ciudades = [
        municipio("Culiacan", 40.4168, -3.7038),
        municipio("Mazatlan", 34.0522, -118.2437),
        municipio("Los Mochis", 51.5074, -0.1278),
        municipio("Guasave", 48.8566, 2.3522),
        municipio("Navolato", 35.6895, 139.6917),
        municipio("Ahome", 55.7558, 37.6173),
        municipio("El Fuerte", 52.5200, 13.4050),
        municipio("Angostura", 41.9028, 12.4964),
        municipio("Salvador Alvarado", 45.4642, 9.1900),
        municipio("Sinaloa", 43.6532, -79.3832),
        municipio("Badiraguato", 37.7749, -122.4194),
        municipio("Concordia", 34.6937, 135.5023),
        municipio("Elota", 35.0116, 135.7681),
        municipio("Escuinapa", 31.2304, 121.4737),
        municipio("Mocorito", 39.9042, 116.4074)
    ]
    return ciudades


def main():
    """
    Funcion: Punto de entrada principal del programa.
    Ejecuta el algoritmo genetico con los parametros definidos.
    """
    municipios = datasetMunicipios()  # Se crean los municipios de prueba

     # Ejecucion del algoritmo genetico con los parametros definidos
    mejorRuta, distanciaFinal = algoritmoGenetico(
        municipios=municipios,  # Lista de municipios   
        tampoblacion=100,       # Tamaño de la poblacion inicial         
        indivSeleccionados=20,  # Individuos seleccionados por generacion     
        razonMutacion=0.01,     # Probabilidad de mutacion      
        generaciones=500,       # Numero total de generaciones         
        verbose=True                
    )
    print(f"\nDistancia Optima: {distanciaFinal:.2f}")

if __name__ == "__main__":
    main()
