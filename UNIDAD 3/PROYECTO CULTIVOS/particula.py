import numpy as np
# clase Particula representa una particula en el enjambre PSO
class Particula:
    # metodo constructor que inicializa la particula
    def __init__(self, id_particula, posicion_inicial, velocidad_inicial):
        self.id = id_particula
        self.posicion = np.array(posicion_inicial) # vector de posicion
        self.velocidad = np.array(velocidad_inicial) # vector de velocidad
        self.mejor_posicion = self.posicion.copy() # mejor posicion
        self.mejor_valor = float('inf') # mejor aptitud de la FO
        self.valor = float('inf') # aptitud actual de la FO
    
    # metodo para actualizar la aptitud de la particula    
    def actualizar_aptitud(self, nueva_aptitud):
        self.valor = nueva_aptitud 
        # si la nueva aptitud es mejor que la mejor conocida, actualizar
        if nueva_aptitud < self.mejor_valor: 
            self.mejor_valor = nueva_aptitud 
            self.mejor_posicion = self.posicion.copy() 
            return True 
        return False 
    # metodo para representar la particula como cadena
    def __str__(self):
        return f"Particula {self.id}: Pos({self.posicion[0]:.4f}, {self.posicion[1]:.4f}) Apt={self.valor:.2f}"