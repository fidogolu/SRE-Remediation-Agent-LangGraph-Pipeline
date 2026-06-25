# models/rules.py
"""Validation schemas for pipeline rules configuration."""
from pydantic import BaseModel, Field, validator
from typing import List, Optional


class RuleConfig(BaseModel):
    """Defines a detection rule with threshold or condition."""

    name: str
    threshold: Optional[float] = None
    severity: str = Field(..., pattern=r"^(normal|warning|critical)$")
    value_multiplier: Optional[int] = 1

    @validator("severity")
    def severity_must_be_valid(cls, v):
        if v not in ["info", "warning", "critical"]:
            raise ValueError("Severity must be 'info', 'warning', or 'critical'")
        return v

    @validator("threshold")
    def threshold_must_be_valid(cls, v, values):
        value_multiplier = values.get("value_multiplier", 1)
        if v is None:
            return v
        if value_multiplier == 100:
            if not (0 <= v <= 1):
                raise ValueError(
                    "Threshold must be between 0 and 1 " "when value_multiplier is 100"
                )
        elif value_multiplier == 1:
            if not (0 <= v <= 100):
                raise ValueError(
                    "Threshold must be between 0 and 100 " "when value_multiplier is 1"
                )
        else:
            if not (0 <= v <= 100):
                raise ValueError(
                    "Threshold must be between 0 and 100 "
                    "when value_multiplier is not 100 or 1"
                )
        return v


class RulesConfig(BaseModel):
    """Container for a list of detection rules."""

    rules: List[RuleConfig]
