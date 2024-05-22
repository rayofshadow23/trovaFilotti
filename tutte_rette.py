import json
from shapely.geometry import Point, LineString
from sklearn.linear_model import RANSACRegressor
from scipy.spatial import KDTree
import numpy as np
import matplotlib.pyplot as plt
import haversine as hv
import math

# Parametri configurabili
FILENAME_JSON="san_siro.json"
NUM_PUNTI_MIN = 2  # Numero minimo di punti allineati
DISTANZA_MAX = 20  # Distanza massima dalla linea retta (in metri)
DISTANZA_MIN_PUNTI = 50  # Distanza minima tra i punti (in metri)


def line_2_points(point_A, point_B):
    # Assicurati che i punti non siano gli stessi, altrimenti la pendenza sarebbe indefinita
    if point_A == point_B:
        raise ValueError("I punti A e B devono essere diversi")

    # Calcola la pendenza (m) della retta
    m = (point_B.y - point_A.y) / (point_B.x - point_A.x)

    # Calcola l'intercetta y (q) usando la formula y = mx + q
    q = point_A.y - m * point_A.x

    # Restituisce la pendenza e l'intercetta come tuple
    return m, q

def distance_from_line(punto,slope,intercept):
    slope_perp = -(1/slope)
    intercept_perp = punto.y - (punto.x * slope_perp)
    a_perp = (slope * punto.y + punto.x - intercept * slope) / (slope ** 2 + 1)
    b_perp =  slope_perp * a_perp + intercept_perp
    
    return hv.haversine(a_perp, b_perp, points[z].x,points[z].y)

def draw_close_points(punti,slope,intercept):
    x_values = np.linspace(min(longitudes), max(longitudes), num=100)
    y_values = slope * x_values + intercept
    x_coords = [point.x for point in punti]
    y_coords = [point.y for point in punti]
    plt.scatter(longitudes, latitudes, label="portali",color="black")
    plt.scatter(x_coords, y_coords, label="portali",color="green")
    #plt.annotate(f"{distanza:.2f} mt", (points[z].x, points[z].y),textcoords="offset points",xytext=(0, 5),ha="center")
    plt.plot(x_values, y_values)
    #plt.annotate(f"{data[z]['title']}", (points[z].x, points[z].y), textcoords="offset points",xytext=(0, -5),ha="center",color='green')
    plt.show()
    return
# (a,b) = (gdf['lng'],gdf['lat']
# c = b + (a/slope)



# Carica i dati dal file JSON
with open(FILENAME_JSON) as f:
    data = json.load(f)

# Crea una lista di oggetti Point da latitudine e longitudine
# points = [Point(d['lng'], d['lat']) for d in data]
points = []
for portale in data:
    point = Point(portale['coordinates']['lng'], portale['coordinates']['lat'])
    points.append(point)
longitudes = [point.x for point in points]
latitudes = [point.y for point in points]

min_dist=0
for i in range(len(points)):
    for j in range(i + 1, len(points)):
        slope, intercept = line_2_points(points[i], points[j])
        if slope is not None:  # Se i punti non sono gli stessi
            punti_vicini=[] #lista dei punti entro la distanza richiesta dalla retta approssimante
            distanze=[]
            for z in range(len(points)):
                #calcolo distanza
                distanza = distance_from_line(points[z],slope,intercept)
                if distanza < DISTANZA_MAX:
                    punti_vicini.append(points[z])
                    distanze.append(distanza)
                if (len(distanze) + len(points) -z ) < NUM_PUNTI_MIN:
                    print(f"i:{i},j:{j},z:{z}")
                    break
            sum_d=0 
            if punti_vicini and len(punti_vicini) >= NUM_PUNTI_MIN:
                if(len(punti_vicini)) >= NUM_PUNTI_MIN:
                    NUM_PUNTI_MIN = len(punti_vicini)
                for d in distanze:
                    sum_d=sum_d+d
                if min_dist<sum_d/len(distanze):
                    min_dist = sum_d/len(distanze)
                    best_slope=slope
                    best_intercept=intercept
                    best_punti_vicini=punti_vicini
                    best_distanze=distanze
                    
                
print(f"La distanza media dalla retta è:{min_dist}")
draw_close_points(best_punti_vicini,best_slope,best_intercept)
                        
                
