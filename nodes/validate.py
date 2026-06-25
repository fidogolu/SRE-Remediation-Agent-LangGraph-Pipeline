# nodes/validate.py
"""Validation node — validates rules config and data."""
import yaml

from models.schemas import DataRecord
from models.rules import RulesConfig
from pydantic import ValidationError
from utils.logger import LOGGER


def validate_node(state: dict) -> dict:
    """
    1. Validate rules configuration (rules.yaml).
    2. Validate raw data against DataRecord model.
    3. Return list of validated DataRecord objects.
    """
    validation_result = validate_rules_config(state)

    if "validation_error" in validation_result:
        return {
            "service_status": [],
            "validation_error": validation_result["validation_error"],
        }

    LOGGER.info("Node 1.5: Validating data...")
    valid_records = []
    invalid_count = 0

    for row in state.get("raw_data", []):
        try:
            valid_records.append(DataRecord(**row))
        except ValidationError:
            invalid_count += 1

    if invalid_count > 0:
        LOGGER.warning(f"Number of invalid entries detected: {invalid_count}")

    return {"records": valid_records}


def validate_rules_config(state: dict) -> dict:
    """
    Validate the rules configuration from 'rules.yaml'.

    Args:
        state: Not used (reads YAML directly from filesystem).

    Returns:
        Dict with validated rules or error message.
    """
    try:
        with open("config/rules.yaml", "r") as f:
            raw_data = yaml.safe_load(f)
    except FileNotFoundError:
        LOGGER.error("File 'rules.yaml' not found.")
        return {"validation_error": "File 'rules.yaml' not found."}
    except yaml.YAMLError as e:
        LOGGER.error(f"YAML syntax error: {str(e)}")
        return {"validation_error": f"YAML syntax error: {str(e)}"}

    try:
        validated_data = RulesConfig(**raw_data)
        return {"validated_rules": validated_data, "status": "success"}
    except Exception as e:
        LOGGER.error(f"Data validation error: {str(e)}")
        return {"validation_error": f"Data validation error: {str(e)}"}
