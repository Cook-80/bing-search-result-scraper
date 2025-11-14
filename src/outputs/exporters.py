thonpython
import json
import logging
from pathlib import Path

class JSONExporter:
    @staticmethod
    def export(data, output_path: Path):
        try:
            with open(output_path, "w") as f:
                json.dump(data, f, indent=4)
            logging.info(f"Exported JSON to {output_path}")
        except Exception as e:
            logging.error(f"Failed to export JSON: {e}")
            raise