import json
from geopy.distance import geodesic
from math import radians, sin, cos, sqrt, atan2
import numpy as np

# Latest data from 29/11/2025
# Getting data from toilets_bidet.json
def load_toilets():
    with open("data/toilets_bidet.json", "r") as f:
        data = json.load(f)
        toilets = []

        for feature in data["features"]:
            props =  feature["properties"]
            coords = feature["geometry"]["coordinates"]

            toilets.append({
                "name": props.get("name"),
                "description": props.get("description"),
                "lon": coords[0], # GeoJSON is [lon, lat]
                "lat": coords[1]    
            })

        return toilets

def find_k_nearest_toilets(lat, lon, toilets, k=5):
    coords = np.array([[t["lat"], t["lon"]] for t in toilets])

    # Convert user location to radians
    lat1 = np.radians(lat)
    lon1 = np.radians(lon)

    # Convert all toilet coords to radians
    lat2 = np.radians(coords[:, 0])
    lon2 = np.radians(coords[:, 1])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = (
        np.sin(dlat / 2) ** 2
        + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    )
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    R = 6371000  # Earth radius in meters
    dist = (R * c) / 1000  # All distances in vectorized form, in km

    # Find k smallest distances
    idx = np.argsort(dist)[:k]

    return [(toilets[i], float(dist[i])) for i in idx]