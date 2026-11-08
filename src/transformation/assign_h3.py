from pathlib import Path
import logging
import time

import h3
import pandas as pd

from src.extraction.download_data import ROOT, download

LOG = logging.getLogger(__name__)


def h3_index(latitude, longitude, resolution: int = 8) -> str:
    if pd.isna(latitude) or pd.isna(longitude):
        return "0"
    try:
        latitude, longitude = float(latitude), float(longitude)
    except (TypeError, ValueError):
        return "0"
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        return "0"
    return h3.latlng_to_cell(latitude, longitude, resolution)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    started = time.perf_counter()
    source_path = ROOT / "data/raw/sr.csv.gz"
    reference_path = ROOT / "data/raw/sr_hex.csv.gz"
    if not source_path.exists() or not reference_path.exists():
        import yaml
        with (ROOT / "configs/data_sources.yaml").open(encoding="utf-8") as stream:
            sources = yaml.safe_load(stream)
        for name in ("sr.csv.gz", "sr_hex.csv.gz"):
            download(sources["objects"][name], ROOT / "data/raw" / name)
    source = pd.read_csv(source_path, compression="gzip")
    reference = pd.read_csv(reference_path, compression="gzip", usecols=["h3_level8_index"])
    for column in ("latitude", "longitude"):
        if column not in source:
            raise KeyError(f"Input is missing required column: {column}")
    if len(source) != len(reference):
        raise ValueError(f"Row alignment failure: generated input has {len(source):,} rows, reference has {len(reference):,}")
    source["h3_level8_index"] = [h3_index(lat, lon) for lat, lon in zip(source.latitude, source.longitude)]
    output = ROOT / "data/output/sr_with_h3.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    source.to_csv(output, index=False)
    generated = source["h3_level8_index"].fillna("0").astype(str).reset_index(drop=True)
    expected = reference["h3_level8_index"].fillna("0").astype(str).reset_index(drop=True)
    failed = int(generated.ne(expected).sum())
    error_rate = 100.0 * failed / len(source) if len(source) else 0.0
    threshold = 1.0
    LOG.info("Rows checked: %s; failures: %s; error rate: %.4f%%", len(source), failed, error_rate)
    LOG.info("Configured maximum error rate: %.2f%%; elapsed: %.2fs", threshold, time.perf_counter() - started)
    LOG.info("Output: %s", output)
    if error_rate > threshold:
        raise ValueError(f"H3 mismatch rate {error_rate:.4f}% exceeds {threshold:.2f}%")


if __name__ == "__main__":
    main()
