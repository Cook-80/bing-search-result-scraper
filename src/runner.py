thonpython
import json
import logging
from pathlib import Path
from extractors.bing_parser import BingParser
from outputs.exporters import JSONExporter
from extractors.utils_normalization import normalize_keyword

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

CONFIG_PATH = Path(__file__).parent / "config" / "settings.example.json"
DATA_INPUT = Path(__file__).parent.parent / "data" / "input.sample.json"
DATA_OUTPUT = Path(__file__).parent.parent / "data" / "sample-output.json"

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def load_input():
    with open(DATA_INPUT, "r") as f:
        return json.load(f)

def main():
    config = load_config()
    keywords = load_input().get("keywords", [])

    parser = BingParser(
        base_url=config.get("bingBaseUrl"),
        count=config.get("resultsPerPage", 20),
        market=config.get("market", "en-US"),
        lang=config.get("language", "en"),
    )

    results = []

    for kw in keywords:
        kw_norm = normalize_keyword(kw)
        logging.info(f"Processing keyword: {kw_norm}")
        serp_data = parser.scrape(kw_norm, page_number=1)
        results.append(serp_data)

    JSONExporter.export(results, DATA_OUTPUT)
    logging.info("Scraping complete. Output saved.")

if __name__ == "__main__":
    main()