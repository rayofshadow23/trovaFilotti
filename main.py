import json
from shapely.geometry import Point, LineString, Polygon
from sklearn.linear_model import RANSACRegressor
from scipy.spatial import KDTree
import numpy as np
import matplotlib.pyplot as plt
from math import radians, cos, sin, asin, sqrt
import time
import multiprocessing

start_time = time.time()

# Parametri configurabili
FILENAME_JSON = "san_siro.json"
NUM_PUNTI_MIN = 5  # Numero minimo di punti allineati
DISTANZA_MAX = 10  # Distanza massima dalla linea retta (in metri)
DISTANZA_MAX_TRA_ESTREMI = 4000  # Distanza max tra i punti estremi del filotto(in metri)



def haversine(lon1, lat1, lon2, lat2):
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of Earth in kilometers
    #returns in meters
    return c * r * 1000

def isInsideTriangle(point_to_check, vertex_A, vertex_B, vertex_C):
    # Creare un triangolo come istanza di Polygon con i vertici A, B e C
    triangle = Polygon([vertex_A[0], vertex_B[0], vertex_C[0]])
    # Creare il plot
    x, y = zip(*triangle.exterior.coords)
    plt.fill(x, y, 'g', alpha=0.2)  # Triangolo blu semi-trasparente
    plt.plot(point_to_check[0].x, point_to_check[0].y, 'ro')  # Punto rosso
    plt.xlim(min(x) - 0.01, max(x) + 0.01)
    plt.ylim(min(y) - 0.01, max(y) + 0.01)
    plt.show()
    # Utilizzare il metodo contains di Polygon per verificare se il punto è all'interno del triangolo
    return triangle.contains(point[0])

def create_tsp_file(locations):
    num_locations = len(locations)

    # Header for the TSP file
    tsp_content = f"""NAME : it{num_locations}
COMMENT : {num_locations} locations in Italy
COMMENT : Derived from National Imagery and Mapping Agency data
TYPE : TSP
DIMENSION : {num_locations}
EDGE_WEIGHT_TYPE : EUC_2D
NODE_COORD_SECTION
"""

    # Add coordinates for each location
    for i, loc in enumerate(locations, start=1):
        lng, lat = float(loc[0].x), float(loc[0].y)
        tsp_content += f"{i} {lat*1000:.6f} {lng*1000:.6f}\n"

    # Write to the TSP file
    with open("locations.tsp", "w") as tsp_file:
        tsp_file.write(tsp_content)


def draw_triangle_and_point(point_to_draw, vertex_A, vertex_B, vertex_C):
    """
    Disegna un triangolo e un punto sul plot.

    Parameters:
    point_to_draw (tuple): Un punto da disegnare, formato da coordinate (x, y).
    vertex_A (tuple): Le coordinate (x, y) del vertice A del triangolo.
    vertex_B (tuple): Le coordinate (x, y) del vertice B del triangolo.
    vertex_C (tuple): Le coordinate (x, y) del vertice C del triangolo.

    Returns:
    None: La funzione non restituisce nulla ma visualizza un plot con un triangolo e un punto.
    """
    # Creare un triangolo come istanza di Polygon con i vertici A, B e C
    triangle = Polygon([vertex_A[0], vertex_B[0], vertex_C[0]])
    # Creare il plot
    x, y = zip(*triangle.exterior.coords)
    plt.fill(x, y, 'g', alpha=0.2)  # Triangolo blu semi-trasparente
    plt.plot(point_to_draw[0].x, point_to_draw[0].y, 'ro')  # Punto rosso
    plt.xlim(min(x) - 0.01, max(x) + 0.01)
    plt.ylim(min(y) - 0.01, max(y) + 0.01)
    plt.show()
    return

# funzione che calcola la retta tra due punti
def line_2_points(point_A, point_B):
    # Assicurati che i punti non siano gli stessi, altrimenti la pendenza sarebbe indefinita
    if point_A == point_B:
        raise ValueError("I punti A e B devono essere diversi")

    # Calcola la pendenza (m) della retta
    m = (point_B[0].y - point_A[0].y) / (point_B[0].x - point_A[0].x)

    # Calcola l'intercetta y (q) usando la formula y = mx + q
    q = point_A[0].y - m * point_A[0].x

    # Restituisce la pendenza e l'intercetta come tuple
    return m, q


def distance_from_line(punto, slope, intercept):
    if slope == 0:
        return 99999
    slope_perp = -(1 / slope)
    intercept_perp = punto[0].y - (punto[0].x * slope_perp)
    a_perp = (slope * punto[0].y + punto[0].x - intercept * slope) / (slope ** 2 + 1)
    b_perp = slope_perp * a_perp + intercept_perp
    return haversine(a_perp, b_perp, punto[0].x, punto[0].y)


