from pathlib import Path
import logging
import os
import re

import pandas as pd

from src.extraction.download_data import ROOT

LOG = logging.getLogger(__name__)


def normalized(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(text).lower())


def find_column(columns, candidates):
    by_normalized = {normalized(column): column for column in columns}
    for candidate in candidates:
        if candidate in by_normalized:
            return by_normalized[candidate]
    for key, column in by_normalized.items():
        if any(candidate in key for candidate in candidates):
            return column
    raise KeyError(f"Could not identify a column matching {candidates}; available: {list(columns)}")


def enrich(requests_df: pd.DataFrame, wind_df: pd.DataFrame, max_age_hours: float = 3) -> pd.DataFrame:
    request_time_col = os.environ.get("REQUEST_TIMESTAMP_COLUMN", "creation_timestamp")
    if request_time_col not in requests_df:
        raise KeyError(f"Service request data is missing {request_time_col!r}; set REQUEST_TIMESTAMP_COLUMN")
    time_col = find_column(wind_df.columns, ["datetime", "timestamp", "dateandtime", "date"])
    direction_col = find_column(wind_df.columns, ["winddirection", "direction"])
    speed_col = find_column(wind_df.columns, ["windspeed", "speed"])
    requests_copy = requests_df.copy()
    wind = wind_df[[time_col, direction_col, speed_col]].copy()
    requests_copy[request_time_col] = pd.to_datetime(requests_copy[request_time_col], errors="coerce", utc=True)
    wind[time_col] = pd.to_datetime(wind[time_col], errors="coerce", utc=True)
    wind = wind.dropna(subset=[time_col]).rename(columns={time_col: "_wind_time", direction_col: "wind_direction", speed_col: "wind_speed"})
    wind = wind.sort_values("_wind_time").drop_duplicates("_wind_time", keep="last")
    left = requests_copy.assign(_row_order=range(len(requests_copy))).sort_values(request_time_col)
    merged = pd.merge_asof(left, wind, left_on=request_time_col, right_on="_wind_time", direction="backward", tolerance=pd.Timedelta(hours=max_age_hours))
    merged["wind_observation_time"] = merged.pop("_wind_time")
    return merged.sort_values("_row_order").drop(columns="_row_order").reset_index(drop=True)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    requests_path = ROOT / "data/output/atlantis_subsample.csv"
    wind_path = ROOT / "data/raw/Wind_direction_and_speed_2020.ods"
    if not requests_path.exists():
        raise FileNotFoundError("Run src.transformation.filter_atlantis_centroid first")
    if not wind_path.exists():
        raise FileNotFoundError("Run src.enrichment.download_wind_data first")
    requests_df = pd.read_csv(requests_path)
    wind_df = pd.read_excel(wind_path, engine="odf")
    max_age = float(os.environ.get("WIND_MAX_AGE_HOURS", "3"))
    result = enrich(requests_df, wind_df, max_age)
    output = ROOT / "data/output/atlantis_wind_enriched.csv"
    result.to_csv(output, index=False)
    matched = int(result.wind_observation_time.notna().sum())
    LOG.info("Wind matched %d/%d requests; max observation age %.1f hours; output %s", matched, len(result), max_age, output)
    if len(result) and matched == 0:
        raise ValueError("No wind observations joined; verify timestamp/column formats and source dataset")


if __name__ == "__main__":
    main()
