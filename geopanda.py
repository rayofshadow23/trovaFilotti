import json
from shapely.geometry import Point, LineString
import geopandas as gpd
from scipy.spatial import KDTree
import numpy as np
import matplotlib.pyplot as plt


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
linea_approssimante = LineString(gdf['geometry'][:2])

# Calcola la distanza di ogni punto dalla linea approssimante
gdf['distanza_dalla_linea'] = gdf['geometry'].apply(lambda punto: punto.distance(linea_approssimante))

# Filtra i punti che sono entro la DISTANZA_MAX dalla linea approssimante
punti_vicini = gdf[gdf['distanza_dalla_linea'] <= DISTANZA_MAX]

# Utilizza KDTree per trovare i punti che rispettano la DISTANZA_MIN_PUNTI
coordinate = np.array(list(zip(punti_vicini['lat'], punti_vicini['lng'])))
tree = KDTree(coordinate)
punti_allineati = []

for i, punto in enumerate(coordinate):
    indici_vicini = tree.query_ball_point(punto, r=DISTANZA_MIN_PUNTI)
    if len(indici_vicini) > 1:  # Esclude se stesso
        continue
    punti_allineati.append(punti_vicini.iloc[i])

# Verifica se ci sono almeno NUM_PUNTI_MIN punti allineati
if len(punti_allineati) >= NUM_PUNTI_MIN:
    print(f"Trovati almeno {NUM_PUNTI_MIN} punti allineati.")
else:
    print(f"Non sono stati trovati abbastanza punti allineati.")

# Crea un plot dei punti e della linea approssimante
fig, ax = plt.subplots()

# Aggiungi i punti al plot
gdf.plot(ax=ax, kind='scatter', x='lng', y='lat', label='Punti', color='blue')

# Aggiungi la linea approssimante al plot
x_coords, y_coords = zip(*linea_approssimante.coords)
ax.plot(x_coords, y_coords, color='red', linewidth=2, label='Linea Approssimante')

# Aggiungi i punti allineati al plot, se presenti
if punti_allineati:
    gdf_allineati = gpd.GeoDataFrame(punti_allineati, geometry='geometry')
    gdf_allineati.plot(ax=ax, kind='scatter', x='lng', y='lat', label='Punti Allineati', color='green')

# Imposta i titoli e le etichette
ax.set_title('Punti e Linea Approssimante')
ax.set_xlabel('Longitudine')
ax.set_ylabel('Latitudine')
ax.legend()


# Aggiungi le descrizioni e le distanze dei punti al plot
for idx, row in gdf.iterrows():
    descrizione = f"{row['title']} ({row['distanza_dalla_linea']:.6f} m)"
    ax.annotate(descrizione, (row['lng'], row['lat']), textcoords="offset points", xytext=(0,10), ha='center')

# Mostra il plot con le descrizioni e le distanze
plt.show()
