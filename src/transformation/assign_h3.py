import time
import pandas as pd
import h3

start_time = time.time()

print("Loading service requests...")

df = pd.read_csv(
    "data/raw/sr.csv.gz",
    compression="gzip"
)

print(f"Rows loaded: {len(df):,}")

def get_h3_index(row):

    lat = row["latitude"]
    lon = row["longitude"]

    if pd.isna(lat) or pd.isna(lon):
        return "0"

    try:
        return h3.latlng_to_cell(lat, lon, 8)

    except Exception:
        return "0"


print("Generating H3 indexes...")

df["h3_level8_index"] = df.apply(
    get_h3_index,
    axis=1
)

df.to_csv(
    "data/output/sr_with_h3.csv",
    index=False
)

execution_time = round(
    time.time() - start_time,
    2
)

print("\nCompleted")
print(f"Rows processed : {len(df):,}")
print(f"Execution time : {execution_time} sec")