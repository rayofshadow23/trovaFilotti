import math
from itertools import permutations
import matplotlib.pyplot as plt

# Haversine formula to calculate the distance between two points on the Earth
def haversine(coord1, coord2):
    R = 6371  # Radius of the Earth in kilometers
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

# Function to calculate the total distance of a path
def total_distance(path):
    distance = 0
    for i in range(len(path) - 1):
        distance += haversine(path[i], path[i + 1])
    return distance

# Read the coordinates from the file with error handling
locations = []
with open('C:\\Users\\c330439\\Downloads\\prova.txt', 'r') as f:
    for line in f:

        try:
            parts = line.strip().split(',')
            if len(parts) == 2:
                locations.append(tuple(map(float, parts)))
            else:
                print(f"Skipping invalid line: {line.strip()}")
        except ValueError:
            print(f"Skipping invalid line: {line.strip()}")

# Ensure we have at least one valid location
if not locations:
    raise ValueError("No valid locations found in the file.")

# Define the starting point A (assuming it's the first location in the list)
start_point = locations[0]

# Generate all possible paths starting from the starting point
paths = permutations(locations[1:])

# Find the path with the minimum total distance
best_path = min(paths, key=lambda path: total_distance([start_point] + list(path)))

# Add the starting point to the best path
best_path = [start_point] + list(best_path)

# Print the best path
print("Best path to visit all locations:")
print(best_path)

# Plotting the best path
lats, lons = zip(*best_path)
plt.figure(figsize=(10, 6))
plt.plot(lons, lats, marker='o')
for i, (lat, lon) in enumerate(best_path):
    plt.text(lon, lat, f'{i}', fontsize=12)
plt.title('Best Path to Visit All Locations')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.grid(True)
plt.show()
