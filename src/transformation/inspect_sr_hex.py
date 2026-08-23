import pandas as pd

df = pd.read_csv(
    "data/raw/sr_hex.csv.gz",
    compression="gzip",
    nrows=5
)

print(df.columns.tolist())
print(df.head())