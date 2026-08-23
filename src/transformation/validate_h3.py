import pandas as pd

generated = pd.read_csv(
    "data/output/sr_with_h3.csv"
)

reference = pd.read_csv(
    "data/raw/sr_hex.csv.gz",
    compression="gzip"
)

matches = (
    generated["h3_level8_index"].astype(str)
    ==
    reference["h3_level8_index"].astype(str)
)

match_rate = matches.mean() * 100

failed = (~matches).sum()

print("\nValidation Results")
print("------------------")
print(f"Records Checked : {len(matches):,}")
print(f"Failed Matches  : {failed:,}")
print(f"Match Rate      : {match_rate:.4f}%")