from pathlib import Path
import logging
import os
import time

import requests

from src.extraction.download_data import ROOT

LOG = logging.getLogger(__name__)
URL = os.environ.get("WIND_DATA_URL", "https://www.capetown.gov.za/_layouts/OpenDataPortalHandler/DownloadHandler.ashx?DocumentName=Wind_direction_and_speed_2020.ods")
OUTPUT = ROOT / "data/raw/Wind_direction_and_speed_2020.ods"


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(1, 4):
        try:
            response = requests.get(URL, timeout=(15, 60))
            if response.status_code == 404:
                raise RuntimeError("Wind-data endpoint returned HTTP 404; locate the current official dataset URL and set WIND_DATA_URL")
            response.raise_for_status()
            if not response.content:
                raise RuntimeError("Wind-data response was empty")
            temp = OUTPUT.with_suffix(OUTPUT.suffix + ".part")
            temp.write_bytes(response.content)
            temp.replace(OUTPUT)
            LOG.info("Downloaded wind data to %s (%d bytes)", OUTPUT, OUTPUT.stat().st_size)
            return
        except RuntimeError:
            raise
        except requests.RequestException as exc:
            if attempt == 3:
                raise RuntimeError(f"Wind-data download failed after {attempt} attempts: {exc}") from exc
            wait = 2 ** attempt
            LOG.warning("Transient download failure (attempt %d/3): %s; retrying in %ds", attempt, exc, wait)
            time.sleep(wait)


if __name__ == "__main__":
    main()
