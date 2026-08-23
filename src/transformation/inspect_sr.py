import pandas as pd

# Lets simple read and put our data into a readable dataset and have a view of sr data

df = pd.read_csv(
    "data/raw/sr.csv.gz",
    compression="gzip",
    nrows=5
)

print(df.columns.tolist())
print(df.head())
