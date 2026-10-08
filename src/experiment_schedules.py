"""Reusable schedule and budget helpers for policy experiments."""

from dataclasses import dataclass
from itertools import cycle, islice

import numpy as np

from src.weed_policies import (
    HighDensityRemovalPolicy,
    SpreadFrontRemovalPolicy,
)


@dataclass(frozen=True)
class PolicyParameters:
    """Parameters required to construct Policies A and B."""

    a_rate: float
    b_rate: float
    max_cells: int
    boundary: float
    b_lower: float
    unit_cost: float = 200.0

    def __post_init__(self) -> None:
        if not 0 <= self.a_rate <= 1:
            raise ValueError("a_rate must be between zero and one")
        if not 0 <= self.b_rate <= 1:
            raise ValueError("b_rate must be between zero and one")
        if (
            not isinstance(self.max_cells, int)
            or isinstance(self.max_cells, bool)
            or self.max_cells <= 0
        ):
            raise ValueError("max_cells must be a positive integer")
        if not 0 <= self.b_lower < self.boundary:
            raise ValueError("b_lower must be below boundary")
        if self.unit_cost < 0:
            raise ValueError("unit_cost must be non-negative")

    def make_policy_a(self) -> HighDensityRemovalPolicy:
        return HighDensityRemovalPolicy(
            threshold=self.boundary,
            removal_rate=self.a_rate,
            max_cells=self.max_cells,
            unit_cost=self.unit_cost,
        )

    def make_policy_b(self) -> SpreadFrontRemovalPolicy:
        return SpreadFrontRemovalPolicy(
            lower_threshold=self.b_lower,
            upper_threshold=self.boundary,
            removal_rate=self.b_rate,
            max_cells=self.max_cells,
            unit_cost=self.unit_cost,
        )


def repeat_pattern(pattern: str, steps: int) -> tuple[str, ...]:
    """Repeat an A/B pattern to exactly ``steps`` policy calls."""

    labels = tuple(pattern.upper())
    if not labels or any(label not in {"A", "B"} for label in labels):
        raise ValueError("pattern must contain only A and B")
    if not isinstance(steps, int) or isinstance(steps, bool) or steps <= 0:
        raise ValueError("steps must be a positive integer")
    return tuple(islice(cycle(labels), steps))


def block_schedule(first: str, steps: int) -> tuple[str, ...]:
    """Create two near-equal blocks, starting with A or B."""

    first = first.upper()
    if first not in {"A", "B"}:
        raise ValueError("first must be A or B")
    if not isinstance(steps, int) or isinstance(steps, bool) or steps <= 0:
        raise ValueError("steps must be a positive integer")

    second = "B" if first == "A" else "A"
    first_count = (steps + 1) // 2
    return (first,) * first_count + (second,) * (steps - first_count)


def balanced_random_schedule(steps: int, seed: int) -> tuple[str, ...]:
    """Shuffle the same near-equal A/B counts used by block schedules."""

    schedule = np.asarray(block_schedule("A", steps), dtype="U1")
    np.random.default_rng(seed).shuffle(schedule)
    return tuple(schedule.tolist())


class ScheduledPolicy:
    """Apply independently constructed policies using a fixed schedule."""

    def __init__(self, schedule, parameters: PolicyParameters):
        self.schedule = tuple(str(label).upper() for label in schedule)
        if not self.schedule or any(
            label not in {"A", "B"} for label in self.schedule
        ):
            raise ValueError("schedule must contain only A and B")
        self.policy_a = parameters.make_policy_a()
        self.policy_b = parameters.make_policy_b()
        self.index = 0

    def reset(self) -> None:
        self.index = 0

    def __call__(self, weed_grid, valid_mask):
        if self.index >= len(self.schedule):
            raise RuntimeError("schedule contains fewer entries than simulation steps")
        label = self.schedule[self.index]
        self.index += 1
        policy = self.policy_a if label == "A" else self.policy_b
        return policy(weed_grid, valid_mask)


class BudgetLimitedPolicy:
    """Limit cumulative expenditure and scale the final treatment if needed."""

    def __init__(self, policy, budget: float):
        if not callable(policy):
            raise TypeError("policy must be callable")
        if not np.isfinite(budget) or budget < 0:
            raise ValueError("budget must be finite and non-negative")
        self.policy = policy
        self.budget = float(budget)
        self.spent = 0.0

    def reset(self) -> None:
        self.spent = 0.0
        reset = getattr(self.policy, "reset", None)
        if callable(reset):
            reset()

    def __call__(self, weed_grid, valid_mask):
        diff, proposed_cost = self.policy(weed_grid, valid_mask)
        proposed_cost = float(proposed_cost)
        remaining = self.budget - self.spent

        if remaining <= 0 or proposed_cost <= 0:
            return np.zeros_like(weed_grid, dtype=np.float32), 0.0
        if proposed_cost <= remaining:
            self.spent += proposed_cost
            return diff, proposed_cost

        scale = remaining / proposed_cost
        self.spent = self.budget
        return np.asarray(diff, dtype=np.float32) * scale, remaining


def make_scheduled_policy(
    schedule,
    parameters: PolicyParameters,
    budget: float,
) -> BudgetLimitedPolicy:
    """Construct a fresh scheduled policy under a common budget."""

    return BudgetLimitedPolicy(
        ScheduledPolicy(schedule, parameters),
        budget=budget,
    )


def standard_schedules(steps: int) -> dict[str, tuple[str, ...]]:
    """Return the core single, periodic and block control schedules."""

    return {
        "A only": repeat_pattern("A", steps),
        "B only": repeat_pattern("B", steps),
        "AB": repeat_pattern("AB", steps),
        "BA": repeat_pattern("BA", steps),
        "A block B": block_schedule("A", steps),
        "B block A": block_schedule("B", steps),
    }


def budget_exhaustion_step(cost_history, budget: float) -> int | None:
    """Return the first step at which a budget is exhausted."""

    matches = np.flatnonzero(np.asarray(cost_history) >= budget - 1e-2)
    return int(matches[0]) if matches.size else None
