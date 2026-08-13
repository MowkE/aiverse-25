"""ClaudeCLIProvider: parsing, guard contract, and $0 charging (no CLI runs)."""

import json

import pytest

from universe25.llm.budget import BudgetGuard, BudgetNotConfirmedError
from universe25.llm.providers.claude_cli import (
    ClaudeCLIError,
    ClaudeCLIProvider,
    parse_cli_output,
)


def _cli_json(result: str, **extra) -> str:
    payload = {
        "type": "result",
        "subtype": "success",
        "is_error": False,
        "result": result,
        "session_id": "sess-1",
        "usage": {"input_tokens": 100, "output_tokens": 20, "cache_read_input_tokens": 50},
    }
    payload.update(extra)
    return json.dumps(payload)


def test_parse_extracts_text_and_tokens():
    text, in_tok, out_tok, sid = parse_cli_output(_cli_json('{"participate": true}'))
    assert json.loads(text) == {"participate": True}
    assert in_tok == 150 and out_tok == 20 and sid == "sess-1"


def test_parse_strips_code_fences():
    fenced = "```json\n{\"a\": 1}\n```"
    text, *_ = parse_cli_output(_cli_json(fenced))
    assert json.loads(text) == {"a": 1}


def test_parse_raises_on_cli_error():
    with pytest.raises(ClaudeCLIError):
        parse_cli_output(_cli_json("boom", is_error=True))


def test_construction_requires_guard():
    with pytest.raises(BudgetNotConfirmedError):
        ClaudeCLIProvider(guard=None)


def test_charges_zero_dollars(monkeypatch, tmp_path):
    fake = tmp_path / "claude"
    fake.write_text("#!/bin/sh\necho unused\n")
    fake.chmod(0o755)
    guard = BudgetGuard(model="claude-haiku-4-5")
    guard.arm(1.0)
    provider = ClaudeCLIProvider(guard=guard, binary=str(fake))

    class FakeProc:
        returncode = 0
        stdout = _cli_json('{"contribution_fraction": 0.5}')
        stderr = ""

    monkeypatch.setattr(
        "universe25.llm.providers.claude_cli.subprocess.run",
        lambda *a, **k: FakeProc(),
    )
    from universe25.llm.providers.base import LLMRequest

    resp = provider.complete(
        LLMRequest(
            system="s", user="u", schema_name="contribution",
            api_schema={"type": "object"}, model="claude-haiku-4-5",
        )
    )
    assert resp.provider == "claude-cli"
    assert guard.spent_usd == 0.0
    assert guard.calls_made == 1
