class ConfiguracionPSO:
    """
    Funcion:
        centraliza todos los parametros de configuracion para el problema de optimizacion
        de sensores y el algoritmo PSO.
    """
    
    def __init__(self):
        """
        Funcion:
            inicializa la configuracion con valores predeterminados para el problema y el PSO
        """
        # parametros del problema
        self.NUM_SENSORES = 4
        self.DIMENSIONES = self.NUM_SENSORES * 2
        self.NUM_PARTICULAS = 50
        self.MAX_ITERACIONES = 150
        
        # limites geograficos
        self.LAT_MIN, self.LAT_MAX = 25.52, 25.62
        self.LON_MIN, self.LON_MAX = -108.52, -108.42
        
        # limites de velocidad
        self.VEL_MIN, self.VEL_MAX = -0.005, 0.005
        
        # parametros PSO
        self.W = 0.7   # Inercia
        self.C1 = 2.0  # Coeficiente cognitivo
        self.C2 = 2.0  # Coeficiente social
        
        # radio de cobertura
        self.RADIO_COBERTURA = 0.03
    
    #metodo para obtener limites de posicion y velocidad
    def obtener_limites(self):
        """
        Funcion:
            genera las listas de limites para la posicion y velocidad de las particulas,
            basandose en el numero de sensores y los limites geograficos/velocidad definidos

        Argumentos:
            ninguno

        Regresa: 
            tuple: una tupla que contiener (limites_posicion, limites_velocidad)
        """
        limites_posicion = []
        limites_velocidad = []
        
        for _ in range(self.NUM_SENSORES):
            limites_posicion.extend([
                [self.LAT_MIN, self.LAT_MAX], 
                [self.LON_MIN, self.LON_MAX]
            ])
            limites_velocidad.extend([
                [self.VEL_MIN, self.VEL_MAX], 
                [self.VEL_MIN, self.VEL_MAX]
            ])
        
        return limites_posicion, limites_velocidad
   
    # metodo para mostrar la configuracion actual
    def mostrar_configuracion(self):
        """
        Funcion:
            imprime en la consola un resumen de la configuracion actual del problema

        Argumentos:
            ninguno
        """
        print("=== CONFIGURACIÓN DEL PROBLEMA ===")
        print(f"Numero de sensores: {self.NUM_SENSORES}")
        print(f"Dimensiones del problema: {self.DIMENSIONES}")
        print(f"Numero de particulas: {self.NUM_PARTICULAS}")
        print(f"Limites geograficos: Lat[{self.LAT_MIN}, {self.LAT_MAX}], Lon[{self.LON_MIN}, {self.LON_MAX}]")
        print(f"Radio de cobertura: {self.RADIO_COBERTURA}")
        print("=" * 40)