# nodes/aggregate.py
"""Aggregation node — groups events into incidents."""
from collections import defaultdict

from models.schemas import AggregatedEvent
from utils import LOGGER


def aggregate_node(state: dict) -> dict:
    """
    Group raw events by metric and severity to produce
    aggregated incidents, reducing noise before LLM processing.

    Args:
        state: LangGraph state containing "events".

    Returns:
        Dict with updated "incidents" key.
    """
    LOGGER.info("Node 2.5: Aggregating events...")

    events = state.get("events", [])
    groups = defaultdict(list)

    for event in events:
        key = (event.metric, event.severity)
        groups[key].append(event)

    incidents = []
    for (metric, severity), group in groups.items():
        incidents.append(
            AggregatedEvent(
                metric=metric,
                severity=severity,
                category=group[0].category,
                occurrences=len(group),
                start=group[0].timestamp,
                end=group[-1].timestamp,
                peak_value=max(e.value for e in group),
                affected_services=list({s for e in group for s in e.affected_services}),
                description=group[0].description,
            )
        )

    severity_order = {"critical": 0, "warning": 1, "info": 2}
    incidents.sort(key=lambda i: (severity_order[i.severity], -i.occurrences))

    count_incidents = len(incidents)
    count_events = len(events)
    LOGGER.info(f"{count_incidents} aggregated incidents from {count_events} events.")
    return {"incidents": incidents}
