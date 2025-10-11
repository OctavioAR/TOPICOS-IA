import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import folium
import os
from typing import List, Tuple 
from cargarDatos import cargarDatos
from recocidoSimulado import recocidoSimulado
from funcionDeCosto import calcularCosto, Solucion
from solucion import solucionInicial

# parametros 
DIR_BASE = os.path.dirname(os.path.abspath(__file__))
ARCH_COORDS = os.path.join(DIR_BASE, "datos", "coordenadas.csv")
ARCH_DIST = os.path.join(DIR_BASE, "datos", "distancia.csv")
ARCH_COSTO = os.path.join(DIR_BASE, "datos", "costo_combustible.csv")
SALIDA_HTML = "rutas_optimas_culiacan.html"

# parametros del recocido simulado
T_INICIAL = 100.0  
T_FINAL = 0.1       
ALPHA = 0.95       
L = 200 

# funcion para generar el mapa de rutas
def mapaRutas(coords: pd.DataFrame, solucion: Solucion, html: str):

    # paleta de colores para las rutas
    colors = ['darkred', 'blue', 'green', 'purple', 'orange', 'darkblue', 'darkgreen', 'cadetblue', 'black', 'red']
    
    # determinar el centro del mapa
    latitudCentro = coords['Latitud_WGS84'].mean()
    longitudCentro = coords['Longitud_WGS84'].mean()
    
    # crear el mapa base
    m = folium.Map(location=[latitudCentro, longitudCentro], zoom_start=11)
    
    # trazar las rutas y agregar marcadores
    for i, route in enumerate(solucion):
        color = colors[i % len(colors)]
        route_coords = []
        
        if not route: continue

        cd_index = route[0]

        # recolectar coordenadas y marcar nodos
        for j, node_index in enumerate(route):
            lat = coords.loc[node_index, 'Latitud_WGS84']
            lon = coords.loc[node_index, 'Longitud_WGS84']
            route_coords.append((lat, lon))
            
            nombre = coords.loc[node_index, 'Nombre']
            tipo = coords.loc[node_index, 'Tipo']
            
            # marcar CD
            if tipo == 'Centro de Distribución' and j == 0:
                folium.Marker(
                    location=[lat, lon],
                    popup=f"CD {cd_index+1}",
                    icon=folium.Icon(color=color, icon='warehouse', prefix='fa')
                ).add_to(m)
            # marcar tiendas
            elif tipo == 'Tienda':
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=5,
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.7,
                    popup=nombre
                ).add_to(m)

        # dibujar la linea de la ruta
        if len(route_coords) > 1:
            folium.PolyLine(
                locations=route_coords,
                color=color,
                weight=3.5,
                opacity=0.8,
                popup=f"Ruta {i+1} (CD {cd_index+1})"
            ).add_to(m)

    m.save(html)
    print(f"\nMapa de rutas generado y guardado como '{html}'")

# funcion principal
def main():
    # cargar datos
    coords_df, dist_matriz, cost_matriz = cargarDatos(
        ARCH_COORDS, 
        ARCH_DIST, 
        ARCH_COSTO
    )
    
    # ejecuta el recocido simulado
    mejorSolucion, costoFinal, historialCost = recocidoSimulado(
        dist_matriz,
        cost_matriz,
        T0=T_INICIAL,
        TF=T_FINAL,
        alpha=ALPHA,
        L=L
    )
    
    # resultados por consola
    print("\n--- RESULTADOS FINALES DE LA OPTIMIZACIÓN ---")
    print(f"Costo Final optimo: ${costoFinal:,.2f} MXN")
    print("\n--- RUTAS ÓPTIMAS ENCONTRADAS (CD -> Tiendas -> CD) ---")
    
    for i, ruta in enumerate(mejorSolucion):
        # mapear los indices de los nodos a sus nombres
        nombres_ruta = [coords_df.loc[nodo, 'Nombre'] for nodo in ruta]
        ruta_str = " -> ".join(nombres_ruta)
        print(f"Ruta {i+1}: {ruta_str}")
        
    # generar mapa de rutas
    mapaRutas(coords_df, mejorSolucion, SALIDA_HTML)
    
if __name__ == "__main__":
    main()