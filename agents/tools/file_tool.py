"""Tools for file operations."""

import json
from pathlib import Path
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)


class FileTool:
    """Tool for file operations."""

    def load_json(self, file_path: str) -> Dict[str, Any]:
        """Load JSON file."""
        with open(file_path, 'r') as f:
            return json.load(f)

    def save_json(self, file_path: str, data: Dict[str, Any]):
        """Save data to JSON file."""
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved JSON to {file_path}")

    def count_csv_rows(self, file_path: str) -> int:
        """Count rows in CSV file (excluding header)."""
        with open(file_path, 'r') as f:
            return sum(1 for _ in f) - 1  # Subtract header
