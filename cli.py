# cli.py
"""Command-line argument parser for the pipeline."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def parse_args() -> argparse.Namespace:
    """
    Parse and validate command-line arguments.

    Validates that the input file exists before launching the pipeline.
    Exits with a clear error message if the file is not found.

    Returns:
        Namespace with input and output path arguments.
    """
    parser = argparse.ArgumentParser(
        description="Generic data processing pipeline — rule-based detection & recommendations."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/sample_data.json"),
        help="Path to the input JSON file (default: data/sample_data.json)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/output.json"),
        help="Path to the output JSON file (default: data/output.json)",
    )

    args = parser.parse_args()

    if not args.input.exists():
        parser.error(f"Input file not found: {args.input}")

    return args
