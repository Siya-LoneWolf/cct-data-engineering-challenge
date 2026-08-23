
import pandas as pd
import h3

INPUT_FILE = "data/output/atlantis_subsample.csv"

print("Loading data...")

df = pd.read_csv(INPUT_FILE)

print(f"Records loaded: {len(df):,}")

# Lets explore anonymisation

def location_to_h3(row):
    try:
        return h3.latlng_to_cell(
            row["latitude"],
            row["longitude"],
            8
        )
    except:
        return None

df["anonymised_h3"] = df.apply(
    location_to_h3,
    axis=1
)

# Remove/drop precise coordinates
df.drop(
    columns=["latitude", "longitude"],
    inplace=True,
    errors="ignore"
)

# Temporal anonymisation detection

df["creation_timestamp"] = pd.to_datetime(
    df["creation_timestamp"],
    errors="coerce"
)

df["creation_time_bucket"] = (
    df["creation_timestamp"]
    .dt.floor("6h")
)

# Remove exact timestamp
df.drop(
    columns=["creation_timestamp"],
    inplace=True,
    errors="ignore"
)

# Now Potential PII fields

potential_pii = [
    "reference_number",
    "notification_number"
]

manual_review_cols = [
    c for c in potential_pii
    if c in df.columns
]

manual_review = df[
    manual_review_cols
].copy()

manual_review.to_csv(
    "data/output/manual_review.csv",
    index=False
)

# Remove from anonymised output
df.drop(
    columns=manual_review_cols,
    inplace=True,
    errors="ignore"
)

# Now we can Save the anonymized data/output

df.to_csv(
    "data/output/atlantis_anonymised.csv",
    index=False
)

print(
    "Saved: data/output/atlantis_anonymised.csv"
)

print(
    "Saved: data/output/manual_review.csv"
)