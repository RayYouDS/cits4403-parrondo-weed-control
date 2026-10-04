"""Helpers for running and evaluating weed simulations."""

from collections.abc import Callable
from dataclasses import dataclass

import geopandas as gpd
import numpy as np

from scripts.weed_ca import WeedCA


Policy = Callable[
    [np.ndarray, np.ndarray],
    tuple[np.ndarray, float | np.number],
]

@dataclass(frozen=True)
class ExperimentConfig:
    """Parameters shared by simulation experiments."""

    # Controls how strongly population density reduces the initial weed index.
    pressure_coef: float = 0.000783

    # Width and height of each square grid cell in metres.
    cell_size: float = 1000.0

    # Minimum weed index assigned during population-based initialisation.
    w_min: float = 0.05

    # Maximum weed index assigned during population-based initialisation.
    w_max: float = 1.0

    # Logistic weed-growth rate applied during each simulation step.
    growth_rate: float = 0.02

    # Rate of weed spread from higher-density neighbouring cells.
    diffusion_rate: float = 0.01

    # Maximum weed index allowed in each grid cell.
    carrying_capacity: float = 1.0

    # Number of abstract update steps performed by the simulation.
    steps: int = 100

    # Weed-index value used to classify a cell as high density.
    high_density_threshold: float = 0.7

    # Projected coordinate system used to create the simulation grid.
    crs: str = "EPSG:7850"

    def __post_init__(self):
        if self.pressure_coef < 0:
            raise ValueError(
                "pressure_coef must be non-negative"
            )

        if self.cell_size <= 0:
            raise ValueError(
                "cell_size must be greater than zero"
            )

        if self.w_min < 0:
            raise ValueError(
                "w_min must be non-negative"
            )

        if self.w_max < self.w_min:
            raise ValueError(
                "w_max must be greater than or equal to w_min"
            )

        if self.growth_rate < 0:
            raise ValueError(
                "growth_rate must be non-negative"
            )

        if self.diffusion_rate < 0:
            raise ValueError(
                "diffusion_rate must be non-negative"
            )

        if self.carrying_capacity <= 0:
            raise ValueError(
                "carrying_capacity must be greater than zero"
            )

        if self.w_max > self.carrying_capacity:
            raise ValueError(
                "w_max cannot exceed carrying_capacity"
            )

        if (
            not isinstance(self.steps, int)
            or isinstance(self.steps, bool)
            or self.steps <= 0
        ):
            raise ValueError(
                "steps must be a positive integer"
            )

        if not (
            0
            <= self.high_density_threshold
            <= self.carrying_capacity
        ):
            raise ValueError(
                "high_density_threshold must be between "
                "zero and carrying_capacity"
            )

        if not isinstance(self.crs, str) or not self.crs:
            raise ValueError(
                "crs must be a non-empty string"
            )


@dataclass(frozen=True)
class ExperimentResult:
    """Results and metrics from one simulation experiment."""

    name: str
    config: ExperimentConfig
    modes: tuple[str, ...]

    history: np.ndarray
    cost_history: np.ndarray

    mean_weed: np.ndarray
    high_density_cells: np.ndarray

    initial_mean: float
    final_mean: float
    relative_change: float

    valid_cell_count: int
    grid_shape: tuple[int, int]

    @property
    def final_cost(self) -> float:
        return float(self.cost_history[-1])

    @property
    def final_high_density_cells(self) -> int:
        return int(self.high_density_cells[-1])

    def summary(self) -> dict:
        """Return a compact experiment summary."""

        return {
            "name": self.name,
            "steps": self.config.steps,
            "grid_height": self.grid_shape[0],
            "grid_width": self.grid_shape[1],
            "valid_cells": self.valid_cell_count,
            "initial_mean_weed": self.initial_mean,
            "final_mean_weed": self.final_mean,
            "relative_change": self.relative_change,
            "final_high_density_cells": (
                self.final_high_density_cells
            ),
            "final_cost": self.final_cost,
        }


