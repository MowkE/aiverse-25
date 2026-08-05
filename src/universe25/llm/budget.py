"""Budget guard: no real-provider call may run without explicit confirmation.

The CLI arms the guard with `--confirm-budget <dollars>` after showing the
estimate; real providers hold the guard and re-check it before every HTTP
request and after every response. Mock runs never construct a guard.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .pricing import cost_usd


class BudgetError(RuntimeError):
    pass


class BudgetNotConfirmedError(BudgetError):
    pass


class BudgetExceededError(BudgetError):
    pass


@dataclass
class BudgetGuard:
    model: str
    confirmed_budget_usd: float | None = None
    spent_usd: float = field(default=0.0, init=False)
    calls_made: int = field(default=0, init=False)

    def arm(self, confirmed_budget_usd: float) -> None:
        if confirmed_budget_usd <= 0:
            raise BudgetNotConfirmedError("confirmed budget must be positive")
        self.confirmed_budget_usd = confirmed_budget_usd

    @property
    def armed(self) -> bool:
        return self.confirmed_budget_usd is not None and self.confirmed_budget_usd > 0

    def authorize_estimate(self, estimated_cost_usd: float) -> None:
        """Abort before a batch starts if the estimate exceeds the confirmation."""
        if not self.armed:
            raise BudgetNotConfirmedError(
                "real-provider execution requires --confirm-budget <dollars>"
            )
        assert self.confirmed_budget_usd is not None
        if estimated_cost_usd > self.confirmed_budget_usd:
            raise BudgetExceededError(
                f"estimated cost ${estimated_cost_usd:.2f} exceeds confirmed "
                f"budget ${self.confirmed_budget_usd:.2f}; aborting before any call"
            )

    def precall(self) -> None:
        if not self.armed:
            raise BudgetNotConfirmedError(
                "budget guard is not armed; refusing to make a paid API call"
            )
        assert self.confirmed_budget_usd is not None
        if self.spent_usd >= self.confirmed_budget_usd:
            raise BudgetExceededError(
                f"accumulated spend ${self.spent_usd:.4f} reached confirmed "
                f"budget ${self.confirmed_budget_usd:.2f}; halting"
            )

    def charge(self, input_tokens: int, output_tokens: int) -> float:
        cost = cost_usd(self.model, input_tokens, output_tokens)
        self.spent_usd += cost
        self.calls_made += 1
        return cost
