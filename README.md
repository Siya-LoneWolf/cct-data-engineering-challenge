# City of Cape Town Data Engineering Code Challenge

## Candidate

Siyambonga Ntolo

## Overview

This repository contains my solution to the Data Engineering sections of the City of Cape Town Data Science Unit Code Challenge.

The solution focuses on Data Engineering sections only:

## Installation guides followed

- Create a virtual environment via terminal: python -m venv .venv
- Activate: .venv\Scripts\activate ```NB: This is Windows OS```
- Install dependencies: pip install -r requirements.txt

# How to run the project:
- git clone <repo>
- cd ds_code_challenge
- python -m venv .venv
- pip install -r requirements.txt

### task 1: python src/extraction/extract_resolution_8.py
### Task 2: python src/transformation/assign_h3.py
### Task 5.1: python src/transformation/filter_atlantis_centroid.py
### Task 5.2: python src/anonymisation/anonymise_atlantis.py
### Task 5.3: python src/anonymisation/anonymise_atlantis.py

## Task 1: Data Extraction
Source Dataset: city-hex-polygons-8-10.geojson
```
## Please note that city-hex-polygons-8-10.geojson is a bit big for the browser and therefore I used python to download and save this. ```
Objective:

Extract only H3 Resolution 8 records.

Validation:

- Schema Validation
- Row Count Validation
- Conformance Score Calculation

Output: data/output/city_hex_resolution_8.geojson

Results:
- Output Rows: 3,832
- Reference Rows: 3,832
- Row Count Match: True
- Conformance Score: 100%

## Task 2: Initial Data Transformation

Source Dataset: sr.csv.gz

Objective:

Assign each service request to an H3 Resolution 8 hexagon based on latitude and longitude coordinates as stated in the CoCT Challenge.

Followed approach:

Generated H3 indices using the H3 Python library.
Used H3 Resolution 8.
Records with missing latitude or longitude values were assigned an index value of 0.
Validated generated results against the supplied reference dataset.
Validation Results:

Records Checked: 941,634
Failed Matches: 0
Match Rate: 100%
Error Threshold:

A maximum acceptable error rate of 1% was selected because H3 index generation is deterministic and should consistently produce identical results for valid coordinates.

## Task 5: Further Data Transformations - Atlantis Subsample

followed approach:
-Atlantis-related service requests were identified.
-Associated H3 Level 8 polygons were extracted.
-Polygon geometries were merged.
-A centroid was calculated computationally.
-Service requests within 100 metres of the derived centroid were selected.
-Derived Centroid
-Latitude: -33.614363450307174
-Longitude: 18.48537296729846

Records were filtered using a 5km radius (well, 2km was also fine but 5km had more) around the derived centroid result:
Subsample Size: 1,750 records 

## 5.2 - Wind Data Enrichment
An automated download process was implemented to retrieve wind direction and speed data from the City of Cape Town Open Data Portal.

The implementation includes:
-Retry logic - this was implemented to test and to see just in case the endpoint comes to life 
-Timeout handling
-Error logging
-Controlled failure behaviour
-During testing the endpoint returned HTTP 404 Client error responses, indicating that the source dataset has been moved or is no longer available via the documented URL. This was also tested directly on the web and also on Postman
-The retry and failure-handling mechanisms worked as expected.

## 5.3 - Data Anonymisation
Spatial Anonymisation
Precise latitude and longitude values were removed and replaced with H3 Resolution 8 indices.

This preserves approximate location accuracy while preventing precise address identification.

Temporal Anonymisation
Exact timestamps were aggregated into 6-hour buckets.

for emphasizes:

Original	Anonymised
2020-03-05 09:17	2020-03-05 06:00
Manual Review
Potentially sensitive identifiers were extracted into a separate file:

manual_review.csv
for human review before publication.

Output Files
atlantis_anonymised.csv
manual_review.csv

### As per the challenge requirements, the implementation emphasizes:
- Reproducibility
- Modularity
- Validation
- Logging
- Data Quality Controls
- Clean and Maintainable Code

