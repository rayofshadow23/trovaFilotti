import json
from shapely.geometry import Point, LineString
from sklearn.linear_model import RANSACRegressor
import geopandas as gpd
from scipy.spatial import KDTree
import numpy as np
import matplotlib.pyplot as plt
import haversine as hv
import math

# Parametri configurabili
NUM_PUNTI_MIN = 23  # Numero minimo di punti allineati
DISTANZA_MAX = 20  # Distanza massima dalla linea retta (in metri)
DISTANZA_MIN_PUNTI = 3  # Distanza minima tra i punti (in metri)


def retta_tra_due_punti(point_A, point_B):
    # Assicurati che i punti non siano gli stessi, altrimenti la pendenza sarebbe indefinita
    if point_A == point_B:
        raise ValueError("I punti A e B devono essere diversi")

    # Calcola la pendenza (m) della retta
    m = (point_B.y - point_A.y) / (point_B.x - point_A.x)

    # Calcola l'intercetta y (q) usando la formula y = mx + q
    q = point_A.y - m * point_A.x

    # Restituisce la pendenza e l'intercetta come tuple
    return m, q


# Carica i dati dal file JSON
with open('punti.json') as f:
    data = json.load(f)

# Crea una lista di oggetti Point da latitudine e longitudine
# points = [Point(d['lng'], d['lat']) for d in data]
points = []
for portale in data:
    lat = portale['coordinates']['lat']
    lng = portale['coordinates']['lng']
    point = Point(lng, lat)
    points.append(point)

# Crea un GeoDataFrame
gdf = gpd.GeoDataFrame(data, geometry=points)

# Calcola la linea retta approssimante usando i primi due punti
# linea_approssimante = LineString(gdf['geometry'][:2])
# using polyfit
slope, intercept = np.polyfit(gdf['coordinates']['lng'], gdf['coordinates']['lat'], deg=1)

slope_perp = -1 / slope
# (a,b) = (gdf['lng'],gdf['lat']
# c = b + (a/slope)
intercept_perp = gdf['lat'] - (gdf['lng'] * slope_perp)
print(intercept_perp)


def y_perp(x):
    return slope_perp * x + intercept_perp


a_perp = (slope * gdf['lat'] + (gdf['lng']) - intercept * slope) / (slope ** 2 + 1)
b_perp = y_perp(a_perp)

i = 0

for index, row in gdf.iterrows():
    print(
        f"punto sulla retta: ({a_perp[index]},{b_perp[index]}) e punti portale: ({gdf.at[index, 'lng']}, {gdf.at[index, 'lat']})")
    gdf.at[index, 'distanza_linea'] = hv.haversine(a_perp[index], b_perp[index], gdf.at[index, 'lng'],
                                                   gdf.at[index, 'lat'])
    print(gdf.at[index, 'distanza_linea'])

# Create the regression line
x_values = np.linspace(min(gdf['lng']), max(gdf['lng']), num=100)
y_values = slope * x_values + intercept
print(x_values)

plt.scatter(gdf['lng'], gdf['lat'], label="portali")
plt.plot(x_values, y_values)
for i, row in gdf.iterrows():
    if row['distanza_linea'] < DISTANZA_MAX:
        plt.annotate(f"{row['distanza_linea']:.2f} mt", (row['lng'], row['lat']), textcoords="offset points",
                     xytext=(0, 5),
                     ha="center")
        plt.annotate(f"{row['title']}", (row['lng'], row['lat']), textcoords="offset points", xytext=(0, -5),
                     ha="center")

# Converti i punti in un array NumPy per l'uso con RANSAC
X = np.array(gdf['lng']).reshape(-1, 1)
y = np.array(gdf['lat'])

# Inizializza il modello RANSAC
ransac = RANSACRegressor()

# Adatta il modello ai dati
ransac.fit(X, y)

# Ottieni i punti inliers (punti che si adattano al modello)
inlier_mask = ransac.inlier_mask_

# Filtra gli outliers
gdf_inliers = gdf[inlier_mask]

# Calcola la linea di regressione con i punti inliers
slope_inliers, intercept_inliers = np.polyfit(gdf_inliers['lng'], gdf_inliers['lat'], deg=1)

# Crea la linea di regressione per il plot
x_values_inliers = np.linspace(min(gdf_inliers['lng']), max(gdf_inliers['lng']), num=100)
y_values_inliers = slope_inliers * x_values_inliers + intercept_inliers
plt.scatter(gdf_inliers['lng'], gdf_inliers['lat'], label="portali inliers", color='red')
for i, row in gdf_inliers.iterrows():
    if row['distanza_linea'] < DISTANZA_MAX:
        plt.annotate(f"{row['distanza_linea']:.2f} mt", (row['lng'], row['lat']), textcoords="offset points",
                     xytext=(0, 5),
                     ha="center")
        plt.annotate(f"{row['title']}", (row['lng'], row['lat']), textcoords="offset points", xytext=(0, -5),
                     ha="center")

# Plot dei punti inliers e della linea di regressione

plt.plot(x_values_inliers, y_values_inliers, color='red', label="linea di regressione")
plt.legend()
plt.show()
