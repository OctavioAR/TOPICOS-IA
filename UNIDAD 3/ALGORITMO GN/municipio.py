import numpy as np

class municipio:
    def __init__(self, nombre, x,y):
        """
        Funcion: Constructor de la clase municipio.

        Argumentos:
            nombre (str): Nombre del municipio.
            x (float): Coordenada X (posicion en el eje horizontal).
            y (float): Coordenada Y (posicion en el eje vertical).

        Retorna:
            Inicializa un objeto 'municipio' con sus atributos.
        """
        self.nombre = nombre 
        self.x = x  
        self.y = y  
    
    def distancia(self, otro_municipio):
        """
        Funcion: Calcula la distancia euclidiana entre el municipio actual
        y otro municipio.

        Argumentos:
            otro_municipio (municipio): Otro objeto de tipo municipio con coordenadas (x, y).

        Retorna:
            float: Distancia euclidiana entre ambos municipios.
        """
        # Diferencia absoluta entre las coordenadas X e Y
        xDis = abs(self.x - otro_municipio.x) 
        yDis = abs(self.y - otro_municipio.y)

        # Calculo de la distancia euclidiana usando el teorema de Pitagoras
        distancia = np.sqrt((xDis ** 2) + (yDis ** 2))
        return distancia
    
    def __repr__(self):
        """
        Funcion: Representacion en cadena del objeto municipio.
        
        Argumentos:
            Ninguno.
        
        Retorna:
            str: Cadena que muestra el nombre del municipio y sus coordenadas (x, y).
        """
        return f"{self.nombre} ({self.x},{self.y})"