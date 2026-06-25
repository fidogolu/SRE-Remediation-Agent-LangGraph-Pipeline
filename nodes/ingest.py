# nodes/ingest.py
"""Data ingestion node — loads and cleans raw JSON data."""
import json
from pathlib import Path

from utils import LOGGER


def ingest_node(state: dict) -> dict:
    """
    Load raw JSON data, apply basic key cleaning, and store in state.

    Args:
        state: LangGraph state containing "input_path".

    Returns:
        Dict with updated "raw_data" key.
    """
    LOGGER.info("Node 1: Loading data...")

    input_path = Path(state.get("input_path", "data/sample_data.json"))

    if not input_path.exists():
        LOGGER.error(f"Input file not found: {input_path}")
        return {"raw_data": []}

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        LOGGER.error(f"Invalid JSON in {input_path}: {e}")
        return {"raw_data": []}
    except UnicodeDecodeError as e:
        LOGGER.error(f"Encoding error in {input_path}: {e}")
        return {"raw_data": []}

    cleaned_data = [{k.strip(): v for k, v in row.items()} for row in data]
    return {"raw_data": cleaned_data}
