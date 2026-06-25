# models/schemas.py
"""Pydantic data models and the PipelineState TypedDict."""
from pydantic import BaseModel
from typing import Literal, TypedDict


# --- Data Models ---


class DataRecord(BaseModel):
    """Generic data record with metric fields."""

    timestamp: str
    metric_a: float
    metric_b: float
    metric_c: float
    metric_d: float
    metric_e: float
    metric_f: float
    metric_g: float
    thread_count: int
    active_connections: int
    metric_h: float
    uptime_seconds: int
    metric_i: float
    metric_j: float
    service_status: dict[str, str]


class Event(BaseModel):
    """Represents a detected event/anomaly."""

    timestamp: str
    metric: str
    value: float
    severity: Literal["info", "warning", "critical"]
    category: Literal["resource", "performance", "availability", "security"]
    description: str
    affected_services: list[str]
    context: dict[str, float] | None = None


class AggregatedEvent(BaseModel):
    """Grouped events for downstream processing."""

    metric: str
    severity: Literal["info", "warning", "critical"]
    category: Literal["resource", "performance", "availability", "security"]
    occurrences: int
    start: str
    end: str
    peak_value: float
    affected_services: list[str]
    description: str


class ActionItem(BaseModel):
    """Actionable recommendation."""

    priority: str
    issue: str
    recommendation: str


class RecommendationList(BaseModel):
    """Wrapper for list of actions."""

    recommendations: list[ActionItem]


# --- THE LANGGRAPH STATE ---


class PipelineState(TypedDict):
    input_path: str
    raw_data: list[dict]
    records: list[DataRecord]
    events: list[Event]
    incidents: list[AggregatedEvent]
    final_report: dict | None
