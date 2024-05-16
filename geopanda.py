import json
from shapely.geometry import Point, LineString
import geopandas as gpd
from scipy.spatial import KDTree
import numpy as np
import matplotlib.pyplot as plt
import haversine as hv
import math


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

slope_perp = -1 / slope
#(a,b) = (gdf['lng'],gdf['lat']
#c = b + (a/slope)
intercept_perp = gdf['lat'] - (gdf['lng'] * slope_perp)
print(intercept_perp)

def y_perp(x):
    return slope_perp*x + intercept_perp

a_perp = (slope*gdf['lat'] + (gdf['lng']) - intercept*slope)/(slope**2+1)
b_perp = y_perp(a_perp)


i=0
while i < 7:
    print(f"il punto di intersezione per il punto {points[i]} è ({a_perp[i]},{b_perp[i]})")
    i = i+1


# Create the regression line
x_values = np.linspace(min(gdf['lng']), max(gdf['lng']), num=100)
y_values = slope * x_values + intercept
print(x_values)

gdf['distanza_dalla_linea'] = hv.haversine(b_perp,a_perp,gdf['lng'],gdf['lat'])

