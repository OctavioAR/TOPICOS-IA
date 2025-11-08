
class Aptitud:
    """
    Clase: Calcula la aptitud (fitness) de una ruta en el problema del agente viajero.
    La aptitud se basa en la distancia total recorrida: a menor distancia, mayor aptitud.
    """
     
    def __init__(self, ruta):
        """
        Funcion: Constructor de la clase Aptitud.

        Argumentos:
            ruta (list): Lista de objetos 'municipio' que representan una ruta.

        Retorna:
            None. Inicializa los atributos distancia y f_aptitud.
        """
        # Lista de municipios que forman la ruta
        self.ruta = ruta     
        # Variable para almacenar la distancia total   
        self.distancia = 0    
        # Valor de aptitud (fitness) de la ruta  
        self.f_aptitud = 0.0    

    def distanciaRuta(self):
        """
        Funcion: Calcula la distancia total de la ruta cerrada (vuelta completa).

        Argumentos:
            Ninguno.

        Retorna:
            float: Distancia total recorrida por la ruta.
        """
        # Solo calcula la distancia una vez (si aun no se ha hecho)
        if self.distancia == 0:
            distanciaTotal = 0
            # Recorre todos los municipios de la ruta
            for i in range(len(self.ruta)):
                puntoInicial = self.ruta[i] #Municipio actual
                puntoFinal = self.ruta[(i + 1) % len(self.ruta)] # El ultimo regresa al primero
                # Suma la distancia euclidiana entre ambos puntos
                distanciaTotal += puntoInicial.distancia(puntoFinal)
            # Guarda la distancia total calculada
            self.distancia = distanciaTotal
        return self.distancia
    
    def rutaApta(self):
        """
        Funcion: Calcula la aptitud de la ruta como el inverso de la distancia total.
        Rutas mas cortas tienen un valor de aptitud mas alto.

        Argumentos:
            Ninguno.

        Retorna:
            float: Valor de aptitud de la ruta.
        """
        # Solo calcula la aptitud una vez (si aun no se ha hecho)
        if self.f_aptitud == 0:
            self.f_aptitud = 1 / float(self.distanciaRuta()) # Asigna su inverso como valor de aptitud (menor distancia = mayor aptitud)
        return self.f_aptitud