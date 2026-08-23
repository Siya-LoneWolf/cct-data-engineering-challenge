import pandas as pd

df = pd.read_csv(
    "data/raw/sr.csv.gz",
    compression="gzip"
)

print(df.head())
print(df.shape)