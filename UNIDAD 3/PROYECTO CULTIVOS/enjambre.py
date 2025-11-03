import numpy as np
from particula import Particula
# Clase enjambre que maneja el conjunto de particulas y logica del PSO
class Enjambre:
    # metodo constructor de la clase enjambre    
    def __init__(self, num_particulas, funcion_objetivo, limites_posicion, limites_velocidad, **param_extra):
        self.num_particulas = num_particulas
        self.funcion_objetivo = funcion_objetivo
        self.limites_posicion = limites_posicion
        self.limites_velocidad = limites_velocidad

        # almacena los datos adicionales para la FO: datos_cultivos, num_sensores y radio_cobertura
        self.parametros_extra = param_extra
        
        # mejores globales
        self.mejor_posicion_global = None
        self.mejor_aptitud_global = float('inf')
        
        # parametros PSO
        self.w = 0.7  # Inercia
        self.c1 = 2.0  # Coeficiente cognitivo
        self.c2 = 2.0  # Coeficiente social
        
        # enjambre de particulas
        self.particulas = []
        self.historial_mejor_aptitud = []

    # metodo para inicializar el enjambre de particulas    
    def inicializar_enjambre(self):
        print(f"Inicializando enjambre con {self.num_particulas} particulas...")
        
        # crea particulas con posiciones y velocidades aleatorias
        for i in range(self.num_particulas):
            # posicion aleatoria dentro de los limites
            posicion = [np.random.uniform(lim[0], lim[1]) for lim in self.limites_posicion]
            
            # velocidad aleatoria dentro de los limites
            velocidad = [np.random.uniform(lim[0], lim[1]) for lim in self.limites_velocidad]
            
            # crear particula
            particula = Particula(i, posicion, velocidad)
            
            # evaluar aptitud inicial
            aptitud = self.funcion_objetivo(particula.posicion, **self.parametros_extra)
            particula.actualizar_aptitud(aptitud)
            
            # actualizar mejor global si aptitud es mejor que la actual
            if aptitud < self.mejor_aptitud_global:
                self.mejor_aptitud_global = aptitud
                self.mejor_posicion_global = posicion.copy()
            
            # agregar particula al enjambre
            self.particulas.append(particula)
        
        print(f"Enjambre inicializado. Mejor aptitud inicial: {self.mejor_aptitud_global:.4f}")
    
    # metodo para iniciar las iteraciones del PSO
    def iteraciones_PSO(self, iteracion):
        mejoras_esta_iteracion = 0
        
        # actualizar cada particula
        for particula in self.particulas:
            # actualizar velocidad
            dimensiones = len(particula.posicion)

            # num aleatorios para componente cognitivo y social
            r1, r2 = np.random.rand(dimensiones), np.random.rand(dimensiones)
            
            # calcular nueva velocidad con formula pso
            inercia = self.w * particula.velocidad
            cognitivo = self.c1 * r1 * (particula.mejor_posicion - particula.posicion)
            social = self.c2 * r2 * (self.mejor_posicion_global - particula.posicion)
            
            particula.velocidad = inercia + cognitivo + social
            
            # aplicar limites de velocidad
            for i in range(dimensiones):
                particula.velocidad[i] = np.clip(
                    particula.velocidad[i], 
                    self.limites_velocidad[i][0], 
                    self.limites_velocidad[i][1]
                )
            
            # actualizar posicion
            particula.posicion = particula.posicion + particula.velocidad
            
            # aplicar limites de posicion
            for i in range(dimensiones):
                particula.posicion[i] = np.clip(
                    particula.posicion[i], 
                    self.limites_posicion[i][0], 
                    self.limites_posicion[i][1]
                )
            
            # evaluar nueva aptitud
            aptitud = self.funcion_objetivo(particula.posicion, **self.parametros_extra)
            
            # actualizar mejores personales y globales
            if particula.actualizar_aptitud(aptitud):
                mejoras_esta_iteracion += 1

                # verificar si es mejor que el global
                if aptitud < self.mejor_aptitud_global:
                    self.mejor_aptitud_global = aptitud
                    self.mejor_posicion_global = particula.posicion.copy()
                    print(f"  Nuevo mejor global en iteracion {iteracion}: {self.mejor_aptitud_global:.4f}")

        # retornar numero de mejoras en esta iteracion
        return mejoras_esta_iteracion
    # metodo para ejecutar la optimizacion completa del PSO
    def optimizar(self, max_iteraciones, verbose=True):

        # inicializar enjambre si no ha sido creado
        if not self.particulas:
            self.inicializar_enjambre()
        
        print(f"\nIniciando optimizacion PSO por {max_iteraciones} iteraciones...")
        
        # criterio de parada por numero maximo de iteraciones
        for iteracion in range(max_iteraciones):
            mejoras = self.iteraciones_PSO(iteracion + 1)
            self.historial_mejor_aptitud.append(self.mejor_aptitud_global)
            
            if verbose and (iteracion + 1) % 10 == 0:
                print(f"Iteracion {iteracion + 1}: Mejor aptitud = {self.mejor_aptitud_global:.4f}, Mejoras = {mejoras}")
        
        print(f"\nOptimización completada.")
        # retornar mejor posicion y optimo global
        return self.mejor_posicion_global, self.mejor_aptitud_global
    
    # metodo para mostrar el estado actual del enjambre
    def mostrar_estado_enjambre(self):
        """Muestra el estado actual de todas las particulas"""
        print(f"\n--- ESTADO ACTUAL DEL ENJAMBRE ---")
        print(f"Mejor global: Pos{self.mejor_posicion_global}, Apt={self.mejor_aptitud_global:.4f} ({self.num_particulas} particulas en total)")
        for particula in self.particulas:
            print(f"  {particula}")