import requests

API_KEY = "fffbf69aa5004d2d88b154502260204"


def get_weather(lat, lon):
    url = f"https://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={lat},{lon}&days=3"

    try:
        res = requests.get(url, timeout=5)
        data = res.json()
    except:
        return {
            "Temperature": None,
            "Humidity": None,
            "Rainfall": None,
            "error": "API request failed"
        }

    if "error" in data:
        return {
            "Temperature": None,
            "Humidity": None,
            "Rainfall": None,
            "error": data["error"]["message"]
        }

    current = data.get("current", {})
    forecast = data.get("forecast", {}).get("forecastday", [])

    temp = current.get("temp_c")
    humidity = current.get("humidity")

    # 🔥 SUM OF NEXT 3 DAYS RAINFALL
    rainfall = sum(day["day"]["totalprecip_mm"] for day in forecast)

    if temp is None or humidity is None:
        return {
            "Temperature": None,
            "Humidity": None,
            "Rainfall": None,
            "error": "Incomplete weather data"
        }

    return {
        "Temperature": float(temp),
        "Humidity": float(humidity),
        "Rainfall": float(round(rainfall, 2))
    }