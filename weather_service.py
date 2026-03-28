import openmeteo_requests
import requests_cache
from retry_requests import retry


cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)

openmeteo = openmeteo_requests.Client(session=retry_session)


def get_weather(lat, lon):

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": [
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation"
        ]
    }

    responses = openmeteo.weather_api(url, params=params)

    response = responses[0]

    hourly = response.Hourly()

    temperature = hourly.Variables(0).ValuesAsNumpy()
    humidity = hourly.Variables(1).ValuesAsNumpy()
    precipitation = hourly.Variables(2).ValuesAsNumpy()

    return {
        "temperature_avg": float(temperature.mean()),
        "humidity_avg": float(humidity.mean()),
        "rainfall_total": float(precipitation.sum())
    }