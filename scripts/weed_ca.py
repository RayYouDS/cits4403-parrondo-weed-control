import numpy as np
from src.weed_simulation_tools import *
import matplotlib.pyplot as plt
from collections.abc import Callable
from scipy.ndimage import convolve


class WeedCA:
    def __init__(
        self,
        gdf,
        weed_grid,
        valid_mask,
        transform=None,
        crs=None,
        cell_size=100,
        pressure_coef=0.05,
        w_min=0.05,
        w_max=0.1,
        growth_rate=0.03,
        carrying_capacity=1.0,
        diffusion_rate=0.1,
    ):
        # -------------------------
        # Spatial data
        # -------------------------
        self.gdf = gdf.copy()  # save a copy of original gdf
        self.weed_grid = weed_grid.astype(np.float32)
        self.valid_mask = valid_mask

        self.transform = transform
        self.crs = crs
        self.cell_size = cell_size

        # -------------------------
        # Initialization parameters
        # -------------------------
        self.pressure_coef = pressure_coef
        self.w_min = w_min
        self.w_max = w_max

        # -------------------------
        # Model parameters
        # -------------------------
        self.growth_rate = growth_rate
        self.carrying_capacity = carrying_capacity
        self.diffusion_rate = diffusion_rate

        # -------------------------
        # Policy List
        # -------------------------
        self.policy: Callable | None = None

        # -------------------------
        # Simulation state
        # -------------------------
        self.step_counter = 0
        self.total_cost = 0

    @classmethod
    def polygon_to_weedca(
        cls,
        gdf,
        pressure_coef,
        cell_size,
        w_min=0.05,
        w_max=1.0,
        crs="EPSG:7850",
        growth_rate=0.03,
        carrying_capacity=1.0,
        diffusion_rate=0.1,
    ):
        # 1. Calculate initial weed index
        gdf = gdf.copy()

        gdf["weed_index"] = weed_index_initialize(
            density=gdf["population_density_km2"],
            pressure_coef=pressure_coef,
            w_min=w_min,
            w_max=w_max,
        )

        # 2. Convert polygons to NumPy grid
        weed_grid, valid_mask, transform = polygon_to_grid(
            gdf, cell_size=cell_size, crs=crs
        )

        # 3. Create WeedCA instance
        return cls(
            gdf=gdf,
            weed_grid=weed_grid,
            valid_mask=valid_mask,
            transform=transform,
            crs=crs,
            cell_size=cell_size,
            pressure_coef=pressure_coef,
            w_min=w_min,
            w_max=w_max,
            growth_rate=growth_rate,
            carrying_capacity=carrying_capacity,
            diffusion_rate=diffusion_rate,
        )

    def register_policy(self, policy: Callable):
        if not callable(policy):
            raise TypeError(
                f"Policy must be callable, " f"while {type(policy)} was given"
            )

        self.policy = policy

    def reset(self):
        # reset grid to initial status according to saved parameters
        gdf = self.gdf.copy()

        # reset the weed index
        gdf["weed_index"] = weed_index_initialize(
            density=gdf["population_density_km2"],
            pressure_coef=self.pressure_coef,
            w_min=self.w_min,
            w_max=self.w_max,
        )

        # re-calculate the initial grid and mask
        weed_grid, valid_mask, transform = polygon_to_grid(
            gdf, cell_size=self.cell_size, crs=self.crs
        )

        # update grid to new state

        self.weed_grid = weed_grid
        self.valid_mask = valid_mask
        self.transform = transform

        self.step_counter = 0
        self.total_cost = 0

    def _growth(self):
        # logistic growth model
        W = self.weed_grid

        growth = self.growth_rate * W * (1 - W / self.carrying_capacity)

        new_W = W + growth

        new_W = np.clip(new_W, 0, self.carrying_capacity)

        new_W[~self.valid_mask] = np.nan

        self.weed_grid = new_W

    def _diffusion(self):
        W = self.weed_grid
        valid = self.valid_mask

        diffusion = np.zeros_like(
            W,
            dtype=np.float32,
        )

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

        height, width = W.shape

        padded_W = np.pad(
            W,
            pad_width=1,
            mode="constant",
            constant_values=np.nan,
        )

        padded_valid = np.pad(
            valid,
            pad_width=1,
            mode="constant",
            constant_values=False,
        )

        for dr, dc in directions:
            row_start = 1 + dr
            col_start = 1 + dc

            neighbor = padded_W[
                row_start : row_start + height,
                col_start : col_start + width,
            ]

            neighbor_valid = padded_valid[
                row_start : row_start + height,
                col_start : col_start + width,
            ]

            difference = np.maximum(
                neighbor - W,
                0,
            )

            difference[~neighbor_valid] = 0
            difference[~valid] = 0

            diffusion += difference

        diffusion *= self.diffusion_rate

        new_W = W + diffusion

        new_W = np.clip(
            new_W,
            0,
            self.carrying_capacity,
        )

        new_W[~valid] = np.nan

        self.weed_grid = new_W

    def _removal(self):
        if self.policy is None:
            return None

        W = self.weed_grid
        valid_mask = self.valid_mask

        policy_grid = W.copy()
        policy_mask = valid_mask.copy()

        diff, cost = self.policy(
            policy_grid,
            policy_mask,
        )

        if isinstance(cost, (bool, np.bool_)) or not isinstance(
            cost, (int, float, np.integer, np.floating)
        ):
            raise TypeError(f"Cost must be numeric, while {type(cost)} was given")

        cost = float(cost)

        if not np.isfinite(cost):
            raise ValueError(f"Cost must be finite, while {cost} was given")

        if cost < 0:
            raise ValueError(f"Cost must be non-negative, while {cost} was given")

        try:
            diff = np.asarray(diff, dtype=np.float32)
        except (TypeError, ValueError) as exc:
            raise TypeError("Policy diff must be a numeric array") from exc

        if diff.shape != W.shape:
            raise ValueError("Policy diff must have the same shape as weed_grid")

        if not np.all(np.isfinite(diff[valid_mask])):
            raise ValueError("Policy diff must contain finite values in valid cells")

        if np.any(diff[valid_mask] < 0):
            raise ValueError("Policy diff must be non-negative")

        diff = diff.copy()
        diff[~valid_mask] = 0

        if np.any(diff[valid_mask] > W[valid_mask]):
            raise ValueError("Policy diff cannot exceed the current weed index")

        new_W = W - diff
        new_W = np.clip(new_W, 0, self.carrying_capacity)
        new_W[~valid_mask] = np.nan

        self.weed_grid = new_W
        self.total_cost += cost

    def _check_mode(self, modes):
        for mode in modes:
            if mode not in ("growth", "diffusion", "removal"):
                raise ValueError(
                    f"Simulation mode can only be a subset of"
                    f' "growth", "diffusion", "removal", while {mode} was given'
                )

    def step(self, modes=("growth", "diffusion", "removal")):

        self._check_mode(modes)

        if "growth" in modes:
            self._growth()

        if "diffusion" in modes:
            self._diffusion()

        if "removal" in modes:
            self._removal()

        self.step_counter += 1

    def show_grid(self, figsize=(4, 6)):
        cmap = plt.cm.YlGn.copy()
        cmap.set_bad("lightgray")

        plt.figure(figsize=figsize)

        plt.imshow(self.weed_grid, cmap=cmap, vmin=0, vmax=self.carrying_capacity)

        plt.colorbar(label="Weed Index")
        plt.title(
            f"Weed Index - Step {self.step_counter} | "
            f"Total Cost: ${self.total_cost:,.2f}"
        )
        plt.axis("off")

        plt.show()

    def simulate(self, steps, modes=["growth", "diffusion", "removal"]):

        self._check_mode(modes)

        self.reset()

        height, width = self.weed_grid.shape

        history = np.empty((steps + 1, height, width), dtype=np.float32)

        cost_history = np.empty(steps + 1, dtype=np.float32)

        # Step 0
        history[0] = self.weed_grid
        cost_history[0] = self.total_cost

        # Step 1 ... steps
        for t in range(1, steps + 1):

            self.step(modes=modes)

            history[t] = self.weed_grid
            cost_history[t] = self.total_cost

        return history, cost_history

    def animate(
        self,
        frames,
        fps,
        modes=["growth", "diffusion", "removal"],
        figsize=(4, 6),
        save_path=None,
    ):

        self._check_mode(modes)

        history, cost_history = self.simulate(frames, modes)

        from matplotlib.animation import FuncAnimation
        from IPython.display import HTML

        fig, ax = plt.subplots(figsize=figsize)

        cmap = plt.cm.YlGn.copy()
        cmap.set_bad("lightgray")

        image = ax.imshow(history[0], cmap=cmap, vmin=0, vmax=self.carrying_capacity)

        ax.axis("off")

        title = ax.set_title(
            f"Weed Index - Step 0 | " f"Total Cost: ${cost_history[0]:,.2f}"
        )

        def update(frame):

            image.set_data(history[frame])

            title.set_text(
                f"Weed Index - Step {frame} | "
                f"Total Cost: ${cost_history[frame]:,.2f}"
            )

            return image, title

        anim = FuncAnimation(
            fig, update, frames=len(history), interval=1000 / fps, blit=False
        )

        # Save GIF if requested
        if save_path is not None:
            anim.save(save_path, writer="pillow", fps=fps)

        plt.close(fig)

        return HTML(anim.to_jshtml())
