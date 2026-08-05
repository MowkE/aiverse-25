"""Contract tests for every structured action schema: valid, invalid, bounds."""

import json

import pytest

from universe25.llm.schemas import (
    SCHEMA_NAMES,
    contribution_schema,
    decision_schema,
    public_phase_schema,
    report_schema,
    to_api_schema,
    validate_action,
)

SCHEMAS = {
    "public_phase": public_phase_schema(240),
    "decision": decision_schema(3),
    "contribution": contribution_schema(),
    "report": report_schema(),
}

VALID = {
    "public_phase": {"participate": True, "proposal_type": 1, "public_message": "hello"},
    "decision": {"adopt_index": 2},
    "contribution": {"contribution_fraction": 0.5},
    "report": {"confidence": 0.5, "perceived_efficacy": 0.1, "legitimacy_rating": 1.0},
}

INVALID = {
    "public_phase": [
        {"participate": "yes", "proposal_type": 1, "public_message": "m"},  # wrong type
        {"participate": True, "proposal_type": 5, "public_message": "m"},  # bad enum
        {"participate": True, "proposal_type": 1},  # missing field
        {"participate": True, "proposal_type": 1, "public_message": "x" * 241},  # too long
        {"participate": True, "proposal_type": 1, "public_message": "m", "extra": 1},
    ],
    "decision": [
        {"adopt_index": 3},   # out of range (n_submissions=3)
        {"adopt_index": -2},  # below -1
        {"adopt_index": 1.5},
        {},
    ],
    "contribution": [
        {"contribution_fraction": 1.5},
        {"contribution_fraction": -0.1},
        {"contribution_fraction": "half"},
        {},
    ],
    "report": [
        {"confidence": 2.0, "perceived_efficacy": 0.1, "legitimacy_rating": 0.5},
        {"confidence": 0.5, "perceived_efficacy": 0.1},
        {"confidence": 0.5, "perceived_efficacy": 0.1, "legitimacy_rating": 0.5, "x": 1},
    ],
}


def test_all_schema_names_covered():
    assert set(SCHEMAS) == set(SCHEMA_NAMES)


@pytest.mark.parametrize("name", sorted(SCHEMAS))
def test_valid_payloads_pass(name):
    outcome = validate_action(json.dumps(VALID[name]), SCHEMAS[name])
    assert outcome.valid, outcome.error
    assert outcome.parsed == VALID[name]


@pytest.mark.parametrize(
    "name,payload",
    [(n, p) for n, ps in INVALID.items() for p in ps],
)
def test_invalid_payloads_fail(name, payload):
    outcome = validate_action(json.dumps(payload), SCHEMAS[name])
    assert not outcome.valid
    assert outcome.error is not None
    assert outcome.parsed is None


@pytest.mark.parametrize("text", ["", "not json", "[1, 2]", '"a string"', "42"])
def test_non_object_json_fails(text):
    outcome = validate_action(text, SCHEMAS["contribution"])
    assert not outcome.valid


def test_api_schema_strips_unsupported_constraints():
    api = to_api_schema(SCHEMAS["contribution"])
    frac = api["properties"]["contribution_fraction"]
    assert "minimum" not in frac and "maximum" not in frac
    api_pub = to_api_schema(SCHEMAS["public_phase"])
    assert "maxLength" not in api_pub["properties"]["public_message"]
    # enum and required survive
    assert api_pub["properties"]["proposal_type"]["enum"] == [0, 1, 2]
    assert api["required"] == ["contribution_fraction"]
    assert api["additionalProperties"] is False


def test_bounds_enforced_locally_even_though_stripped_for_api():
    # The API schema alone would accept 1.5; local validation must reject it.
    outcome = validate_action('{"contribution_fraction": 1.5}', SCHEMAS["contribution"])
    assert not outcome.valid
