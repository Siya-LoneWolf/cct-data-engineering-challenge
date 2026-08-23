import time
import yaml
import geopandas as gpd
from pathlib import Path

start_time = time.time()

print("Loading datasets...")

source_file = "data/raw/city-hex-polygons-8-10.geojson"
validation_file = "data/raw/city-hex-polygons-8.geojson"

source_gdf = gpd.read_file(source_file)
validation_gdf = gpd.read_file(validation_file)

print(f"Input rows: {len(source_gdf):,}")

# Extract only resolution 8
resolution8_gdf = source_gdf[
    source_gdf["resolution"] == 8
].copy()

print(f"Extracted rows: {len(resolution8_gdf):,}")

# Create output folder
Path("data/output").mkdir(exist_ok=True)

output_file = "data/output/city_hex_resolution_8.geojson"

resolution8_gdf.to_file(
    output_file,
    driver="GeoJSON"
)

print(f"Saved: {output_file}")

# Load schema config
with open("configs/schema.yaml", "r") as f:
    schema = yaml.safe_load(f)

required_columns = schema["required_columns"]

valid_columns = sum(
    1 for col in required_columns
    if col in resolution8_gdf.columns
)

conformance_score = (
    valid_columns / len(required_columns)
) * 100

# Compare with official file
row_match = len(resolution8_gdf) == len(validation_gdf)

execution_time = round(
    time.time() - start_time,
    2
)

print("\nValidation Results")
print("--------------------")
print(f"Output Rows      : {len(resolution8_gdf):,}")
print(f"Reference Rows   : {len(validation_gdf):,}")
print(f"Row Count Match  : {row_match}")
print(f"Conformance Score: {conformance_score:.2f}%")
print(f"Execution Time   : {execution_time} sec")