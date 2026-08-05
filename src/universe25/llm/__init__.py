"""Study 2 LLM-agent confirmation layer (docs/LLM_DESIGN.md).

Code, not the model, owns environment state, treatments, scoring, logging, and
termination. All tests and default execution paths use the deterministic
MockProvider; real providers are gated behind an armed BudgetGuard.
"""
