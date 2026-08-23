import pandas as pd

df = pd.read_csv(
    "data/raw/sr.csv.gz",
    compression="gzip",
    usecols=["official_suburb"]
)

suburbs = (
    df["official_suburb"]
    .dropna()
    .astype(str)
    .sort_values()
    .unique()
)

for suburb in suburbs:
    if "ATL" in suburb.upper():
        print(suburb)