"""Removal policies used by weed simulation experiments."""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class HighDensityRemovalPolicy:
    """Remove weeds from cells with the highest weed index."""

    # Minimum weed index required for a cell to be treated.
    threshold: float = 0.7

    # Proportion of the current weed index removed from a selected cell.
    removal_rate: float = 0.2

    # Maximum number of cells treated during one simulation step.
    max_cells: int = 100

    # Cost charged for one unit of removed weed index.
    unit_cost: float = 200.0

    def __post_init__(self):
        # The threshold cannot be negative.
        if self.threshold < 0:
            raise ValueError(
                "threshold must be non-negative"
            )

        # The removal rate represents a proportion from zero to one.
        if not 0 <= self.removal_rate <= 1:
            raise ValueError(
                "removal_rate must be between zero and one"
            )

        # At least one cell must be available for treatment.
        if (
            not isinstance(self.max_cells, int)
            or isinstance(self.max_cells, bool)
            or self.max_cells <= 0
        ):
            raise ValueError(
                "max_cells must be a positive integer"
            )

        # A negative treatment cost is not meaningful.
        if self.unit_cost < 0:
            raise ValueError(
                "unit_cost must be non-negative"
            )

    def __call__(
        self,
        weed_grid: np.ndarray,
        valid_mask: np.ndarray,
    ) -> tuple[np.ndarray, float]:
        """Return the removal grid and treatment cost."""

        # Both arrays must describe the same simulation grid.
        if weed_grid.shape != valid_mask.shape:
            raise ValueError(
                "weed_grid and valid_mask must have the same shape"
            )

        # Create an output grid containing no removal by default.
        removal = np.zeros_like(
            weed_grid,
            dtype=np.float32,
        )

        # Select valid cells whose weed index reaches the threshold.
        candidate_mask = (
            valid_mask
            & np.isfinite(weed_grid)
            & (weed_grid >= self.threshold)
        )

        # Convert candidate positions into one-dimensional indices.
        candidate_indices = np.flatnonzero(
            candidate_mask
        )

        # No treatment is required if there are no candidates.
        if candidate_indices.size == 0:
            return removal, 0.0

        # Read the weed indices of all candidate cells.
        flat_weed_grid = weed_grid.ravel()

        candidate_values = flat_weed_grid[
            candidate_indices
        ]

        # Sort candidates from the highest weed index to the lowest.
        ranked_positions = np.argsort(
            -candidate_values,
            kind="stable",
        )

        # Treat no more than max_cells during this step.
        selected_positions = ranked_positions[
            : self.max_cells
        ]

        selected_indices = candidate_indices[
            selected_positions
        ]

        # Remove the configured proportion from each selected cell.
        flat_removal = removal.ravel()

        flat_removal[selected_indices] = (
            flat_weed_grid[selected_indices]
            * self.removal_rate
        )

        # Calculate the cost from the amount actually removed.
        cost = float(
            np.sum(flat_removal)
            * self.unit_cost
        )

        return removal, cost