def draw_close_points(punti, slope, intercept, i, j):
    x_values = np.linspace(get_west_portal(punti)[0].x, get_east_portal(punti)[0].x, num=100)
    y_values = slope * x_values + intercept
    # plt.ylim(min(y_values)-((0.01*min(y_values))/100),max(y_values)+((0.01*max(y_values))/100))
    # plt.xlim(min(x_values)-((0.02*min(x_values))/100),max(x_values)+((0.02*max(x_values))/100))
    x_coords = [point[0].x for point in punti]
    y_coords = [point[0].y for point in punti]
    plt.scatter(longitudes, latitudes, label="portali", color="black")
    plt.scatter(x_coords, y_coords, label="portali", color="green")
    # plt.annotate(f"{distanza:.2f} mt", (points[z].x, points[z].y),textcoords="offset points",xytext=(0, 5),ha="center")
    plt.plot(x_values, y_values)
    plt.annotate(f"{titles_portal[i]}", (points[i][0].x, points[i][0].y), textcoords="offset points", xytext=(0, -5),
                 ha="center", color='green')
    plt.annotate(f"{titles_portal[j]}", (points[j][0].x, points[j][0].y), textcoords="offset points", xytext=(0, -5),
                 ha="center", color='green')
    plt.show()
    return


def load_file(file_json):
    # Carica i dati dal file JSON
    with open(file_json) as f:
        portali = json.load(f)
    return portali


def get_west_portal(punti):
    min_lon = 999;
    west_portal = punti[0]
    for punto in punti:
        if punto[0].x < min_lon:
            west_portal = punto
            min_lon = punto[0].x
    return west_portal


def get_east_portal(punti):
    max_lon = 0;
    east_portal = punti[0]
    for punto in punti:
        if punto[0].x > max_lon:
            east_portal = punto
            max_lon = punto[0].x
    return east_portal


def compute_distances(points, i, j, DISTANZA_MAX, NUM_PUNTI_MIN):
    try:
        slope, intercept = line_2_points(points[i], points[j])
        if slope is not None:
            punti_vicini = []
            distanze = []
            for z in range(len(points)):
                distanza = distance_from_line(points[z], slope, intercept)
                if distanza <= DISTANZA_MAX:
                    punti_vicini.append(points[z])
                    if haversine(get_east_portal(punti_vicini)[0].x,
                                 get_east_portal(punti_vicini)[0].y,
                                 get_west_portal(punti_vicini)[0].x,
                                 get_west_portal(punti_vicini)[0].y) > DISTANZA_MAX_TRA_ESTREMI:
                        punti_vicini.pop()
                        break
                    distanze.append(distanza)
                if (len(distanze) + len(points) - z) < NUM_PUNTI_MIN: #esco se i portali rimanenti cmq non bastano per superare il max già raggiunto
                    break
            return i, j, punti_vicini, distanze
    except ValueError as e:
        print(f"Errore: {e}")
        return None


def save_to_json(points, filename='bookmarks.json'):
    # Initialize the JSON structure
    data = {
        "maps": {
            "idOthers": {
                "label": "Others",
                "state": 1,
                "bkmrk": {}
            }
        },
        "portals": {
            "idOthers": {
                "label": "Others",
                "state": 1,
                "bkmrk": {}
            }
        }
    }

    # Populate the 'bkmrk' dictionary with points and labels
    for idx, (point, label) in enumerate(points):
        latlng = f"{point.y},{point.x}"
        data['portals']['idOthers']['bkmrk'][chr(97 + idx)] = {
            "latlng": latlng,
            "label": label
        }

    # Write the JSON data to a file
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=2)




def are_lines_almost_parallel(slope1, slope2, tolerance=0.1):
    # Compare the slopes with a given tolerance
    return abs(slope1 - slope2) < tolerance


def find_best_line(points, NUM_PUNTI_MIN):
    min_dist_media = 0
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            slope, intercept = line_2_points(points[i], points[j])
            if slope is not None:  # Se i punti non sono gli stessi
                punti_vicini = []  # lista dei punti entro la distanza richiesta dalla retta approssimante
                distanze = []
                for z in range(len(points)):
                    # calcolo distanza
                    distanza = distance_from_line(points[z], slope, intercept)
                    if distanza < DISTANZA_MAX:
                        punti_vicini.append(points[z])
                        if haversine(get_east_portal(punti_vicini)[0].x, get_east_portal(punti_vicini)[0].y,
                                        get_west_portal(punti_vicini)[0].x,
                                        get_west_portal(punti_vicini)[0].y) > DISTANZA_MAX_TRA_ESTREMI:
                            break
                        distanze.append(distanza)
                    if (len(distanze) + len(points) - z) < NUM_PUNTI_MIN:
                        break
                sum_d = 0
                if punti_vicini and (len(punti_vicini) > NUM_PUNTI_MIN):
                    NUM_PUNTI_MIN = len(punti_vicini)
                    print(f"i:{i},j:{j},z:{z},NUM_PUNTI_MIN:{NUM_PUNTI_MIN}")
                    for d in distanze:
                        sum_d = sum_d + d
                    if min_dist_media < sum_d / len(distanze):
                        min_dist_media = sum_d / len(distanze)
                        best_slope = slope
                        best_intercept = intercept
                        best_punti_vicini = punti_vicini
                        best_distanze = distanze
                        portale_i = i
                        portale_j = j

    return min_dist_media, best_slope, best_intercept, best_punti_vicini, best_distanze, portale_i, portale_j, NUM_PUNTI_MIN
