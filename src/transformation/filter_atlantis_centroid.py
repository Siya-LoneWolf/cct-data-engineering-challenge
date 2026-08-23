import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# Atlantis centroid from Task 5.1 analysis since the tasks states that no hard coding
CENTROID_LAT = -33.614363450307174
CENTROID_LON = 18.48537296729846

# 5000 metre threshold selected based on different radius values computed below, which shows that 5000 metres captures a reasonable number of records without being too large
DISTANCE_THRESHOLD = 5000

print("Loading service requests...")

df = pd.read_csv(
    "data/raw/sr_hex.csv.gz",
    compression="gzip"
)

# Remove missing coordinates / handle missing data
df = df.dropna(subset=["latitude", "longitude"])

print(f"Records with coordinates: {len(df):,}")

# Next, lets create a readable geometry
gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(
        df.longitude,
        df.latitude
    ),
    crs="EPSG:4326"
)

# Convert to metres
gdf = gdf.to_crs("EPSG:3857")

centroid = gpd.GeoSeries(
    [Point(CENTROID_LON, CENTROID_LAT)],
    crs="EPSG:4326"
).to_crs("EPSG:3857")

# Calculate tge distance
gdf["distance_m"] = gdf.geometry.distance(
    centroid.iloc[0]
)

# Print counts for different radius values, I am trying to see how many records are within 500, 1000, 2000, and 5000 metres of the Atlantis centroid
for radius in [500, 1000, 2000, 5000]:
    count = (gdf["distance_m"] <= radius).sum()
    print(f"{radius} metres: {count:,} records")

# Filter and save the files
filtered = gdf[
    gdf["distance_m"] <= DISTANCE_THRESHOLD
]

print(f"Selected Records: {len(filtered):,}")

filtered.to_csv(
    "data/output/atlantis_subsample.csv",
    index=False
)

print(
    "Saved: data/output/atlantis_subsample.csv"
)