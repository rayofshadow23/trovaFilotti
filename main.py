import numpy as np
import matplotlib.pyplot as plt
import json
import cartopy.crs as ccrs
import cartopy.feature as cfeature

from skimage.measure import LineModelND, ransac

# Load the JSON data from "your.json"
with open("punti.json", "r") as json_file:
    json_data = json.load(json_file)

# Extract latitudes and longitudes
coordinates = np.array([(entry["lat"], entry["lng"]) for entry in json_data])

# Fit line using all data
model = LineModelND()
model.estimate(coordinates)

# Robustly fit line only using inlier data with RANSAC algorithm
model_robust, inliers = ransac(
    coordinates, LineModelND, min_samples=2, residual_threshold=1, max_trials=1000
)
outliers = inliers == False

# Generate coordinates of estimated models
line_x = np.arange(min(coordinates[:, 0]), max(coordinates[:, 0]), 0.01)
line_y = model.predict_y(line_x)
line_y_robust = model_robust.predict_y(line_x)

# Create a map with PlateCarree projection
fig = plt.figure(figsize=(10, 8))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_title("Geographic Line Model")

# Plot the line model
ax.plot(coordinates[inliers, 0], coordinates[inliers,  1], ".b", alpha=0.1, label="Inlier data")
ax.plot(coordinates[outliers, 0], coordinates[outliers, 1], ".r", alpha=0.1, label="Outlier data")
ax.plot(line_x, line_y, "-k", label="Line model from all data")
ax.plot(line_x, line_y_robust, "-b", label="Robust line model")

# Add coastlines
ax.coastlines()

# Show the plot
plt.legend(loc="lower left")
plt.show()