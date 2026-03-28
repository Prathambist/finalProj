from fastapi import FastAPI
from soil import lookup_soil
from weather_service import get_weather

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Soil + Weather Data API for ML Model"}


@app.get("/data")
def get_data(lat: float, lon: float, crop: str, season: str):

    soil_data = lookup_soil(lat, lon)

    if "error" in soil_data:
        return soil_data

    weather = get_weather(lat, lon)

    return {
        "location": {
            "lat": lat,
            "lon": lon
        },
        "crop": crop,
        "season": season,
        "soil_data": soil_data,
        "weather_data": weather
    }