import geopandas as gpd

url = "https://opendata.arcgis.com/datasets/5e5b0f2f8d5e4c4a9e2b3f2c4d8c9aef_0.geojson"

print("Downloading suburb boundaries...")

gdf = gpd.read_file(url)

print(gdf.columns.tolist())

print(gdf.head())

print(f"Rows: {len(gdf)}")