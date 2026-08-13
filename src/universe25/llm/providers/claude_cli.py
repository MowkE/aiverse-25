"""Claude Code CLI adapter — subscription-funded SHAKEDOWN provider.

Each completion runs `claude -p` as a headless subprocess authenticated by the
researcher's Claude subscription: zero marginal dollars, but the CLI wraps our
system prompt in harness scaffolding we do not control and exposes no sampling
metadata. Runs made through this provider are engineering shakedowns only and
must never enter preregistered analyses or the paper (DECISIONS D15).

Guard contract matches the real providers: construction requires a BudgetGuard,
every call passes precall(), and each call is charged at $0 so call counts are
still audited.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import time

from ..budget import BudgetGuard, BudgetNotConfirmedError
from .base import LLMRequest, LLMResponse, MissingAPIKeyError

_TIMEOUT_S = 240.0


class ClaudeCLIError(RuntimeError):
    pass


def _strip_fences(text: str) -> str:
    s = text.strip()
    if s.startswith("```"):
        first_newline = s.find("\n")
        if first_newline != -1:
            s = s[first_newline + 1 :]
        if s.rstrip().endswith("```"):
            s = s.rstrip()[:-3]
    return s.strip()


def parse_cli_output(stdout: str) -> tuple[str, int, int, str | None]:
    """Returns (text, input_tokens, output_tokens, session_id) from
    `claude -p --output-format json` stdout."""
    data = json.loads(stdout)
    if data.get("is_error"):
        raise ClaudeCLIError(f"claude CLI reported error: {data.get('result')!r}")
    text = _strip_fences(str(data.get("result", "")))
    usage = data.get("usage") or {}
    in_tok = int(usage.get("input_tokens", 0) or 0) + int(
        usage.get("cache_read_input_tokens", 0) or 0
    ) + int(usage.get("cache_creation_input_tokens", 0) or 0)
    out_tok = int(usage.get("output_tokens", 0) or 0)
    return text, in_tok, out_tok, data.get("session_id")


class ClaudeCLIProvider:
    name = "claude-cli"
    is_real = True

    def __init__(self, guard: BudgetGuard | None, binary: str | None = None):
        if guard is None:
            raise BudgetNotConfirmedError(
                "ClaudeCLIProvider requires a BudgetGuard; refusing to construct"
            )
        found = binary or shutil.which("claude")
        if not found:
            raise MissingAPIKeyError("claude CLI not found on PATH")
        self.guard = guard
        self._binary = found
        # Neutral cwd so the CLI cannot pick up this project's context files.
        self._cwd = tempfile.mkdtemp(prefix="u25-claude-cli-")
        # Subscription auth only: an API key in the environment would silently
        # turn shakedown runs into paid ones.
        self._env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}

    def complete(self, request: LLMRequest) -> LLMResponse:
        self.guard.precall()

        user = (
            f"{request.user}\n\n"
            "Respond with ONLY a single JSON object (no prose, no code fences) "
            f"that validates against this JSON Schema:\n{json.dumps(request.api_schema)}"
        )
        system = (
            f"{request.system}\n\n"
            "You have no tools. Never attempt to use tools. "
            "Output only the requested JSON object."
        )
        cmd = [
            self._binary,
            "-p",
            user,
            "--system-prompt",
            system,
            "--output-format",
            "json",
            "--model",
            request.model,
        ]

        start = time.perf_counter()
        proc = None
        # A single hung call (transient rate-limit wait) must not kill a long
        # batch: retry the timeout once after a cool-down before giving up.
        for attempt in range(2):
            try:
                proc = subprocess.run(
                    cmd,
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=_TIMEOUT_S,
                    cwd=self._cwd,
                    env=self._env,
                )
                break
            except subprocess.TimeoutExpired as exc:
                if attempt == 1:
                    raise ClaudeCLIError(
                        f"claude CLI timed out twice ({_TIMEOUT_S}s each)"
                    ) from exc
                time.sleep(30.0)
        assert proc is not None
        latency_ms = (time.perf_counter() - start) * 1000.0

        if proc.returncode != 0:
            raise ClaudeCLIError(
                f"claude CLI exited {proc.returncode}: {proc.stderr.strip()[-500:]}"
            )
        text, in_tok, out_tok, session_id = parse_cli_output(proc.stdout)

        # Subscription-funded: audited as a call, charged as zero dollars.
        self.guard.charge(0, 0)

        return LLMResponse(
            text=text,
            model=request.model,
            provider=self.name,
            input_tokens=in_tok,
            output_tokens=out_tok,
            latency_ms=latency_ms,
            request_id=session_id,
            raw=None,
        )
