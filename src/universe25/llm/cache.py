"""Append-only JSONL call cache with resume support (docs/LLM_DESIGN.md §8).

Every resolved call is persisted keyed by (run_id, round, agent_id, phase,
template_version, model, seed). On resume the orchestrator replays the run
from round 0; cache hits short-circuit the provider and are marked. A key hit
whose stored prompt hash differs from the freshly rendered prompt raises:
template/config drift under an unchanged version string is a bug, not a
resume.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path


class CacheDriftError(RuntimeError):
    pass


def prompt_hash(system: str, user: str) -> str:
    return hashlib.sha256((system + "\x1e" + user).encode("utf-8")).hexdigest()


def call_key(
    run_id: str, round_index: int, agent_id: int, phase: str,
    template_version: str, model: str, seed: int,
) -> str:
    return f"{run_id}|{round_index}|{agent_id}|{phase}|{template_version}|{model}|{seed}"


@dataclass(frozen=True)
class CachedCall:
    key: str
    prompt_sha256: str
    response_text: str
    parsed: dict | None
    valid: bool
    retries: int
    invalid_after_retries: bool
    contamination_flag: bool
    input_tokens: int
    output_tokens: int
    latency_ms: float
    provider: str
    model: str
    request_id: str | None


class CallCache:
    """One JSONL file per run, loaded eagerly, appended atomically per call."""

    def __init__(self, cache_dir: str | Path, run_id: str):
        self.path = Path(cache_dir) / f"{run_id}.jsonl"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._records: dict[str, CachedCall] = {}
        self.hits = 0
        self.misses = 0
        if self.path.exists():
            with open(self.path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    rec = CachedCall(**json.loads(line))
                    self._records[rec.key] = rec

    def __len__(self) -> int:
        return len(self._records)

    def lookup(self, key: str, expected_prompt_sha256: str) -> CachedCall | None:
        rec = self._records.get(key)
        if rec is None:
            self.misses += 1
            return None
        if rec.prompt_sha256 != expected_prompt_sha256:
            raise CacheDriftError(
                f"cache key {key} exists but the rendered prompt differs from the cached "
                "one; bump the template version or clear the cache before re-running"
            )
        self.hits += 1
        return rec

    def store(self, rec: CachedCall) -> None:
        self._records[rec.key] = rec
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(rec), sort_keys=True) + "\n")
            f.flush()
