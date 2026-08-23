
import requests
import time
from pathlib import Path

URL = (
    "https://www.capetown.gov.za/"
    "_layouts/OpenDataPortalHandler/"
    "DownloadHandler.ashx?"
    "DocumentName=Wind_direction_and_speed_2020.ods"
)

OUTPUT = Path(
    "data/raw/Wind_direction_and_speed_2020.ods"
)

MAX_RETRIES = 10

for attempt in range(1, MAX_RETRIES + 1):

    try:

        print(f"Attempt {attempt}...")

        response = requests.get(
            URL,
            timeout=60
        )

        response.raise_for_status()

        OUTPUT.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(OUTPUT, "wb") as f:
            f.write(response.content)

        print("Download successful")

        break

    except Exception as e:

        print(
            f"Attempt {attempt} failed: {e}"
        )

        if attempt < MAX_RETRIES:
            time.sleep(10)

else:
    raise RuntimeError(
        "Failed to download wind data"
    )