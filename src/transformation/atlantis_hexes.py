import pandas as pd

df = pd.read_csv(
    "data/raw/sr_hex.csv.gz",
    compression="gzip"
)

atlantis = df[
    df["official_suburb"]
    .fillna("")
    .str.contains("ATL", case=False)
]

print("Rows:", len(atlantis))

print("\nUnique H3 cells:")
print(
    atlantis["h3_level8_index"]
    .value_counts()
    .head(20)
)