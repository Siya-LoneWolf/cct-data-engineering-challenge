import requests
from pathlib import Path

Path("data/raw").mkdir(parents=True, exist_ok=True)

files = {
    "city-hex-polygons-8-10.geojson":
    "https://cct-ds-code-challenge-input-data.s3.af-south-1.amazonaws.com/city-hex-polygons-8-10.geojson"
}

for filename, url in files.items():

    print(f"Downloading {filename}...")

    response = requests.get(url, stream=True)

    with open(f"data/raw/{filename}", "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"Completed {filename}")

print("All downloads complete.")