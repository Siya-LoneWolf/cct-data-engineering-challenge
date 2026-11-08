from pathlib import Path
import logging
import re

import h3
import pandas as pd

from src.extraction.download_data import ROOT

LOG = logging.getLogger(__name__)
PII_PATTERN = re.compile(r"name|phone|mobile|email|address|street|contact|identity|\bid\b|reference|notification_number|resident|complainant", re.I)


def anonymise(frame: pd.DataFrame, timestamp_column: str | None = None):
    result = frame.copy()
    latitude = next((c for c in result.columns if c.lower() == "latitude"), None)
    longitude = next((c for c in result.columns if c.lower() == "longitude"), None)
    if latitude and longitude:
        result["anonymised_h3"] = [
            h3.latlng_to_cell(float(lat), float(lon), 8) if pd.notna(lat) and pd.notna(lon) else None
            for lat, lon in zip(result[latitude], result[longitude])
        ]
        result = result.drop(columns=[latitude, longitude])
    timestamp_column = timestamp_column or next((c for c in result.columns if c.lower() in {"creation_timestamp", "created_at", "notification_created"}), None)
    if timestamp_column:
        timestamps = pd.to_datetime(result[timestamp_column], errors="coerce", utc=True)
        result["creation_time_bucket"] = timestamps.dt.floor("6h")
        result = result.drop(columns=[timestamp_column])
    pii_columns = [c for c in result.columns if PII_PATTERN.search(str(c))]
    review = result[pii_columns].copy()
    review.insert(0, "source_row_number", range(1, len(result) + 1))
    review.insert(1, "review_reason", "Potential direct or indirect identifier; assess and manually redact before publication")
    result = result.drop(columns=pii_columns)
    return result, review


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    input_path = ROOT / "data/output/atlantis_wind_enriched.csv"
    if not input_path.exists():
        raise FileNotFoundError("Run wind enrichment first; anonymisation must apply to the augmented subsample")
    data = pd.read_csv(input_path)
    anonymised, review = anonymise(data)
    output_dir = ROOT / "data/output"
    output_dir.mkdir(parents=True, exist_ok=True)
    anonymised.to_csv(output_dir / "atlantis_anonymised.csv", index=False)
    review.to_csv(output_dir / "manual_review.csv", index=False)
    LOG.info("Anonymised rows: %d; records for restricted manual review: %d", len(anonymised), len(review))
    LOG.warning("manual_review.csv may contain personal data; restrict access and do not publish or commit it")


if __name__ == "__main__":
    main()
