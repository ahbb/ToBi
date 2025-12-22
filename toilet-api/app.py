from fastapi import FastAPI
from utils import load_toilets, find_k_nearest_toilets
from pydantic import BaseModel
from geopy.geocoders import Nominatim

# python -m uvicorn app:app --reload
app = FastAPI()
geolocator = Nominatim(user_agent="BidetBuddyBot")

class Location(BaseModel):
    latitude: float
    longitude: float

# Load toilets on startup
TOILETS = load_toilets()

@app.get("/")
def root():
    return {"status": "ok", "total_toilets": len(TOILETS)}

@app.get("/all")
def all_toilets():
    return TOILETS

@app.get("/nearest")
def nearest(lat: float, lon: float, k: int = 3):
    results = find_k_nearest_toilets(lat, lon, TOILETS, k)

    output = []
    for toilet, dist in results:
        output.append({
            "toilet": toilet,
            "distances": round(dist, 2)
        })

    return {"results": output}

# Lat long -> Address
@app.post("/reverse_geocode")
def reverse_geocode(loc: Location):
    try:
        result = geolocator.reverse((loc.latitude, loc.longitude))
        return {"address": result.address}
    except Exception:
        return {"address": ""} # If geocode fails, return empty string

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "BidetBuddy API"
    }