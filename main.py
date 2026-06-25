# main.py
"""Pipeline entry point — orchestrates the LangGraph data processing workflow."""
from pathlib import Path
from dotenv import load_dotenv

from cli import parse_args
from graph import build_graph
from utils.report import save_report
from utils.logger import LOGGER

load_dotenv()


def run_pipeline(input_path: Path, output_path: Path) -> None:
    """
    Execute the full processing pipeline.

    Builds the LangGraph workflow, invokes it with the input state,
    and saves the final report to disk.

    Args:
        input_path:  Path to the input JSON data file.
        output_path: Path where the output report will be saved.
    """
    graph = build_graph()

    initial_state = {
        "raw_data": [],
        "records": [],
        "events": [],
        "incidents": [],
        "final_report": None,
        "input_path": str(input_path),
    }

    LOGGER.info(f"Starting pipeline - input: {input_path}")

    result_state = graph.invoke(initial_state)

    final_report = result_state.get("final_report")

    if final_report:
        save_report(final_report, output_path)
    else:
        LOGGER.warning("No report generated (pipeline stopped or no data).")


if __name__ == "__main__":
    args = parse_args()
    run_pipeline(args.input, args.output)
