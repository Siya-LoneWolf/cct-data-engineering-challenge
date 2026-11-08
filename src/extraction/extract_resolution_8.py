from pathlib import Path
import json
import logging
import time

import boto3
import geopandas as gpd
import yaml

from src.extraction.download_data import ROOT, download

LOG = logging.getLogger(__name__)


def select_resolution_8(client, bucket: str, key: str) -> list[dict]:
    """Use S3 Select against the GeoJSON FeatureCollection's features array."""
    response = client.select_object_content(
        Bucket=bucket,
        Key=key,
        ExpressionType="SQL",
        Expression="SELECT * FROM S3Object[*].features[*] s WHERE s.properties.resolution = 8",
        InputSerialization={"JSON": {"Type": "DOCUMENT"}},
        OutputSerialization={"JSON": {}},
    )
    payload = []
    for event in response["Payload"]:
        if "Records" in event:
            payload.append(event["Records"]["Payload"])
    text = b"".join(payload).decode("utf-8")
    if not text.strip():
        return []
    # S3 Select emits one JSON value per selected feature, usually newline-delimited.
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def load_geojson(path: Path) -> gpd.GeoDataFrame:
    return gpd.read_file(path)


def feature_frame(features: list[dict]) -> gpd.GeoDataFrame:
    return gpd.GeoDataFrame.from_features(features, crs="EPSG:4326")


def conformance_score(frame: gpd.GeoDataFrame, schema: dict) -> float:
    required = schema["required_properties"]
    checks = []
    for _, row in frame.iterrows():
        props_ok = all(name in frame.columns and row.get(name) is not None for name in required)
        geometry = row.geometry
        geometry_ok = (
            geometry is not None
            and not geometry.is_empty
            and geometry.is_valid
            and geometry.geom_type in schema["geometry_types"]
        )
        resolution_ok = row.get("resolution") == schema["expected_resolution"]
        checks.extend([props_ok, geometry_ok, resolution_ok])
    return 100.0 * sum(checks) / len(checks) if checks else 0.0


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    started = time.perf_counter()
    raw_dir = ROOT / "data/raw"
    output = ROOT / "data/output/city_hex_resolution_8.geojson"
    output.parent.mkdir(parents=True, exist_ok=True)
    with (ROOT / "configs/data_sources.yaml").open(encoding="utf-8") as source:
        sources = yaml.safe_load(source)
    with (ROOT / "configs/schema.yaml").open(encoding="utf-8") as source:
        schema = yaml.safe_load(source)
    bucket = sources["bucket"]
    key = "city-hex-polygons-8-10.geojson"
    selected = None
    try:
        client = boto3.client("s3", region_name=sources["region"])
        selected = select_resolution_8(client, bucket, key)
        result = feature_frame(selected)
        LOG.info("S3 Select returned %s features", len(result))
    except Exception as exc:  # Public object download is the documented fallback.
        LOG.warning("S3 Select unavailable (%s); falling back to downloaded GeoJSON", exc)
        combined = raw_dir / key
        reference_path = raw_dir / "city-hex-polygons-8.geojson"
        download(sources["objects"][key], combined)
        download(sources["objects"]["city-hex-polygons-8.geojson"], reference_path)
        source = load_geojson(combined)
        result = source.loc[source["resolution"] == 8].copy()
    score = conformance_score(result, schema)
    if score < schema["minimum_conformance_score"]:
        raise ValueError(f"Schema conformance {score:.2f}% is below configured minimum")
    result.to_file(output, driver="GeoJSON")
    reference_path = raw_dir / "city-hex-polygons-8.geojson"
    if not reference_path.exists():
        download(sources["objects"]["city-hex-polygons-8.geojson"], reference_path)
    reference = load_geojson(reference_path)
    result_ids = set(result["index"].astype(str))
    reference_ids = set(reference["index"].astype(str))
    same_ids = result_ids == reference_ids
    count_match = len(result) == len(reference)
    elapsed = time.perf_counter() - started
    LOG.info("Output features: %s; reference: %s", len(result), len(reference))
    LOG.info("ID sets match: %s; row counts match: %s", same_ids, count_match)
    LOG.info("Schema conformance: %.2f%% (minimum %.2f%%)", score, schema["minimum_conformance_score"])
    LOG.info("Elapsed: %.2fs; output: %s", elapsed, output)
    if not (same_ids and count_match):
        raise ValueError("Extracted resolution-8 features do not match reference index set/count")


if __name__ == "__main__":
    main()
