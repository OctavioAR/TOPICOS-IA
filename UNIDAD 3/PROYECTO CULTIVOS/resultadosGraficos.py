import matplotlib.pyplot as plt
from matplotlib import patches
import seaborn as sns
import numpy as np

# clase para graficar resultados de la optimizacion
class ResultadosGraficos:
    # constructor que recibe los datos de cultivos
    def __init__(self, datos_cultivos):
        self.datos_cultivos = datos_cultivos
    # metodo para graficar la cobertura de sensores
    def cobertura_sensores(self, enjambre, num_sensores, radio_cobertura):
        print("\nGenerando visualización de resultados...")
        
        plt.figure(figsize=(12, 6))
        
        # paleta de colores para los cultivos
        palette_cultivos = {
            'Tomate': 'red',
            'Maiz': 'gold',  
            'Chile': 'green'
        }
        
        # dibujar cultivos
        sns.scatterplot(
            data=self.datos_cultivos, 
            x='Longitud', 
            y='Latitud', 
            hue='Cultivo', 
            s=40, 
            alpha=0.7,
            palette=palette_cultivos
        )
        
        # posiciones optimas de sensores
        mejor_configuracion = np.array(enjambre.mejor_posicion_global).reshape(num_sensores, 2)
        plt.scatter(
            mejor_configuracion[:, 1], 
            mejor_configuracion[:, 0], 
            c='red', 
            marker='d', 
            s=300, 
            edgecolor='black', 
            label=f'Sensores Óptimos (Apt: {enjambre.mejor_aptitud_global:.2f})'
        )
        
        # agregar etiquetas a los sensores
        for i, sensor in enumerate(mejor_configuracion):
            lat, lon = sensor
            plt.text(lon, lat, f"S{i+1}", fontsize=9, color='black', 
                    ha='center', va='center', fontweight='bold')
        
        plt.title(f'Cobertura de {num_sensores} Sensores - Optimización PSO')
        plt.xlabel('Longitud')
        plt.ylabel('Latitud')
        plt.legend(title='Leyenda')
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.axis('equal')
        plt.tight_layout()
        plt.show()