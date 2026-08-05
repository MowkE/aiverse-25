"""CLI: estimate makes no calls; smoke uses mock; run-batch is budget-gated."""

import pytest

from universe25.llm.cli import main


def _write_config(tmp_path, provider="mock", n_rounds=6, out_name="out"):
    out = tmp_path / out_name
    cfg = tmp_path / "cfg.toml"
    cfg.write_text(
        f"""
master_seed = 99
n_pairs = 1
output_dir = "{out}"

[run]
n_agents = 8
n_rounds = {n_rounds}
provider = "{provider}"
model = "claude-sonnet-5"
report_rounds = "none"
"""
    )
    return cfg, out


def test_estimate_prints_costs(tmp_path, capsys):
    cfg, _ = _write_config(tmp_path)
    assert main(["estimate", "--config", str(cfg)]) == 0
    text = capsys.readouterr().out
    assert "per run" in text and "per batch" in text
    assert "claude-sonnet-5" in text and "claude-opus-5" in text


def test_smoke_runs_mock_and_validates(tmp_path, capsys):
    cfg, out = _write_config(tmp_path)
    assert main(["smoke", "--config", str(cfg)]) == 0
    text = capsys.readouterr().out
    assert "no API calls were made" in text
    assert "PASS" in text
    assert (out / "run_summary.csv").exists()


def test_run_batch_mock_needs_no_budget(tmp_path):
    cfg, out = _write_config(tmp_path, out_name="out2")
    assert main(["run-batch", "--config", str(cfg)]) == 0
    assert (out / "run_summary.csv").exists()


def test_run_batch_real_provider_blocked_without_confirmation(tmp_path, capsys,
                                                              monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-not-a-real-key")
    cfg, out = _write_config(tmp_path, provider="anthropic", out_name="out3")
    rc = main(["run-batch", "--config", str(cfg)])
    assert rc == 2
    assert "ABORT" in capsys.readouterr().err
    assert not (out / "run_summary.csv").exists()


def test_run_batch_real_provider_blocked_when_estimate_exceeds_budget(
    tmp_path, capsys, monkeypatch
):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-not-a-real-key")
    cfg, out = _write_config(tmp_path, provider="anthropic", out_name="out4")
    rc = main(["run-batch", "--config", str(cfg), "--confirm-budget", "0.000001"])
    assert rc == 2
    assert "exceeds confirmed" in capsys.readouterr().err
    assert not (out / "run_summary.csv").exists()


def test_unknown_provider_rejected(tmp_path):
    cfg, _ = _write_config(tmp_path, provider="skynet", out_name="out5")
    with pytest.raises(ValueError, match="unknown provider"):
        main(["estimate", "--config", str(cfg)])
