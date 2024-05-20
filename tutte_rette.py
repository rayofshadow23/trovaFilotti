import json
from shapely.geometry import Point, LineString
from sklearn.linear_model import RANSACRegressor
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


# (a,b) = (gdf['lng'],gdf['lat']
# c = b + (a/slope)

def y_perp(x):
    return slope_perp * x + intercept_perp


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
longitudes = [point.x for point in points]
latitudes = [point.y for point in points]


for i in range(len(points)):
    for j in range(i + 1, len(points)):
        slope, intercept = retta_tra_due_punti(points[i], points[j])
        if slope is not None:  # Se i punti non sono gli stessi
            print(f"Retta tra {points[i]} e {points[j]}: y = {slope}x + {intercept}")
            slope_perp = -1 / slope
            for z in range(len(points)):
                intercept_perp = points[z].y - (points[z].x * slope_perp)
                a_perp = (slope * points[z].y + points[z].x - intercept * slope) / (slope ** 2 + 1)
                b_perp = y_perp(a_perp)
                distanza = hv.haversine(a_perp, b_perp, points[z].x,points[z].y)
                if distanza < 25:
                    x_values = np.linspace(min(longitudes), max(latitudes), num=100)
                    y_values = slope * x_values + intercept
                    plt.scatter(points[z].x, points[z].y, label="portali")
                    plt.annotate(f"{distanza:.2f} mt", (points[z].x, points[z].y),
                                 textcoords="offset points",
                                 xytext=(0, 5),
                                 ha="center")
                    plt.plot(x_values, y_values)
                    plt.annotate(f"{data[z]['title']}", (points[z].x, points[z].y), textcoords="offset points",
                                 xytext=(0, -5),
                                 ha="center")
                    plt.show()

                    print(f"ciclo i:{i},j:{j},z:{z}")
                    print(f"Distanza dalla retta:{distanza} mt")
                    print(f"punto sulla retta: ({a_perp:.6f},{b_perp:.6f}) e punti portale: ({points[z].x}, {points[z].y})")

                else:
                    break


plt.show()


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
