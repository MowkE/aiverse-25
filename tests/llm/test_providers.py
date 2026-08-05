"""Provider contract: mock determinism + retry machinery; real providers gated."""

import json

import pytest

from universe25.llm.budget import BudgetGuard, BudgetNotConfirmedError
from universe25.llm.providers import MockProvider
from universe25.llm.providers.base import LLMRequest, MissingAPIKeyError, Provider
from universe25.llm.schemas import public_phase_schema, to_api_schema, validate_action


def _request(seed=7, schema_name="public_phase", metadata=None):
    return LLMRequest(
        system="sys", user="user", schema_name=schema_name,
        api_schema=to_api_schema(public_phase_schema()),
        model="claude-sonnet-5", seed=seed, metadata=metadata or {},
    )


def test_mock_is_deterministic_in_seed():
    a = MockProvider().complete(_request(seed=123))
    b = MockProvider().complete(_request(seed=123))
    assert a.text == b.text
    assert MockProvider().complete(_request(seed=124)).text != a.text


def test_mock_satisfies_protocol_and_is_not_real():
    provider = MockProvider()
    assert isinstance(provider, Provider)
    assert provider.is_real is False


def test_mock_output_validates_against_full_schema():
    for seed in range(20):
        resp = MockProvider().complete(_request(seed=seed))
        assert validate_action(resp.text, public_phase_schema()).valid


def test_mock_decision_uses_submission_count():
    for seed in range(30):
        resp = MockProvider(adopt_p=1.0).complete(
            _request(seed=seed, schema_name="decision", metadata={"n_submissions": 3})
        )
        assert 0 <= json.loads(resp.text)["adopt_index"] <= 2


def test_mock_fault_injection_invalid_then_valid():
    provider = MockProvider(invalid_first_calls=2)
    r1 = provider.complete(_request())
    r2 = provider.complete(_request())
    r3 = provider.complete(_request())
    assert not validate_action(r1.text, public_phase_schema()).valid
    assert not validate_action(r2.text, public_phase_schema()).valid
    assert validate_action(r3.text, public_phase_schema()).valid


def test_mock_raise_after_calls():
    provider = MockProvider(raise_after_calls=1)
    provider.complete(_request())
    with pytest.raises(ConnectionError):
        provider.complete(_request())


def test_anthropic_provider_requires_guard_and_key(monkeypatch):
    from universe25.llm.providers.anthropic_provider import AnthropicProvider

    with pytest.raises(BudgetNotConfirmedError):
        AnthropicProvider(guard=None)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(MissingAPIKeyError):
        AnthropicProvider(guard=BudgetGuard(model="claude-sonnet-5"))


def test_openai_provider_requires_guard_and_key(monkeypatch):
    from universe25.llm.providers.openai_provider import OpenAIProvider

    with pytest.raises(BudgetNotConfirmedError):
        OpenAIProvider(guard=None)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(MissingAPIKeyError):
        OpenAIProvider(guard=BudgetGuard(model="gpt-5"))


def test_real_provider_call_blocked_by_unarmed_guard(monkeypatch):
    """Even with a key present, an unarmed guard blocks before any HTTP."""
    from universe25.llm.providers.anthropic_provider import AnthropicProvider

    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-not-a-real-key")
    provider = AnthropicProvider(guard=BudgetGuard(model="claude-sonnet-5"))
    with pytest.raises(BudgetNotConfirmedError):
        provider.complete(_request())
