from kml2geojson import convert
import json

input_kml = 'Dataset_291125.kml'
output_geojson = "map_data.json"

# Convert KML → GeoJSON (returns list because a KML may contain multiple layers)
geojson_list = convert(input_kml)

# Write map data into map_data.json
with open(output_geojson, "w") as f:
    json.dump(geojson_list[0], f, indent=2)