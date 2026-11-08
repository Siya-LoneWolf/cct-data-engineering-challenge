"""Backward-compatible validation command for the Task 2 generated output."""
from pathlib import Path
import logging

import pandas as pd

from src.extraction.download_data import ROOT


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    generated = pd.read_csv(ROOT / "data/output/sr_with_h3.csv", usecols=["h3_level8_index"])
    reference = pd.read_csv(ROOT / "data/raw/sr_hex.csv.gz", compression="gzip", usecols=["h3_level8_index"])
    if len(generated) != len(reference):
        raise ValueError("Generated/reference row counts differ; row-wise comparison is invalid")
    mismatches = generated.h3_level8_index.fillna("0").astype(str).ne(reference.h3_level8_index.fillna("0").astype(str)).sum()
    rate = 100 * mismatches / len(generated) if len(generated) else 0
    logging.info("Checked=%d mismatches=%d match_rate=%.4f%%", len(generated), mismatches, 100-rate)
    if rate > 1:
        raise ValueError(f"Mismatch rate {rate:.4f}% exceeds 1%")


if __name__ == "__main__":
    main()
