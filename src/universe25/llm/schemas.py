"""Structured action schemas + validation (docs/LLM_DESIGN.md §4).

Each schema has two views: the full schema (with numeric bounds / maxLength)
used for local validation, and an API view (bounds stripped) sent to providers,
because Anthropic structured outputs do not support minimum/maximum/maxLength.
Bounds are always enforced locally. Invalid responses are retried up to a fixed
maximum; exhaustion yields a recorded no-op, never a substituted action.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import jsonschema

SCHEMA_NAMES = ("public_phase", "decision", "contribution", "report")

_UNSUPPORTED_API_KEYS = ("minimum", "maximum", "maxLength", "minLength")


def public_phase_schema(message_max_chars: int = 240) -> dict:
    return {
        "type": "object",
        "properties": {
            "participate": {"type": "boolean"},
            "proposal_type": {"type": "integer", "enum": [0, 1, 2]},
            "public_message": {"type": "string", "maxLength": message_max_chars},
        },
        "required": ["participate", "proposal_type", "public_message"],
        "additionalProperties": False,
    }


def decision_schema(n_submissions: int) -> dict:
    return {
        "type": "object",
        "properties": {
            "adopt_index": {"type": "integer", "minimum": -1, "maximum": n_submissions - 1},
        },
        "required": ["adopt_index"],
        "additionalProperties": False,
    }


def contribution_schema() -> dict:
    return {
        "type": "object",
        "properties": {
            "contribution_fraction": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        },
        "required": ["contribution_fraction"],
        "additionalProperties": False,
    }


def report_schema() -> dict:
    bounded = {"type": "number", "minimum": 0.0, "maximum": 1.0}
    return {
        "type": "object",
        "properties": {
            "confidence": dict(bounded),
            "perceived_efficacy": dict(bounded),
            "legitimacy_rating": dict(bounded),
        },
        "required": ["confidence", "perceived_efficacy", "legitimacy_rating"],
        "additionalProperties": False,
    }


def to_api_schema(schema: dict) -> dict:
    """Strip constraints unsupported by provider structured-output features."""

    def strip(node: Any) -> Any:
        if isinstance(node, dict):
            return {k: strip(v) for k, v in node.items() if k not in _UNSUPPORTED_API_KEYS}
        if isinstance(node, list):
            return [strip(v) for v in node]
        return node

    return strip(schema)


@dataclass(frozen=True)
class ValidationOutcome:
    valid: bool
    parsed: dict | None
    error: str | None


def validate_action(text: str, schema: dict) -> ValidationOutcome:
    """Parse JSON text and validate against the full (bounded) schema."""
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        return ValidationOutcome(False, None, f"not valid JSON: {exc}")
    if not isinstance(parsed, dict):
        return ValidationOutcome(False, None, "top-level JSON value must be an object")
    try:
        jsonschema.validate(parsed, schema, cls=jsonschema.Draft202012Validator)
    except jsonschema.ValidationError as exc:
        return ValidationOutcome(False, None, f"schema violation: {exc.message}")
    return ValidationOutcome(True, parsed, None)
