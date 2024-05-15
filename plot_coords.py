import json
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
import csv
import haversine as hv

def plot_coordinates(filename):
    with open(filename, 'r') as json_file:
        data = json.load(json_file)

    # Extract latitude and longitude coordinates and portal names
    coordinates = np.array([(point['lat'], point['lng']) for point in data])
    portal_names = [point['title'] for point in data]

    # Compute the regression line
    m, b = np.polyfit(coordinates[:, 1], coordinates[:, 0], 1)  # 1 denotes linear regression

    # Create a world map
    fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()})
    ax.coastlines()

    # Plot the coordinates
    ax.plot(coordinates[:, 1], coordinates[:, 0], 'bo', markersize=0.5, transform=ccrs.PlateCarree())

    # Generate x values for the regression line based on the longitude range
    reg_x = np.linspace(min(coordinates[:, 1]), max(coordinates[:, 1]), len(data))

    # Calculate corresponding y values for the regression line
    reg_y = m * reg_x + b
    print("function is " + str(m) +"x " + str(b))

    # Plot the regression line
    ax.plot(reg_x, reg_y, color='red', linewidth=1, transform=ccrs.PlateCarree())

    plt.title('Coordinates on World Map with Regression Line')
    plt.savefig('paderno_with_regression.png')  # Save the plot as "paderno_with_regression.png"
    plt.show()
    distance_km = hv.haversine(coordinates[0, 1], coordinates[0, 0], coordinates[1, 1], coordinates[1, 0])
    print("la distanza tra due punti è:" + str(distance_km*1000))
    # Calculate distances from the regression line and write to CSV
    with open('distances.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Portal Name', 'Distance from Regression Line'])

        for i, point in enumerate(data):
            distance = np.abs(m*coordinates[i, 1] - coordinates[i, 0] + b) / np.sqrt(m**2 + 1)
            writer.writerow([point['title'], distance])

# Usage: Replace 'punti.json' with the actual filename
plot_coordinates('punti.json')

