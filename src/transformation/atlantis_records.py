import pandas as pd

df = pd.read_csv(
    "data/raw/sr.csv.gz",
    compression="gzip"
)

mask = df["official_suburb"].str.contains(
    "ATL",
    case=False,
    na=False
)

results = df.loc[
    mask,
    ["official_suburb", "latitude", "longitude"]
]

print(results["official_suburb"].value_counts())

print("\nSample Records")
print(results.head())

print("\nTotal Records")
print(len(results))