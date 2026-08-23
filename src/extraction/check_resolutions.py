import geopandas as gpd

gdf = gpd.read_file(
    "data/raw/city-hex-polygons-8-10.geojson"
)

print(gdf["resolution"].value_counts())