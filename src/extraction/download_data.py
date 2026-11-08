from pathlib import Path
import logging
import time

import requests
import yaml

ROOT = Path(__file__).resolve().parents[2]
LOG = logging.getLogger(__name__)


def download(url: str, destination: Path, retries: int = 3) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.stat().st_size:
        LOG.info("Already present: %s", destination)
        return
    for attempt in range(1, retries + 1):
        try:
            with requests.get(url, stream=True, timeout=(15, 120)) as response:
                response.raise_for_status()
                temporary = destination.with_suffix(destination.suffix + ".part")
                with temporary.open("wb") as output:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            output.write(chunk)
                temporary.replace(destination)
            LOG.info("Downloaded %s", destination)
            return
        except requests.RequestException:
            if attempt == retries:
                raise
            time.sleep(min(2 ** attempt, 10))


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    with (ROOT / "configs/data_sources.yaml").open(encoding="utf-8") as source:
        config = yaml.safe_load(source)
    for filename, url in config["objects"].items():
        download(url, ROOT / "data/raw" / filename)


if __name__ == "__main__":
    main()
