from src.extraction.extract_resolution_8 import conformance_score
from src.transformation.assign_h3 import h3_index
from src.enrichment.enrich_wind_data import enrich
from src.anonymisation.anonymise_atlantis import anonymise

import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon


def test_h3_index_handles_missing_and_valid_coordinates():
    assert h3_index(None, -70) == "0"
    assert len(h3_index(-33.9, 18.4)) == 15


def test_schema_conformance_is_row_level():
    frame = gpd.GeoDataFrame({"index": ["a"], "centroid_lat": [-33.0], "centroid_lon": [18.0], "resolution": [8]}, geometry=[Polygon([(0,0),(1,0),(1,1),(0,0)])], crs="EPSG:4326")
    schema = {"required_properties": ["index", "centroid_lat", "centroid_lon", "resolution"], "geometry_types": ["Polygon"], "expected_resolution": 8}
    assert conformance_score(frame, schema) == 100
    frame.loc[0, "resolution"] = 9
    assert conformance_score(frame, schema) < 100


def test_wind_enrichment_uses_latest_prior_observation():
    requests = pd.DataFrame({"creation_timestamp": ["2020-01-01 01:00:00"]})
    wind = pd.DataFrame({"Date Time": ["2020-01-01 00:00:00", "2020-01-01 00:30:00"], "Wind Direction": [10, 20], "Wind Speed": [1.0, 2.0]})
    result = enrich(requests, wind, max_age_hours=2)
    assert result.loc[0, "wind_direction"] == 20
    assert result.loc[0, "wind_speed"] == 2.0


def test_anonymisation_removes_coordinates_and_sensitive_columns():
    frame = pd.DataFrame({"latitude": [-33.9], "longitude": [18.4], "creation_timestamp": ["2020-01-01 01:00"], "reference_number": ["abc"], "service_type": ["waste"]})
    output, review = anonymise(frame)
    assert not {"latitude", "longitude", "creation_timestamp", "reference_number"}.intersection(output.columns)
    assert output.loc[0, "creation_time_bucket"].hour == 0
    assert "reference_number" in review.columns
    assert "anonymised_h3" in output.columns
