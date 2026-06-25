# nodes/generate.py
"""Recommendation node — generates LLM-based recommendations."""
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from models.schemas import RecommendationList
from utils import LOGGER

load_dotenv()

llm = ChatOpenAI(
    base_url=os.getenv("OPENAI_BASE_URL", "http://localhost:8000"),
    api_key=os.getenv("OPENAI_API_KEY", "sk-no-key-required"),
    model=os.getenv("OPENAI_DEFAULT_MODEL", "Qwen2.5-7B"),
    temperature=float(os.getenv("GEN_TEMPERATURE", "0.0")),
    max_tokens=int(os.getenv("GEN_MAX_TOKENS", 2048)),
)

llm_structured = llm.with_structured_output(RecommendationList)

prompt_path = Path("config/prompts/generate.txt")
_PROMPT_TEMPLATE = prompt_path.read_text(encoding="utf-8")
_SYSTEM_PROMPT = (
    "You are an expert data analysis engineer. "
    "You respond ONLY with valid JSON, no preamble, "
    "no markdown, no explanation."
)


def generate_node(state: dict) -> dict:
    """
    Send aggregated incidents to a local LLM for recommendations.

    Args:
        state: LangGraph state containing "incidents".

    Returns:
        Dict with updated "final_report" key.
    """
    LOGGER.info("Node 3: Generating recommendations...")

    incidents = state.get("incidents", [])

    if not incidents:
        LOGGER.warning("No incidents to process.")
        return {"final_report": {"recommendations": []}}

    incidents_payload = [i.model_dump() for i in incidents]

    messages = [
        SystemMessage(content=_SYSTEM_PROMPT),
        HumanMessage(
            content=_PROMPT_TEMPLATE.format(
                incidents=json.dumps(incidents_payload, indent=2)
            )
        ),
    ]

    try:
        response: RecommendationList = llm_structured.invoke(messages)
        actions = response.recommendations
        count_actions = len(actions)
        LOGGER.info(f"{count_actions} recommendations generated.")
    except Exception as e:
        LOGGER.error(f"LLM call failed: {e}")
        critical_count = sum(1 for i in incidents if i.severity == "critical")
        warning_count = sum(1 for i in incidents if i.severity == "warning")
        return {
            "final_report": {
                "total_events": sum(i.occurrences for i in incidents),
                "total_incidents": len(incidents),
                "critical_count": critical_count,
                "warning_count": warning_count,
                "recommendations": [],
                "error": "LLM unavailable — no recommendations.",
            }
        }

    critical_count = sum(1 for i in incidents if i.severity == "critical")
    warning_count = sum(1 for i in incidents if i.severity == "warning")
    return {
        "final_report": {
            "total_events": sum(i.occurrences for i in incidents),
            "total_incidents": len(incidents),
            "critical_count": critical_count,
            "warning_count": warning_count,
            "recommendations": actions,
        }
    }