def find_best_line_parallel(points, NUM_PUNTI_MIN, DISTANZA_MAX):
    best_slope = None
    best_intercept = None
    best_punti_vicini = []
    best_distanze = []
    portale_i = portale_j = None

    # Prepara i dati per il processo parallelo
    tasks = [(points, i, j, DISTANZA_MAX, NUM_PUNTI_MIN) for i in range(len(points)) for j in range(i + 1, len(points))]

    # Esegui in parallelo
    with multiprocessing.Pool() as pool:
        results = pool.starmap(compute_distances, tasks)

    # Processa i risultati
    for result in results:
        if result is not None:
            i, j, punti_vicini, distanze = result
            if punti_vicini and (len(punti_vicini) > NUM_PUNTI_MIN):
                NUM_PUNTI_MIN = len(punti_vicini)
                sum_d = sum(distanze)
                dist_media = sum_d / len(distanze)
                print(f"i:{i},j:{j},NUM_PUNTI_MIN:{NUM_PUNTI_MIN},dist_media:{dist_media}")
                min_dist_media = dist_media
                best_slope, best_intercept = line_2_points(points[i], points[j])
                best_punti_vicini = punti_vicini
                best_distanze = distanze
                portale_i = i
                portale_j = j

    return min_dist_media, best_slope, best_intercept, best_punti_vicini, best_distanze, portale_i, portale_j, NUM_PUNTI_MIN


def order_by_longitudes(portals):
    # Sort the list of Point objects by their x-coordinate (longitude)
    sorted_portals = sorted(portals, key=lambda point: point['coordinates']['lng'])
    return sorted_portals

def order_by_latitudes(portals):
    # Sort the list of Point objects by their x-coordinate (longitude)
    sorted_portals = sorted(portals, key=lambda point: point['coordinates']['lat'])
    return sorted_portals


if __name__ == '__main__':
    multiprocessing.freeze_support()
    portals = load_file(FILENAME_JSON)
    portals = order_by_longitudes(portals)
    titles_portal = [portal['title'] for portal in portals]
    # Crea una lista di oggetti Point da latitudine e longitudine
    # points = [Point(d['lng'], d['lat']) for d in data]
    points = []
    for portal in portals:
        point = Point(float(portal['coordinates']['lng']), float(portal['coordinates']['lat']))
        title = portal['title']
        points.append((point, title))

    longitudes = [point[0].x for point in points]
    latitudes = [point[0].y for point in points]

    # Utilizzo della funzione parallelizzata
    min_dist_media, best_slope, best_intercept, best_punti_vicini, best_distanze, portale_i, portale_j, NUM_PUNTI_MIN = find_best_line_parallel(points, NUM_PUNTI_MIN, DISTANZA_MAX)

    #min_dist_media, best_slope, best_intercept, best_punti_vicini, best_distanze, portale_i, portale_j, n = find_best_line(points, NUM_PUNTI_MIN)
    print(
        f"La distanza media dalla retta è:{min_dist_media:.2f}mt e ci sono {len(best_punti_vicini) + 2} portali nel filotto")
    print(f"--- {time.time() - start_time:.2f} seconds ---")
    draw_close_points(best_punti_vicini, best_slope, best_intercept, portale_i, portale_j)
    print(f'{best_slope}')
    top_points = []
    p = 0
    while p < len(best_punti_vicini) - 1:
        a = best_punti_vicini[p]
        n = 1
        while True:
            if p + n < len(best_punti_vicini):
                b = best_punti_vicini[p + n]
                m, q = line_2_points(a, b)
                if are_lines_almost_parallel(m, best_slope, 0.35):
                    top_points.append(a)
                    print(f"pendenza tra {a[1]} e {b[1]} è: {m}")
                    p += n  # Move p to the position of b
                    break
                else:
                    print(f"NO BENE pendenza tra {a[1]} e {b[1]} è: {m}")
                    best_punti_vicini.pop(p + n)  # Remove b if not almost parallel
                    n -= 1
            else:
                break  # Exit the loop if there are no more points to compare
            n += 1  # Increment n to check the next point

    print(f"{portals[portale_i]['title']} A {portals[portale_j]['title']}")

    print(f"slope della retta è: {best_slope}")
    draw_close_points(top_points, best_slope, best_intercept, portale_i, portale_j)
    save_to_json(best_punti_vicini, filename='data.json')
    print(
        f"Ci sono {len(best_punti_vicini) + 2} portali nel filotto")
    create_tsp_file(best_punti_vicini)