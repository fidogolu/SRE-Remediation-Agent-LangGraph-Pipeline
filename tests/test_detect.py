# tests/test_detect.py
"""Unit tests for the detection node."""
import sys
from pathlib import Path

# Add project root to path (Windows compatibility)
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from nodes.detect import resolve_metric_priority


class MockRecord:
    """Minimal mock of a DataRecord for testing."""

    def __init__(self, **kwargs):
        self.metric_a = kwargs.get("metric_a", 0.0)
        self.metric_b = kwargs.get("metric_b", 0.0)
        self.metric_d = kwargs.get("metric_d", 0.0)
        self.metric_g = kwargs.get("metric_g", 0.0)
        self.metric_h = kwargs.get("metric_h", 0.0)


class TestResolveMetricPriority:

    def test_offline_services_wins_over_everything(self):
        """Availability must always be the top priority."""
        m = MockRecord(metric_a=95, metric_d=95, metric_h=0.5)
        metric, value = resolve_metric_priority(m, ["database"])
        assert metric == "availability"
        assert value == 0.0

    def test_error_rate_wins_over_disk(self):
        """Error rate (priority 2) must beat disk (priority 3)."""
        m = MockRecord(metric_h=0.15, metric_d=95)
        metric, value = resolve_metric_priority(m, [])
        assert metric == "error_rate"
        assert value == pytest.approx(15.0)

    def test_disk_wins_over_io_wait(self):
        """Disk (priority 3) must beat io_wait (priority 4)."""
        m = MockRecord(metric_d=95, metric_g=20)
        metric, value = resolve_metric_priority(m, [])
        assert metric == "disk"
        assert value == pytest.approx(95.0)

    def test_memory_critical_wins_over_cpu(self):
        """Memory > 95% (priority 5) must beat cpu > 90% (priority 6)."""
        m = MockRecord(metric_b=97, metric_a=92)
        metric, value = resolve_metric_priority(m, [])
        assert metric == "memory"
        assert value == pytest.approx(97.0)

    def test_cpu_returned_when_only_cpu_critical(self):
        """CPU must be returned when it is the only critical metric."""
        m = MockRecord(metric_a=92)
        metric, value = resolve_metric_priority(m, [])
        assert metric == "cpu"
        assert value == pytest.approx(92.0)

    def test_memory_warning_is_fallback(self):
        """Memory warning (priority 7) must be returned as last resort."""
        m = MockRecord(metric_b=88)
        metric, value = resolve_metric_priority(m, [])
        assert metric == "memory"
        assert value == pytest.approx(88.0)

    def test_no_match_raises_value_error(self):
        """ValueError must be raised if no rule matches."""
        m = MockRecord()
        with pytest.raises(ValueError, match="no rule matched"):
            resolve_metric_priority(m, [])

    def test_error_rate_multiplier(self):
        """Error rate must be multiplied by 100 for display."""
        m = MockRecord(metric_h=0.20)
        metric, value = resolve_metric_priority(m, [])
        assert metric == "error_rate"
        assert value == pytest.approx(20.0)