def _validate_input_gdf(
    gdf: gpd.GeoDataFrame,
) -> None:
    """Validate the spatial input required by WeedCA."""

    if not isinstance(gdf, gpd.GeoDataFrame):
        raise TypeError(
            "gdf must be a GeoDataFrame"
        )

    if gdf.empty:
        raise ValueError(
            "gdf must contain at least one row"
        )

    required_columns = {
        "geometry",
        "population_density_km2",
    }

    missing_columns = (
        required_columns - set(gdf.columns)
    )

    if missing_columns:
        raise ValueError(
            "gdf is missing required columns: "
            f"{sorted(missing_columns)}"
        )

    population_density = (
        gdf["population_density_km2"]
        .to_numpy(dtype=float)
    )

    if not np.all(
        np.isfinite(population_density)
    ):
        raise ValueError(
            "population_density_km2 must contain "
            "only finite values"
        )

    if np.any(population_density < 0):
        raise ValueError(
            "population_density_km2 cannot "
            "contain negative values"
        )

    if gdf.geometry.isna().any():
        raise ValueError(
            "gdf cannot contain missing geometries"
        )

    if gdf.geometry.is_empty.any():
        raise ValueError(
            "gdf cannot contain empty geometries"
        )


def _calculate_metrics(
    history: np.ndarray,
    high_density_threshold: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Calculate the mean index and high-density cell count."""

    if history.ndim != 3:
        raise ValueError(
            "history must be a three-dimensional array"
        )

    # NaN cells are outside the study area.
    mean_weed = np.nanmean(
        history,
        axis=(1, 2),
    )

    high_density_cells = np.sum(
        history >= high_density_threshold,
        axis=(1, 2),
    )

    return mean_weed, high_density_cells


def run_experiment(
    name: str,
    gdf: gpd.GeoDataFrame,
    config: ExperimentConfig,
    policy: Policy | None = None,
) -> ExperimentResult:
    """Run one simulation and calculate its metrics."""

    if not isinstance(name, str) or not name.strip():
        raise ValueError(
            "name must be a non-empty string"
        )

    if not isinstance(
        config,
        ExperimentConfig,
    ):
        raise TypeError(
            "config must be an ExperimentConfig"
        )

    _validate_input_gdf(gdf)

    weedca = WeedCA.polygon_to_weedca(
        gdf,
        pressure_coef=config.pressure_coef,
        cell_size=config.cell_size,
        w_min=config.w_min,
        w_max=config.w_max,
        crs=config.crs,
        growth_rate=config.growth_rate,
        carrying_capacity=(
            config.carrying_capacity
        ),
        diffusion_rate=config.diffusion_rate,
    )

    if policy is None:
        modes = (
            "growth",
            "diffusion",
        )
    else:
        if not callable(policy):
            raise TypeError(
                "policy must be callable"
            )

        weedca.register_policy(policy)

        modes = (
            "growth",
            "diffusion",
            "removal",
        )

    history, cost_history = weedca.simulate(
        steps=config.steps,
        modes=modes,
    )

    expected_length = config.steps + 1

    if history.shape[0] != expected_length:
        raise RuntimeError(
            "Unexpected simulation-history length"
        )

    if cost_history.shape[0] != expected_length:
        raise RuntimeError(
            "Unexpected cost-history length"
        )

    if not np.all(np.isfinite(cost_history)):
        raise RuntimeError(
            "Simulation produced non-finite costs"
        )

    if np.any(cost_history < 0):
        raise RuntimeError(
            "Simulation produced negative costs"
        )

    if np.any(np.diff(cost_history) < 0):
        raise RuntimeError(
            "Cumulative cost decreased"
        )

    mean_weed, high_density_cells = (
        _calculate_metrics(
            history,
            config.high_density_threshold,
        )
    )

    if not np.all(np.isfinite(mean_weed)):
        raise RuntimeError(
            "Simulation produced invalid mean values"
        )

    initial_mean = float(mean_weed[0])
    final_mean = float(mean_weed[-1])

    if np.isclose(initial_mean, 0.0):
        relative_change = float("nan")
    else:
        relative_change = (
            final_mean - initial_mean
        ) / initial_mean

    return ExperimentResult(
        name=name.strip(),
        config=config,
        modes=modes,
        history=history,
        cost_history=cost_history,
        mean_weed=mean_weed,
        high_density_cells=(
            high_density_cells
        ),
        initial_mean=initial_mean,
        final_mean=final_mean,
        relative_change=float(
            relative_change
        ),
        valid_cell_count=int(
            weedca.valid_mask.sum()
        ),
        grid_shape=weedca.weed_grid.shape,
    )