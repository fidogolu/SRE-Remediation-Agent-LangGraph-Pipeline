# graph.py
"""LangGraph pipeline builder — defines the DAG workflow."""
from langgraph.graph import StateGraph, START, END

from models.schemas import PipelineState
from nodes.ingest import ingest_node
from nodes.validate import validate_node
from nodes.detect import detect_node
from nodes.aggregate import aggregate_node
from nodes.generate import generate_node


def build_graph():
    """
    Build and compile the LangGraph pipeline.

    Returns:
        Compiled LangGraph workflow ready to be invoked.
    """
    workflow = StateGraph(PipelineState)

    workflow.add_node("ingest", ingest_node)
    workflow.add_node("validate", validate_node)
    workflow.add_node("detect", detect_node)
    workflow.add_node("aggregate", aggregate_node)
    workflow.add_node("generate", generate_node)

    workflow.add_edge(START, "ingest")
    workflow.add_edge("ingest", "validate")
    workflow.add_edge("validate", "detect")
    workflow.add_edge("detect", "aggregate")
    workflow.add_edge("aggregate", "generate")
    workflow.add_edge("generate", END)

    return workflow.compile()
