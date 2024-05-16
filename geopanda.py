import json
from shapely.geometry import Point, LineString
import geopandas as gpd
from scipy.spatial import KDTree
import numpy as np
import matplotlib.pyplot as plt
import haversine as hv


# Parametri configurabili
NUM_PUNTI_MIN = 3  # Numero minimo di punti allineati
DISTANZA_MAX = 20  # Distanza massima dalla linea retta (in metri)
DISTANZA_MIN_PUNTI = 3  # Distanza minima tra i punti (in metri)

# Carica i dati dal file JSON
with open('punti.json') as f:
    data = json.load(f)

# Crea una lista di oggetti Point da latitudine e longitudine
points = [Point(d['lng'], d['lat']) for d in data]

# Crea un GeoDataFrame
gdf = gpd.GeoDataFrame(data, geometry=points)

# Calcola la linea retta approssimante usando i primi due punti
#linea_approssimante = LineString(gdf['geometry'][:2])
#using polyfit
slope, intercept = np.polyfit(gdf['lng'], gdf['lat'], deg=1)
print(slope)
print(intercept)

# Calcola la distanza di ogni punto dalla linea approssimante
#gdf['distanza_dalla_linea'] = gdf['geometry'].apply(lambda punto: punto.distance(linea_approssimante))
y_estimated = -(1/slope) * gdf['lng'] + intercept


gdf['distanza_dalla_linea'] = np.abs(gdf['lat'] - (slope * gdf['lng'] + intercept)) / np.sqrt(1 + slope**2)

# Filtra i punti che sono entro la DISTANZA_MAX dalla linea approssimante
punti_vicini = gdf[gdf['distanza_dalla_linea'] <= DISTANZA_MAX]

# Create the regression line
x_values = np.linspace(min(gdf['lng']), max(gdf['lng']), num=100)
y_values = slope * x_values + intercept

# Plot the data points, regression line, and distances
plt.scatter(gdf['lng'], gdf['lat'], label='Data Points')
plt.plot(x_values, y_values, color='red', label='Regression Line')
for i, row in gdf.iterrows():
    plt.annotate(f"{row['distanza_dalla_linea']:.6f}", (row['lng'], row['lat']), textcoords="offset points", xytext=(0, 5), ha='center')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Regression Line with Perpendicular Distances')
plt.legend()
plt.show()