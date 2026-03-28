import geopandas as gpd
from shapely.geometry import Point

# Load shapefile
soil_df = gpd.read_file("shapefiles/soilparent.shp")

# Ensure correct CRS
if soil_df.crs != "EPSG:4326":
    soil_df = soil_df.to_crs("EPSG:4326")


# Parent material soil properties
PARENT_MATERIAL_MAP = {
    "UF2": {
        "ph": (6.0, 7.0),
        "nitrogen": "medium",
        "phosphorus": "medium",
        "potassium": "medium",
        "organic_matter": "medium"
    },
    "MA1": {
        "ph": (6.5, 7.0),
        "nitrogen": "high",
        "phosphorus": "high",
        "potassium": "high",
        "organic_matter": "high"
    }
}


# Soil type modifiers
SOIL_TYPE_MAP = {
    "CMe": {
        "ph_adjust": 0,
        "drainage": "good",
        "fertility": "medium"
    },
    "GLe": {
        "ph_adjust": -0.2,
        "drainage": "very_poor",
        "fertility": "medium"
    }
}


# Landform effects
LANDFORM_MAP = {
    "TM": {
        "runoff_risk": "medium",
        "erosion": "medium"
    },
    "LP": {
        "runoff_risk": "low",
        "erosion": "very_low"
    }
}


def calculate_soil(parent, soil, landform, elev, slope):

    base = PARENT_MATERIAL_MAP.get(parent, PARENT_MATERIAL_MAP["UF2"])

    modifier = SOIL_TYPE_MAP.get(
        soil,
        {"ph_adjust": 0, "drainage": "moderate", "fertility": "medium"}
    )

    terrain = LANDFORM_MAP.get(
        landform,
        {"runoff_risk": "medium", "erosion": "medium"}
    )

    # Calculate pH
    ph = (base["ph"][0] + base["ph"][1]) / 2
    ph += modifier["ph_adjust"]

    if elev > 3000:
        ph -= 0.5
    elif elev > 2000:
        ph -= 0.3
    elif elev > 1000:
        ph -= 0.1

    ph = round(ph, 1)

    return {
        "ph_estimated": float(ph),
        "nitrogen_level": str(base["nitrogen"]),
        "phosphorus_level": str(base["phosphorus"]),
        "potassium_level": str(base["potassium"]),
        "organic_matter": str(base["organic_matter"]),
        "drainage": str(modifier["drainage"]),
        "fertility": str(modifier["fertility"]),
        "runoff_risk": str(terrain["runoff_risk"]),
        "erosion_risk": str(terrain["erosion"]),
        "parent_material_code": str(parent),
        "soil_type_code": str(soil),
        "landform_code": str(landform),
        "elevation_max_m": int(elev),
        "slope_median_deg": float(slope)
    }


def lookup_soil(lat, lon):

    point = Point(lon, lat)

    # Use intersects instead of contains
    match = soil_df[soil_df.geometry.intersects(point)]

    if match.empty:
        return {"error": "Location not found in soil dataset"}

    row = match.iloc[0]

    parent = str(row["Parent_Mat"])
    soil = str(row["Dominant_S"])
    landform = str(row["Landform"])
    elev = int(row["Elev_max"])
    slope = float(row["Slope_med"])

    return calculate_soil(parent, soil, landform, elev, slope)