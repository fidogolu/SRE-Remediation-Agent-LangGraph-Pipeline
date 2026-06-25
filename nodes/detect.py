# nodes/detect.py
"""Detection node — applies rule-based anomaly/event detection."""
import yaml

from models.schemas import Event
from utils import LOGGER


def load_rules(path: str = "config/rules.yaml") -> list:
    """
    Load and sort detection rules from the YAML configuration file.

    Args:
        path: Path to the YAML configuration file.

    Returns:
        List of rules sorted by ascending priority order.
    """
    with open(path) as f:
        return sorted(yaml.safe_load(f)["rules"], key=lambda r: r["priority"])


RULES = load_rules()


def resolve_metric_priority(m, offline_services: list) -> tuple:
    """
    Iterate through rules by priority and return the primary metric
    and the value that triggered the event.

    Args:
        m:                Object containing metrics.
        offline_services: List of currently offline services.

    Returns:
        Tuple (metric, trigger_value).
    """
    for rule in RULES:
        match rule["type"]:
            case "offline_services":
                if offline_services:
                    return rule["metric"], 0.0

            case "threshold":
                value = getattr(m, rule["condition"], None)
                if value is not None and value > rule["threshold"]:
                    multiplier = rule.get("value_multiplier", 1)
                    trigger_value = float(value * multiplier)
                    return rule["metric"], trigger_value

    raise ValueError("resolve_metric_priority called but no rule matched")


def detect_node(state: dict) -> dict:
    """
    Detect events based on rule configuration.

    Args:
        state: LangGraph state containing "records" and "events".

    Returns:
        Dict with updated "events" key.
    """
    LOGGER.info("Node 2: Detecting events...")

    events = state.get("events", [])
    records = state.get("records", [])

    for m in records:
        reasons = []
        affected = []
        severity = "info"
        category = "resource"
        metric_name = "unknown"
        trigger_value = 0.0

        offline_services = [
            s for s, status in m.service_status.items() if status == "offline"
        ]

        for rule in RULES:
            match rule["type"]:
                case "offline_services":
                    if offline_services:
                        severity = rule["severity"]
                        category = rule["category"]
                        offline_str = ", ".join(offline_services)
                        reasons.append(rule["message"].format(value=offline_str))
                        affected = list(offline_services)
                        metric_name = rule["metric"]
                        trigger_value = 0.0

                case "threshold":
                    value = getattr(m, rule["condition"], None)
                    if value is not None and value > rule["threshold"]:
                        severity = rule["severity"]
                        category = rule["category"]
                        multiplier = rule.get("value_multiplier", 1)
                        trigger_value = float(value * multiplier)
                        metric_name = rule["metric"]
                        reasons.append(rule["message"].format(value=trigger_value))
                        affected = rule.get("affected", [])
                        break

            if reasons:
                event = Event(
                    timestamp=m.timestamp,
                    metric=metric_name,
                    value=trigger_value,
                    severity=severity,
                    category=category,
                    description=reasons[0],
                    affected_services=affected,
                    context={
                        "cpu_usage": m.metric_a,
                        "memory_usage": m.metric_b,
                        "disk_usage": m.metric_d,
                        "error_rate": m.metric_h,
                    },
                )
                events.append(event)
                break

    return {"events": events}
