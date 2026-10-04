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


@dataclass(frozen=True)
class SpreadFrontRemovalPolicy:
    """Remove weeds from medium-density cells that may drive spread."""

    # Minimum weed index required for a cell to be considered.
    lower_threshold: float = 0.3

    # Exclusive upper limit for candidate cells.
    upper_threshold: float = 0.7

    # Proportion of the current weed index removed from a selected cell.
    removal_rate: float = 0.2

    # Maximum number of cells treated during one simulation step.
    max_cells: int = 100

    # Cost charged for one unit of removed weed index.
    unit_cost: float = 200.0

    def __post_init__(self):
        # The lower threshold cannot be negative.
        if self.lower_threshold < 0:
            raise ValueError(
                "lower_threshold must be non-negative"
            )

        # The upper threshold must exceed the lower threshold.
        if self.upper_threshold <= self.lower_threshold:
            raise ValueError(
                "upper_threshold must be greater than "
                "lower_threshold"
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

        # No weed is removed unless a cell is selected below.
        removal = np.zeros_like(
            weed_grid,
            dtype=np.float32,
        )

        # Accumulate the outward spread score for every cell.
        spread_score = np.zeros_like(
            weed_grid,
            dtype=np.float32,
        )

        # Include horizontal, vertical and diagonal neighbours.
        directions = [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        ]

        height, width = weed_grid.shape

        # Padding prevents one edge of the grid from wrapping to another.
        padded_weed_grid = np.pad(
            weed_grid,
            pad_width=1,
            mode="constant",
            constant_values=np.nan,
        )

        padded_valid_mask = np.pad(
            valid_mask,
            pad_width=1,
            mode="constant",
            constant_values=False,
        )

        for row_offset, column_offset in directions:
            row_start = 1 + row_offset
            column_start = 1 + column_offset

            # Extract the neighbour corresponding to this direction.
            neighbour = padded_weed_grid[
                row_start : row_start + height,
                column_start : column_start + width,
            ]

            neighbour_valid = padded_valid_mask[
                row_start : row_start + height,
                column_start : column_start + width,
            ]

            # A cell receives a positive score when it is higher
            # than its neighbouring cell.
            difference = np.maximum(
                weed_grid - neighbour,
                0,
            )

            # Invalid neighbours must not affect the score.
            difference[~neighbour_valid] = 0

            # Invalid centre cells must not receive a score.
            difference[~valid_mask] = 0

            spread_score += difference

        # Candidate cells must be valid and within the medium range.
        candidate_mask = (
            valid_mask
            & np.isfinite(weed_grid)
            & (weed_grid >= self.lower_threshold)
            & (weed_grid < self.upper_threshold)
            & (spread_score > 0)
        )

        # Convert candidate positions into one-dimensional indices.
        candidate_indices = np.flatnonzero(
            candidate_mask
        )

        # Return zero removal if no spread-front cells are available.
        if candidate_indices.size == 0:
            return removal, 0.0

        flat_weed_grid = weed_grid.ravel()
        flat_spread_score = spread_score.ravel()

        # Read the scores of candidate cells.
        candidate_scores = flat_spread_score[
            candidate_indices
        ]

        # Rank cells from the highest spread score to the lowest.
        ranked_positions = np.argsort(
            -candidate_scores,
            kind="stable",
        )

        # Treat no more than max_cells during this step.
        selected_positions = ranked_positions[
            : self.max_cells
        ]

        selected_indices = candidate_indices[
            selected_positions
        ]

        # Remove the configured proportion from selected cells.
        flat_removal = removal.ravel()

        flat_removal[selected_indices] = (
            flat_weed_grid[selected_indices]
            * self.removal_rate
        )

        # Calculate cost from the amount actually removed.
        cost = float(
            np.sum(flat_removal)
            * self.unit_cost
        )

        return removal, cost