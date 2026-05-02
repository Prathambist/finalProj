import geopandas as gpd
from shapely.geometry import Point

# ---------------- LOAD SHAPEFILE ----------------
soil_df = gpd.read_file("shapefiles/soilparent.shp")

# Ensure correct coordinate system
if soil_df.crs != "EPSG:4326":
    soil_df = soil_df.to_crs("EPSG:4326")


# ---------------- SOIL TYPE CONVERSION ----------------
# Shapefile → Dataset values
SOIL_TYPE_CONVERSION = {
    "CMu": "Clay", "CMe": "Clay", "CMx": "Clay", "CMg": "Clay", "CMo": "Clay",
    "RGd": "Sandy", "RGe": "Sandy", "LPi": "Sandy",
    "LVx": "Loamy", "FLc": "Loamy", "PHh": "Loamy", "PHc": "Loamy",
    "GLe": "Silt",
}


# ---------------- BASE SOIL RULES ----------------
PARENT_MATERIAL_MAP = {
    "UF1": {"ph": (6.5, 7.5), "n": "high", "p": "high", "k": "high", "oc": "high"},
    "UF2": {"ph": (6.0, 7.0), "n": "medium", "p": "medium", "k": "medium", "oc": "medium"},
    "UC1": {"ph": (5.0, 6.0), "n": "low", "p": "low", "k": "low", "oc": "low"},
    "UL2": {"ph": (6.5, 7.5), "n": "medium", "p": "medium", "k": "medium", "oc": "high"},
    "MA1": {"ph": (6.5, 7.0), "n": "high", "p": "high", "k": "high", "oc": "high"},
    "MA2": {"ph": (6.0, 6.5), "n": "medium", "p": "medium", "k": "medium", "oc": "medium"},
    "MB1": {"ph": (5.5, 6.5), "n": "medium", "p": "medium", "k": "medium", "oc": "medium"},
    "SC2": {"ph": (4.5, 5.5), "n": "low", "p": "low", "k": "low", "oc": "medium"},
    "RK":  {"ph": (4.0, 5.5), "n": "very_low", "p": "low", "k": "low", "oc": "very_low"},
    "GG":  {"ph": (5.0, 6.0), "n": "low", "p": "low", "k": "medium", "oc": "low"},
}


# ---------------- CONVERSION FUNCTIONS ----------------

def convert_npk(level):
    mapping = {
        "very_low": 25,
        "low": 50,
        "medium": 90,
        "high": 130
    }
    return mapping.get(level, 90)


def convert_oc(level):
    mapping = {
        "very_low": 0.3,
        "low": 0.5,
        "medium": 0.8,
        "high": 1.2
    }
    return mapping.get(level, 0.8)


# ---------------- CORE SOIL CALCULATION ----------------

def calculate_soil(parent, soil, elev, slope):

    base = PARENT_MATERIAL_MAP.get(parent, PARENT_MATERIAL_MAP["UF2"])

    # ---- Soil pH ----
    ph = (base["ph"][0] + base["ph"][1]) / 2

    # Elevation adjustment
    if elev > 3000:
        ph -= 0.5
    elif elev > 2000:
        ph -= 0.3
    elif elev > 1000:
        ph -= 0.1

    ph = round(max(4.5, min(8.0, ph)), 2)

    # ---- Nutrients ----
    nitrogen = convert_npk(base["n"])
    phosphorus = convert_npk(base["p"])
    potassium = convert_npk(base["k"])

    # Slope impact
    if slope > 30:
        nitrogen *= 0.7
        phosphorus *= 0.7
        potassium *= 0.7
    elif slope > 20:
        nitrogen *= 0.85

    nitrogen = int(nitrogen)
    phosphorus = int(phosphorus)
    potassium = int(potassium)

    # ---- Organic Carbon ----
    organic_carbon = round(convert_oc(base["oc"]), 2)

    # ---- Soil Type ----
    soil_type = SOIL_TYPE_CONVERSION.get(soil, "Loamy")

    return {
        "Soil_Type": soil_type,
        "Soil_pH": float(ph),
        "Organic_Carbon": float(organic_carbon),
        "Nitrogen_Level": nitrogen,
        "Phosphorus_Level": phosphorus,
        "Potassium_Level": potassium
    }


# ---------------- MAIN FUNCTION ----------------

def get_soil_data(lat, lon):

    try:
        point = Point(lon, lat)
        match = soil_df[soil_df.geometry.intersects(point)]

        if match.empty:
            return {"error": "Location not found in shapefile"}

        row = match.iloc[0]

        return calculate_soil(
            str(row["Parent_Mat"]),
            str(row["Dominant_S"]),
            int(row["Elev_max"]),
            float(row["Slope_med"])
        )

    except Exception as e:
        return {"error": str(e)}