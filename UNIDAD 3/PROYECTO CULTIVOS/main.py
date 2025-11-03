import pandas as pd
import numpy as np
import os
from enjambre import Enjambre
from funcion_objetivo import funcion_objetivo
from resultadosGraficos import ResultadosGraficos
from configuracion import ConfiguracionPSO

def main():
    # cargar configuracion
    config = ConfiguracionPSO()
    config.mostrar_configuracion()
    
    DIR_BASE = os.path.dirname(os.path.abspath(__file__))
    RUTA_DATOS = os.path.join(DIR_BASE, 'datosCultivos.csv')
    # cargar datos
    try:
        datos_cultivos = pd.read_csv(RUTA_DATOS)
        print("Datos cargados correctamente")
    except FileNotFoundError:
        print("Error: No se pudo encontrar el archivo 'datosCultivos.csv'")
        return
    
    # configurar limites del problema
    limites_posicion, limites_velocidad = config.obtener_limites()
    
    # crear y ejecutar enjambre PSO
    print(f"\nINICIANDO OPTIMIZACION DE {config.NUM_SENSORES} SENSORES")
    
    enjambre = Enjambre(
        num_particulas=config.NUM_PARTICULAS,
        funcion_objetivo=funcion_objetivo,
        limites_posicion=limites_posicion,
        limites_velocidad=limites_velocidad,
        datos_cultivos=datos_cultivos,
        num_sensores=config.NUM_SENSORES,
        radio_cobertura=config.RADIO_COBERTURA
    )
    
    # ejecutar optimizacion
    mejor_pos, mejor_apt = enjambre.optimizar(config.MAX_ITERACIONES)
    
    # mostrar resultados
    print(f"\n=== RESULTADOS FINALES ===")
    mejores_sensores = np.array(mejor_pos).reshape(config.NUM_SENSORES, 2)
    
    for i, sensor in enumerate(mejores_sensores):
        print(f"Sensor {i+1}: Lat={sensor[0]:.6f}, Lon={sensor[1]:.6f}")
    
    print(f"Aptitud final: {mejor_apt:.4f}")
    
    # calcular y mostrar el numero de cultivos cubiertos por la mejor solucion
    posiciones_sensores_optimas = np.array(mejor_pos).reshape(config.NUM_SENSORES, 2)
    cultivos_cubiertos = 0
    for _, cultivo in datos_cultivos.iterrows():
        cultivo_pos = [cultivo['Latitud'], cultivo['Longitud']]
        # calcular la distancia euclidiana desde el cultivo a todos los sensores
        distancias_a_sensores = np.sqrt(np.sum((posiciones_sensores_optimas - cultivo_pos)**2, axis=1))
        # encontrar la distancia al sensor mas cercano
        distancia_minima = np.min(distancias_a_sensores)
        # si la distancia es menor o igual al radio, el cultivo esta cubierto
        if distancia_minima <= config.RADIO_COBERTURA:
            cultivos_cubiertos += 1
    print(f"Cultivos cubiertos: {cultivos_cubiertos} de {len(datos_cultivos)}")
    
    # visualizar resultados
    visualizador = ResultadosGraficos(datos_cultivos)
    visualizador.cobertura_sensores(enjambre, config.NUM_SENSORES, config.RADIO_COBERTURA)
    
    print("\nOptimizacion completada")

if __name__ == "__main__":
    main()