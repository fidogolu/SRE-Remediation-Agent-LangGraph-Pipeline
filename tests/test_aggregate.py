# tests/test_aggregate.py
"""Unit tests for the aggregation node."""
import sys
from pathlib import Path

# Add project root to path (Windows compatibility)
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from nodes.aggregate import aggregate_node
from models.schemas import Event


def make_event(**kwargs) -> Event:
    """Helper to create Event objects with sensible defaults."""
    return Event(
        timestamp=kwargs.get("timestamp", "2024-01-01T00:00:00Z"),
        metric=kwargs.get("metric", "cpu"),
        value=kwargs.get("value", 92.0),
        severity=kwargs.get("severity", "critical"),
        category=kwargs.get("category", "resource"),
        description=kwargs.get("description", "CPU saturation (92%)"),
        affected_services=kwargs.get("affected_services", ["system"]),
        context=kwargs.get("context", None),
    )


class TestAggregateNode:

    def test_empty_events_returns_empty_incidents(self):
        """No events should produce no incidents."""
        result = aggregate_node({"events": []})
        assert result["incidents"] == []

    def test_single_event_produces_single_incident(self):
        """One event should produce exactly one incident."""
        event = make_event()
        result = aggregate_node({"events": [event]})
        assert len(result["incidents"]) == 1

    def test_same_metric_and_severity_are_grouped(self):
        """Multiple events with same metric+severity must be grouped."""
        events = [
            make_event(
                metric="cpu",
                severity="critical",
                value=92.0,
                timestamp="2024-01-01T00:00:00Z",
            ),
            make_event(
                metric="cpu",
                severity="critical",
                value=95.0,
                timestamp="2024-01-01T00:30:00Z",
            ),
            make_event(
                metric="cpu",
                severity="critical",
                value=91.0,
                timestamp="2024-01-01T01:00:00Z",
            ),
        ]
        result = aggregate_node({"events": events})
        assert len(result["incidents"]) == 1
        assert result["incidents"][0].occurrences == 3

    def test_different_metrics_produce_separate_incidents(self):
        """Events with different metrics must not be grouped."""
        events = [
            make_event(metric="cpu", severity="critical"),
            make_event(metric="disk", severity="critical"),
            make_event(metric="memory", severity="warning"),
        ]
        result = aggregate_node({"events": events})
        assert len(result["incidents"]) == 3

    def test_peak_value_is_max(self):
        """peak_value must be the maximum across grouped events."""
        events = [
            make_event(metric="cpu", severity="critical", value=91.0),
            make_event(metric="cpu", severity="critical", value=97.0),
            make_event(metric="cpu", severity="critical", value=93.0),
        ]
        result = aggregate_node({"events": events})
        assert result["incidents"][0].peak_value == pytest.approx(97.0)

    def test_start_and_end_timestamps(self):
        """start must be first timestamp, end must be last."""
        events = [
            make_event(
                metric="cpu",
                severity="critical",
                timestamp="2024-01-01T00:00:00Z",
            ),
            make_event(
                metric="cpu",
                severity="critical",
                timestamp="2024-01-01T01:00:00Z",
            ),
            make_event(
                metric="cpu",
                severity="critical",
                timestamp="2024-01-01T02:00:00Z",
            ),
        ]
        result = aggregate_node({"events": events})
        incident = result["incidents"][0]
        assert incident.start == "2024-01-01T00:00:00Z"
        assert incident.end == "2024-01-01T02:00:00Z"

    def test_affected_services_are_deduplicated(self):
        """affected_services must not contain duplicates."""
        events = [
            make_event(
                metric="cpu",
                severity="critical",
                affected_services=["service_a", "service_b"],
                timestamp="2024-01-01T00:00:00Z",
            ),
            make_event(
                metric="cpu",
                severity="critical",
                affected_services=["service_b", "service_c"],
                timestamp="2024-01-01T01:00:00Z",
            ),
        ]
        result = aggregate_node({"events": events})
        affected = result["incidents"][0].affected_services
        assert len(affected) == 3
        assert "service_a" in affected
        assert "service_b" in affected
        assert "service_c" in affected
