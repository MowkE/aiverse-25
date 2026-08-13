# Clean Subscription Pathway — Isolation Test Report (2026-08-13)

Question (per project direction): can headless Claude Code (`claude -p`, subscription-funded) be
isolated well enough to serve for calibration runs — and possibly a legitimate Haiku Study 2?
Installed CLI: 2.1.229. Model: claude-haiku-4-5. All tests headless, neutral cwd, API key
stripped from env.

## Test matrix (probe: "quote your system prompt's first sentence; count your tools")

| Config | Flags | Input tokens | System prompt seen by model | Tools |
|---|---|---|---|---|
| A (shakedown) | `--system-prompt` only | 24,304 | Harness's ("You are a Claude agent…"); ours appended later | 28 |
| B | A + `--exclude-dynamic-system-prompt-sections` | 24,304 | **Ours first**, harness bulk still present | 12 |
| C (max isolation) | B + `--no-session-persistence` + `--setting-sources ""` + `--strict-mcp-config` + `--disallowedTools "*"` | **696** | Ours (see caveats) | 0 named |

## Behavioral verification under config C

- Adversarial extraction probe → model refused and described our system prompt as "initial
  preamble", raising concern that the substituted prompt might lack full system-role authority.
- **Decisive test — real society prompts (3 calls): 3/3 valid schema-conforming JSON**, correct
  role adoption ("Agent Kestrel"), no refusals, no meta-commentary. Input 892 tokens each
  (~380 ours + ~510 residual wrapper). The earlier refusal was an artifact of the extraction
  probe, which models legitimately resist.

## Checklist verdicts

| Requirement | Verdict |
|---|---|
| Default coding prompt replaced | PASS (config B/C: our text is the prompt's first sentence) |
| No CLAUDE.md / memories / skills / hooks / repo context | PASS via `--setting-sources ""` + neutral cwd (token count consistent with none present) |
| Independent calls (no cross-call state) | PASS (`--no-session-persistence`; fresh subprocess per call) |
| Token counts ≈ experimental prompt only | PARTIAL — ~510-token residual wrapper of uninspectable content remains (vs ~24,000 before) |
| Model version recorded and stable | PARTIAL — `claude-haiku-4-5` recorded per call; subscription routing does not pin point-releases; no temperature/sampling control exists in the CLI |

## Conclusions

1. **Calibration use: APPROVED.** The calibration study (docs/CALIBRATION_PROTOCOL.md) selects
   economy parameters from participation rates; a stable ~510-token wrapper shared by every call
   in every condition cannot plausibly confound a within-grid comparison. Provider updated to use
   the config-C flag set.
2. **Confirmatory use: OPEN QUESTION for professor review.** The residual wrapper is small and
   condition-constant but unauditable, and sampling parameters are uncontrollable. Whether that
   meets a preregistration's disclosure bar is exactly professor question #6 in the review packet.
   Until answered, the paid API path remains the provider of record for confirmatory data (D14).

Raw probe transcripts: scratchpad isotest (session artifacts); flag set encoded in
`src/universe25/llm/providers/claude_cli.py`.
