import numpy as np

class Particula:
    """
    Funcion:
        representa una particula individual en el algoritmo PSO
        cada particula tiene una posicion, una velocidad, una aptitud actual y recuerda su mejor posicion historica
    """
    # metodo constructor que inicializa la particula
    def __init__(self, id_particula, posicion_inicial, velocidad_inicial):
        """
        Funcion:
            Inicializa una nueva particula

        Argumentos:
            id_particula (int): identificador unico para la particula
            posicion_inicial (list): posicion inicial de la particula en el espacio de busqueda
            velocidad_inicial (list): velocidad inicial de la particula
        """
        self.id = id_particula
        self.posicion = np.array(posicion_inicial) # vector de posicion
        self.velocidad = np.array(velocidad_inicial) # vector de velocidad
        self.mejor_posicion = self.posicion.copy() # mejor posicion
        self.mejor_valor = float('inf') # mejor aptitud de la FO
        self.valor = float('inf') # aptitud actual de la FO
    
    # metodo para actualizar la aptitud de la particula    
    def actualizar_aptitud(self, nueva_aptitud):
        """
        Funcion:
            actualiza la aptitud de la particula y si la nueva aptitud es mejor que la
            mejor aptitud personal anterior, actualiza la mejor posición y valor personal

        Argumentos:
            nueva_aptitud (float): El nuevo valor de aptitud calculado para la posicion actual

        Regresa: 
            bool: True si la mejor aptitud personal fue actualizada, False en caso contrario
        """
        self.valor = nueva_aptitud 
        # si la nueva aptitud es mejor que la mejor conocida, actualizar
        if nueva_aptitud < self.mejor_valor: 
            self.mejor_valor = nueva_aptitud 
            self.mejor_posicion = self.posicion.copy() 
            return True 
        return False 