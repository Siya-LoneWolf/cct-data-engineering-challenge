"""Backward-compatible entry point; prefer ``python -m src.extraction.download_data``."""
from src.extraction.download_data import main

if __name__ == "__main__":
    main()
