import pandas as pd
import geopandas as gpd

# Load service requests
sr = pd.read_csv(
    "data/raw/sr_hex.csv.gz",
    compression="gzip"
)

# Atlantis requests
atlantis = sr[
    sr["official_suburb"]
    .fillna("")
    .str.contains("ATL", case=False)
]

hex_ids = atlantis["h3_level8_index"].unique()

print(f"Unique Atlantis H3 cells: {len(hex_ids)}")

# Load polygons
hexes = gpd.read_file(
    "data/raw/city-hex-polygons-8.geojson"
)

# Match polygons
atlantis_hexes = hexes[
    hexes["index"].isin(hex_ids)
].copy()

print(f"Matched polygons: {len(atlantis_hexes)}")

# Create merged geometry
merged = atlantis_hexes.unary_union

centroid = merged.centroid

print("\nCentroid")
print("Latitude :", centroid.y)
print("Longitude:", centroid.x)