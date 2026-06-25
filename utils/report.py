# utils/report.py
"""JSON serialization helpers for pipeline reports."""
import json
from pathlib import Path

from models.schemas import ActionItem
from utils.logger import LOGGER


class CustomJSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder for Pydantic V2 models.

    Handles serialization of ActionItem objects
    which are not natively serializable by the standard encoder.
    """

    def default(self, obj):
        if isinstance(obj, ActionItem):
            return obj.model_dump()
        return super().default(obj)


def save_report(report: dict, output_path: Path) -> None:
    """
    Save the final report to disk as JSON.

    Args:
        report:      The final report dictionary to save.
        output_path: Destination file path.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False, cls=CustomJSONEncoder)
    LOGGER.info(f"Report saved to {output_path}")
