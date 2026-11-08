# Data engineering challenge — reproducible run guide

This repository contains the Data Engineering parts of the City of Cape Town challenge (Tasks 1, 2 and 5). It is not a solution to the Data Science, Analyst or Visualisation tasks.

## Requirements

- Python 3.10+ (3.11 recommended)
- Internet access for the public challenge data and wind-data endpoint
- AWS credentials are not required for the public downloads. S3 Select may require a permitted AWS identity; Task 1 falls back to the public object download if Select is unavailable.

## Fresh-clone setup

```bash
git clone https://github.com/Siya-LoneWolf/cct-data-engineering-challenge.git
cd cct-data-engineering-challenge
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m src.extraction.download_data
```

The download command places challenge inputs under the ignored `data/raw/` directory. Generated results and logs are written under ignored `data/output/` and `logs/` directories. Do not commit raw request data or the manual-review file.

## Run the engineering tasks

Commands below are run from the repository root:

```bash
# Task 1: S3 Select (with public-file fallback), schema score and reference validation
python -m src.extraction.extract_resolution_8

# Task 2: generate H3 indices, compare to sr_hex.csv.gz, and enforce the error threshold
python -m src.transformation.assign_h3
```

Task 5 has an external-data dependency and an ambiguity in the challenge wording (“within 1 minute” of a centroid is not a distance unit). The pipeline deliberately requires the boundary source and a radius to be selected rather than silently claiming that 5 km meets that condition. Obtain an official suburb-boundary GeoJSON, set `ATLANTIS_BOUNDARIES_FILE` to its path (or `ATLANTIS_BOUNDARIES_URL` to a trusted downloadable GeoJSON URL), and set `ATLANTIS_RADIUS_METERS` to the documented interpretation of the requested proximity. For 5.2, An automated download process was implemented to retrieve wind direction and speed data from the City of Cape Town Open Data Portal.

The implementation includes:
-Retry logic - this was implemented to test and to see just in case the endpoint comes to life 
-Timeout handling
-Error logging
-Controlled failure behaviour
-During testing the endpoint returned HTTP 404 Client error responses, indicating that the source dataset has been moved or is no longer available via the documented URL. This was also tested directly on the web and also on Postman
-The retry and failure-handling mechanisms worked as expected. Then run:

```bash
python -m src.transformation.filter_atlantis_centroid
python -m src.enrichment.download_wind_data
python -m src.enrichment.enrich_wind_data
python -m src.anonymisation.anonymise_atlantis
```

The boundary must contain an official suburb-name field; override its name with `ATLANTIS_BOUNDARY_NAME_COLUMN` if needed. The default suburb name match is “Atlantis”. The wind portal endpoint has returned 404 during prior testing. The downloader retries transient errors, fails promptly for permanent client errors, and does not fabricate wind values. If the endpoint remains unavailable, Task 5.2 cannot be represented as completed; restore a valid official source before running the enrichment step.

## Validation and tests

```bash
pytest -q
```

Task 1 writes `data/output/city_hex_resolution_8.geojson` and prints schema conformance, reference comparison, and elapsed time. Task 2 writes `data/output/sr_with_h3.csv` and checks positional row counts and H3 matches against the supplied reference, failing when the configured 1% error threshold is exceeded. The threshold is intentionally strict because H3 assignment is deterministic for valid coordinate pairs.

Task 5 anonymisation uses H3 resolution 8 (roughly 500 m cell scale) and floors timestamps to six-hour intervals. Removed potentially identifying columns are written to `data/output/manual_review.csv` for restricted human review. That file can contain personal data and must not be published or committed. Review and remove any additional identifying fields before release; H3 and time bucketing reduce precision but do not alone guarantee anonymity.

## Configuration and known limits

- `configs/schema.yaml` defines Task 1 required properties and the minimum schema conformance score.
- `configs/data_sources.yaml` lists the public S3 object URLs.
- Task 5 requires an official boundary dataset not included in the challenge input list and a deliberate interpretation of the proximity wording. No fabricated centroid or unverified boundary URL is provided.
- Wind enrichment requires the City’s 2020 wind-data file and recognizable timestamp, direction, and speed columns. The implementation uses the latest prior observation within a configured age limit.
- The challenge requests `AI_log.md`; it records the assistance currently disclosed. Add any further AI prompts, model details, and token counts if applicable. Never invent retrospective token counts.
