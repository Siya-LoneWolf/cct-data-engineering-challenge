from pathlib import Path
import logging
import os
import re

import geopandas as gpd
import pandas as pd
import requests
from shapely.ops import unary_union

from src.extraction.download_data import ROOT, download

LOG = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    raw = ROOT / "data/raw"
    requests_file = raw / "sr_hex.csv.gz"
    if not requests_file.exists():
        from src.extraction.download_data import main as download_inputs
        download_inputs()
    boundary_file = Path(os.environ.get("ATLANTIS_BOUNDARIES_FILE", raw / "suburb_boundaries.geojson"))
    boundary_url = os.environ.get("ATLANTIS_BOUNDARIES_URL")
    if not boundary_file.exists():
        if not boundary_url:
            raise RuntimeError("Official suburb boundaries are required. Set ATLANTIS_BOUNDARIES_FILE or ATLANTIS_BOUNDARIES_URL; see README.")
        download(boundary_url, boundary_file)
    boundaries = gpd.read_file(boundary_file)
    name_col = os.environ.get("ATLANTIS_BOUNDARY_NAME_COLUMN", "official_suburb")
    if name_col not in boundaries:
        raise KeyError(f"Boundary file has no {name_col!r} field; set ATLANTIS_BOUNDARY_NAME_COLUMN")
    name_pattern = os.environ.get("ATLANTIS_SUBURB_PATTERN", "Atlantis")
    mask = boundaries[name_col].astype(str).str.contains(name_pattern, case=False, na=False, regex=False)
    selected = boundaries.loc[mask]
    if selected.empty:
        raise ValueError(f"No suburb boundary matched {name_pattern!r} in {name_col!r}")
    # Compute in a local metric CRS; do not calculate planar distances in longitude/latitude.
    projected = selected.to_crs("EPSG:32734")
    suburb_centroid = unary_union(projected.geometry).centroid
    centroid_wgs84 = gpd.GeoSeries([suburb_centroid], crs="EPSG:32734").to_crs("EPSG:4326").iloc[0]
    radius_m = float(os.environ.get("ATLANTIS_RADIUS_METERS", ""))
    if radius_m <= 0:
        raise ValueError("Set ATLANTIS_RADIUS_METERS to a positive radius after documenting your interpretation of 'within 1 minute'.")
    requests_df = pd.read_csv(requests_file, compression="gzip")
    if not {"latitude", "longitude"}.issubset(requests_df.columns):
        raise KeyError("sr_hex.csv.gz must have latitude and longitude columns")
    valid = requests_df.dropna(subset=["latitude", "longitude"]).copy()
    points = gpd.GeoDataFrame(valid, geometry=gpd.points_from_xy(valid.longitude, valid.latitude), crs="EPSG:4326").to_crs("EPSG:32734")
    points["distance_m"] = points.geometry.distance(suburb_centroid)
    subset = points.loc[points.distance_m <= radius_m].copy()
    subset["centroid_latitude"] = centroid_wgs84.y
    subset["centroid_longitude"] = centroid_wgs84.x
    output = ROOT / "data/output/atlantis_subsample.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(subset.drop(columns="geometry")).to_csv(output, index=False)
    LOG.info("Suburb boundary: %s; centroid (lat, lon): %.7f, %.7f", ", ".join(selected[name_col].astype(str).unique()), centroid_wgs84.y, centroid_wgs84.x)
    LOG.info("Radius: %.1fm; selected %d of %d coordinate-valid records; wrote %s", radius_m, len(subset), len(valid), output)


if __name__ == "__main__":
    main()
