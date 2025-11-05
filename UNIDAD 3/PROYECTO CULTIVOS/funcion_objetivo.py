import numpy as np
import pandas as pd

# FO que conbina cobertura geografica y calidad agricola
def funcion_objetivo(posicion_completa, datos_cultivos, num_sensores, radio_cobertura):
    """
    Funcion:
        calcula el valor de aptitud "costo" para una configuracion de sensores.
        El costo es una combinacion de la distancia promedio a los cultivos, una penalizacion
        por cultivos no cubiertos y costos relacionados con la calidad agricola (diversidad,
        variabilidad de humedad, etc.). Un valor mas bajo es mejor

    Argumentos:
        posicion_completa (list): un vector con las coordenadas (lat, lon) de todos los sensores
        datos_cultivos (pd.DataFrame): DataFrame con los datos de los cultivos
        num_sensores (int): el numero de sensores en la configuracion
        radio_cobertura (float): el radio de cobertura de cada sensor

    Regresa: 
        float: el costo total (aptitud) de la configuracion de sensores
    """
    
    # convertir posicion plana a matriz de posiciones de sensores
    posiciones_sensores = np.array(posicion_completa).reshape(num_sensores, 2)
    datos_completos = datos_cultivos.copy()
    
    distancias_minimas = []     # almacenar distancias minimas de cultivos a sensores
    cultivos_cubiertos = []     # almacenar cultivos cubiertos 
    cultivos_no_cubiertos = 0
    
    # calcular covertura y distancia minima
    for _, cultivo in datos_completos.iterrows():
        cultivo_pos = [cultivo['Latitud'], cultivo['Longitud']] # coordenadas del cultivo
        # formula de distancia euclidiana raiz (x^2 + y^2)
        distancias_a_sensores = np.sqrt(np.sum((posiciones_sensores - cultivo_pos)**2, axis=1))
        distancia_minima = np.min(distancias_a_sensores) # distancia minima al sensor mas cercano
        distancias_minimas.append(distancia_minima)     # distancia minima al sensor mas cercano
        
        # Si el cultivo esta dentro del radio de cobertura entonces guardar sus datos
        if distancia_minima <= radio_cobertura:
            cultivos_cubiertos.append(cultivo)
        else:
            cultivos_no_cubiertos += 1
    
    # calcular metricas para calidad agricola
    if len(cultivos_cubiertos) > 0:
        df_cubiertos = pd.DataFrame(cultivos_cubiertos)
        
        # diversidad de cultivos cubiertos
        costo_diversidad = 100 - (len(df_cubiertos['Cultivo'].unique()) * 25)  # menos diversidad = mas costo
        costo_variabilidad = 50 - (df_cubiertos['Humedad (%)'].std() * 5)     # menos variabilidad = mas costo
        if np.isnan(costo_variabilidad):
            costo_variabilidad = 50  # maximo costo si no hay variabilidad
            
        costo_elevacion = 30 - ((df_cubiertos['Elevacion (m)'].max() - df_cubiertos['Elevacion (m)'].min()) * 0.2)
        
    else:
        # maximos costos si no hay cultivos cubiertos
        costo_diversidad = 100
        costo_variabilidad = 50
        costo_elevacion = 30
    
    # calculo de aptitud combinada
    distancia_promedio = np.mean(distancias_minimas) if distancias_minimas else 10.0
    
    # componente de cobertura 
    componente_cobertura = distancia_promedio * 100  # Escalado para que sea significativo
    
    # componente de penalizacion por no cobertura 
    penalizacion_no_cobertura = cultivos_no_cubiertos * 10
    
    # componente de calidad agricola MAXIMIZAR
    componente_calidad = (costo_diversidad + 
                         costo_variabilidad + 
                         costo_elevacion)
    
    # costo total suma
    costo_total = (componente_cobertura + 
                  penalizacion_no_cobertura + 
                  componente_calidad)
    
    # imprimir detalles de la evaluacion
    if np.random.random() < 0.01: 
        print(f"Cubiertos: {len(cultivos_cubiertos)}, Aptitud: {costo_total:.2f}")
    # retornar aptitud total
    return costo_total