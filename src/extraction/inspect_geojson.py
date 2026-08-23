import geopandas as gpd

print("Reading file...")

gdf = gpd.read_file(
    "data/raw/city-hex-polygons-8-10.geojson"
)

print("\nColumns:")
print(gdf.columns.tolist())

print("\nShape:")
print(gdf.shape)

print("\nSample:")
print(gdf.head())